import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path


def send_email(receiver_email: str,
               subject: str,
               content: MIMEText,
               sender_email: str | None=None,
               sender_password: str | None=None,
               host: str="smtp.gmail.com",
               config_path: Path=Path(__file__).parent / ".env") -> None:
    conf = None
    with open(config_path, "r") as f:
        conf = json.loads(f.read())
    default_sender_email = conf["sender_email"]
    default_password = conf["password"]
    
    msg = MIMEMultipart()
    if sender_email is None:
        sender_email = default_sender_email
    if sender_password is None:
        sender_password = default_password
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg['Subject'] = subject
    msg.attach(content)

    with smtplib.SMTP(host, 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent successfully to {receiver_email}.")
