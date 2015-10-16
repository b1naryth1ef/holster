import mandrill, logging

from flask import current_app

log = logging.getLogger(__name__)
mandrill_client = mandrill.Mandrill(current_app.config.get("EMAIL_MANDRILL_KEY"))

class Email(object):
    def __init__(self):
        self.from_addr = "noreply@csgofort.com"
        self.from_name = "CSGO Fort"
        self.to_addrs = []
        self.subject = ""
        self.body = ""

    def send(self):
        payload = {
            "from_email": self.from_addr,
            "from_name": self.from_name,
            "html": self.body,
            "subject": self.subject,
            "to": map(lambda i: {
                "email": i, "type": "to"
            }, self.to_addrs),
        }

        if current_app.config.get("EMAIL_DISABLE"):
            log.debug("Would send email %s" % payload)
            return

        log.info("Sending email to %s" % self.to_addrs)
        mandrill_client.messages.send(message=payload)

