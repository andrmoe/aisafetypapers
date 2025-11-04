import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path


def send_email(receiver_email: str,
               subject: str,
               content: MIMEText,
               config_path: Path=Path(__file__).parent / ".env") -> None:
    conf = None  # TODO: Make this a typedDict
    with open(config_path, "r") as f:
        conf = json.loads(f.read())
    sender_email = conf["sender_email"]
    password = conf["password"]
    host = conf["host"]
    port = conf["port"]
    
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg['Subject'] = subject
    msg.attach(content)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent successfully to {receiver_email}.")
