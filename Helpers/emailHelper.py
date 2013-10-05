import smtplib
from email.mime.text import MIMEText
from Helpers import logger
import settings

class Email:
    
    def __init__(self, sender=None, recipients=None):
        self.host = settings.EMAILHOST
        self.sender = sender or settings.EMAILSENDER
        self.recipients = recipients or settings.EMAILRECIPIENTS
    
    def send(self, subject, body):
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender

        for r in self.recipients:
            msg['To'] = r
            
            try:
                s = smtplib.SMTP(self.host)
                if settings.EMAILUSERNAME and settings.EMAILPASSWORD:
                    s.login(settings.EMAILUSERNAME, settings.EMAILPASSWORD)
                s.sendmail(self.sender, r, msg.as_string())
            except:
                logger.log_to_file(msg.as_string())
        