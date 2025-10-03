# busy_smtp.py
import os
import time
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [busy-smtp] %(message)s",
)
log = logging.getLogger("busy-smtp")

OUTLOOK_451 = (
    "451 4.7.500 Server busy. Please try again later from [2.56.250.16]. (S77714) "
    "[DB1PEPF000509EF.eurprd03.prod.outlook.com 2025-09-06T02:41:15.886Z 08DDE524AD2CBD69]"
)

class BusyHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Log context so you can see what’s happening
        log.info(
            "RCPT: helo=%s from=%s to=%s peer=%s",
            getattr(session, "host_name", None),
            envelope.mail_from,
            address,
            getattr(session, "peer", None),
        )
        return OUTLOOK_451  # deny at RCPT with 451

class BrandedController(Controller):
    """Just to customize the banner/ident; DO NOT override EHLO/HELO."""
    def __init__(self, handler, bind_ip, port, helo_host, ident="ESMTP BusySim"):
        super().__init__(handler, hostname=bind_ip, port=port)
        self._helo_host = helo_host
        self._ident = ident

    def factory(self):
        # Pass ident (banner) and the hostname used in 250- lines
        return SMTP(self.handler, hostname=self._helo_host, ident=self._ident)

def start_busy_smtp(bind_ip="127.0.0.1", port=2526, helo_host="busy.mx.local"):
    ctrl = BrandedController(BusyHandler(), bind_ip, port, helo_host)
    ctrl.start()
    log.info("Started on %s:%s banner=%s", bind_ip, port, helo_host)
    return ctrl

if __name__ == "__main__":
    ctrl = start_busy_smtp(
        bind_ip=os.getenv("BIND_IP", "127.0.0.1"),
        port=int(os.getenv("PORT", "25")),
        helo_host=os.getenv("BANNER_HOST", "busy.mx.local"),
    )
    try:
        while True:
            time.sleep(3600)
    finally:
        ctrl.stop()