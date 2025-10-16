# tcp_timeout_smtp.py
import os
import socket
import time
import logging
import threading
import signal
import sys

# ---- Match busy_smtp.py logging style ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [timeout-smtp] %(message)s",
)
log = logging.getLogger("timeout-smtp")

# ---- SAME CONFIG SHAPE AS busy_smtp.py ----
host_ip = "192.168.1.14"
port = "25"  # keep as string to match your busy_smtp.py, cast later

# Optional extras (with sane defaults)
# - MODE: how to stall the session
# - BANNER_HOST: hostname to use if we send a banner (after_banner mode)
# - SLEEP_SECS: how long to stall each connection
MODE = os.getenv("MODE", "no_banner").lower()
BANNER_HOST = os.getenv("BANNER_HOST", "sleepy.mx.local")
SLEEP_SECS = int(os.getenv("SLEEP_SECS", "1200"))

# MODE options:
#   no_banner    -> accept TCP, send nothing, just sleep (client times out waiting for banner)
#   after_banner -> send a 220 banner once, then sleep (client times out on next command)
#   partial_line -> send "220 " only (no CRLF), then sleep (client waits for a full line)

def handle_client(conn: socket.socket, addr):
    try:
        log.info("accepted peer=%s mode=%s", addr, MODE)

        if MODE == "no_banner":
            # Do not send anything; client should time out waiting for greeting
            time.sleep(SLEEP_SECS)

        elif MODE == "after_banner":
            banner = f"220 {BANNER_HOST} ESMTP Service Ready\r\n".encode()
            conn.sendall(banner)
            log.debug("sent banner; sleeping %ss", SLEEP_SECS)
            time.sleep(SLEEP_SECS)

        elif MODE == "partial_line":
            # Send an incomplete response (no CRLF)
            conn.sendall(b"220 ")
            log.debug("sent partial banner; sleeping %ss", SLEEP_SECS)
            time.sleep(SLEEP_SECS)

        else:
            log.warning("unknown MODE '%s', defaulting to no_banner", MODE)
            time.sleep(SLEEP_SECS)

    except Exception as e:
        log.exception("error in client handler: %s", e)
    finally:
        try:
            conn.close()
        except Exception:
            pass
        log.info("closed peer=%s", addr)

def serve_forever(bind_ip: str, bind_port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((bind_ip, bind_port))
        srv.listen(64)
        log.info("Started on %s:%s mode=%s sleep=%ss", bind_ip, bind_port, MODE, SLEEP_SECS)

        # Graceful stop flags + signal handlers
        stop = {"flag": False}
        def _stop(*_):
            stop["flag"] = True
            log.info("shutdown requested…")

        # Note: SIGTERM may not be delivered on Windows; Ctrl-C (SIGINT) works.
        try:
            signal.signal(signal.SIGINT, _stop)
            signal.signal(signal.SIGTERM, _stop)
        except Exception:
            pass

        srv.settimeout(1.0)
        while not stop["flag"]:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

        log.info("server exiting")

if __name__ == "__main__":
    # Respect your exact busy_smtp.py override pattern:
    bind_ip = os.getenv("BIND_IP", host_ip)
    bind_port = int(os.getenv("PORT", port))

    try:
        serve_forever(bind_ip, bind_port)
    except Exception as e:
        log.exception("fatal: %s", e)
        sys.exit(1)
