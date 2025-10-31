import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai_safety_rss import create_html
import os
import json
from datetime import datetime, UTC
import traceback

dir = os.path.dirname(__file__)

def send_email() -> None:
    # Email configuration
    conf = None
    with open(f"{dir}/.env", "r") as f:
        conf = json.loads(f.read())
    sender_email = conf["sender_email"]
    receiver_emails = conf["receiver_emails"]
    maintainer_email = conf["maintainer_email"]
    password = conf["password"]

    # Create the email
    try:
        print()
        print(f"Time: {datetime.now(tz=UTC)}")
        for receiver_email in receiver_emails:
            subject = "New Papers from AI Safety Researchers"

            email_content = create_html()
            if email_content is None:
                return
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email

            msg['Subject'] = subject
            msg.attach(MIMEText(email_content, 'html'))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print(f"Email sent successfully to {receiver_email}.")
    except BaseException as e:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = maintainer_email
        msg['Subject'] = "Error in 'ai_safety_papers'"
        msg.attach(MIMEText(traceback.format_exc(), "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, maintainer_email, msg.as_string())
            print(f"Email with exception stack trace sent successfully to {maintainer_email}.")
            raise


if __name__ == "__main__":
    send_email()
