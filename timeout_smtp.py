# timeout_smtp.py
import os
import socket
import time
import logging
import threading
import signal
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [timeout-smtp] %(message)s",
)
log = logging.getLogger("timeout-smtp")

# CONFIG (mirrors busy_smtp.py style)
BIND_IP = os.getenv("BIND_IP", "127.0.0.1")
PORT = int(os.getenv("PORT", "2525"))
BANNER_HOST = os.getenv("BANNER_HOST", "sleepy.mx.local")  # used only in after_banner mode
SLEEP_SECS = int(os.getenv("SLEEP_SECS", "600"))           # how long to stall per connection
MODE = os.getenv("MODE", "no_banner").lower()
# MODE options:
#   no_banner    -> accept TCP, send nothing, just sleep (client times out waiting for banner)
#   after_banner -> send 220 banner once, then sleep (client times out on next command)
#   partial_line -> send "220 " only (no CRLF), then sleep (client waits for full line)

def handle_client(conn: socket.socket, addr):
    try:
        log.info("accepted peer=%s mode=%s", addr, MODE)
        if MODE == "no_banner":
            time.sleep(SLEEP_SECS)

        elif MODE == "after_banner":
            banner = f"220 {BANNER_HOST} ESMTP Service Ready\r\n".encode()
            conn.sendall(banner)
            log.debug("sent banner; sleeping for %ss", SLEEP_SECS)
            time.sleep(SLEEP_SECS)

        elif MODE == "partial_line":
            conn.sendall(b"220 ")  # incomplete response (no hostname, no CRLF)
            log.debug("sent partial banner; sleeping for %ss", SLEEP_SECS)
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

def serve_forever():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # On macOS you can also set a small accept backlog to mimic busy server if desired
        srv.bind((BIND_IP, PORT))
        srv.listen(64)
        log.info("Started on %s:%s mode=%s", BIND_IP, PORT, MODE)

        # Graceful shutdown via signal
        stop = {"flag": False}

        def _stop(*_):
            stop["flag"] = True
            log.info("shutdown requested…")

        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

        srv.settimeout(1.0)
        while not stop["flag"]:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            # Per-connection thread so multiple senders can hang simultaneously
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

        log.info("server exiting")

if __name__ == "__main__":
    try:
        serve_forever()
    except Exception as e:
        log.exception("fatal: %s", e)
        sys.exit(1)
