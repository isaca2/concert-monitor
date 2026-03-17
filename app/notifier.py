import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

class EmailNotifier:
    def __init__(self):
        self.logger = logging.getLogger("EmailNotifier")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.recipient = os.getenv("RECIPIENT_EMAIL")

    def send_notification(self, new_concerts):
        if not self.username or not self.password:
            self.logger.warning("SMTP credentials not set. Skipping email.")
            # For testing: just log the concerts found
            for c in new_concerts:
                self.logger.info(f"Would email about: {c.title} by {c.artist.name}")
            return

        if not new_concerts:
            return

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = self.recipient
        msg['Subject'] = f"New Concerts Found! ({len(new_concerts)})"

        body = "<h2>New Concerts Detected:</h2><ul>"
        for c in new_concerts:
            body += f"<li><strong>{c.artist.name}</strong>: <a href='{c.url}'>{c.title}</a> ({c.date_str}) @ {c.venue}</li>"
        body += "</ul>"

        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            self.logger.info(f"Email sent to {self.recipient}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
