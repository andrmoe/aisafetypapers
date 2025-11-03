import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai_safety_rss import create_html
import os
import json
from datetime import datetime, UTC
import traceback


def send_email(sender_email: str,
               sender_password: str,
               receiver_email: str,
               subject: str,
               content: MIMEText) -> None:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg['Subject'] = subject
    msg.attach(content)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent successfully to {receiver_email}.")


dir = os.path.dirname(__file__)

def send_ai_safety_email() -> None:
    # Email configuration
    conf = None
    with open(f"{dir}/.env", "r") as f:
        conf = json.loads(f.read())
    sender_email = conf["sender_email"]
    receiver_emails = conf["receiver_emails"]
    maintainer_email = conf["maintainer_email"]
    password = conf["password"]

    try:
        print()
        print(f"Time: {datetime.now(tz=UTC)}")
        for receiver_email in receiver_emails:
            subject = "New Papers from AI Safety Researchers"

            email_content = create_html()
            if email_content is None:
                return
            send_email(sender_email, password, receiver_email, subject, 
                       MIMEText(email_content, 'html'))
    except BaseException as e:
        send_email(sender_email, password, maintainer_email, 
                   subject="Error in 'ai_safety_papers'", 
                   content=MIMEText(traceback.format_exc(), "plain"))

if __name__ == "__main__":
    send_ai_safety_email()
