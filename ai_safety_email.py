import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai_safety_rss import create_html
import os
import json

dir = os.path.dirname(__file__)

def send_email() -> None:
    # Email configuration
    conf = None
    with open(f"{dir}/.env", "r") as f:
        conf = json.loads(f.read())
    sender_email = conf["sender_email"]
    receiver_email = conf["receiver_email"]
    password = conf["password"]

    # Create the email
    subject = "New Papers from AI Safety Researchers"

    email_content = create_html()
    if email_content is None:
        return
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg['Subject'] = subject
    msg.attach(MIMEText(email_content, 'html'))


    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_email()
