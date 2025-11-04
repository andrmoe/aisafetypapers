import pytest
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox
from email.mime.text import MIMEText
from typing import Generator
import json
from mailbox import Maildir, MaildirMessage
from operator import itemgetter

from ai_safety_rss import load_authors
from ai_safety_email import send_email

def test_load_authors(tmpdir: Path) -> None:
    file_path = tmpdir / "authors.txt"
    authors = "Adam Gleave\nAdam Shimi\nAdrià Garriga-Alonso\nAdrian Weller\nAidan Kierans\nAkbir Khan\n"
    file_path.write_text(authors, encoding="utf-8")
    loaded_authors = list(load_authors(tmpdir))
    assert len(loaded_authors) == 6
    assert loaded_authors[0] == "Adam Gleave"
    assert loaded_authors[1] == "Adam Shimi"
    assert loaded_authors[2] == "Adrià Garriga-Alonso"
    assert loaded_authors[3] == "Adrian Weller"
    assert loaded_authors[4] == "Aidan Kierans"
    assert loaded_authors[5] == "Akbir Khan"

class EmailTester:
    def __init__(self, mailbox_dir: Path) -> None:
        self.hostname = "127.0.0.1"
        self.port = 1025
        self.mailbox_dir = mailbox_dir
        for sub in ["cur", "new", "tmp"]:
            (mailbox_dir / sub).mkdir(parents=True, exist_ok=True)
        self.controller = Controller(Mailbox(mailbox_dir), hostname=self.hostname, port=self.port)
    
    def received_messages(self) -> list[MaildirMessage]:
        mailbox = Maildir(self.mailbox_dir)
        return sorted(mailbox, key=itemgetter('message-id'))

@pytest.fixture()
def email_tester(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[EmailTester, None, None]:
    monkeypatch.setattr("smtplib.SMTP.starttls", lambda self: None)
    monkeypatch.setattr("smtplib.SMTP.login", lambda self, email, password: None)
    email_tester_inst = EmailTester(tmp_path)
    email_tester_inst.controller.start()
    try:
        yield email_tester_inst
    finally:
        email_tester_inst.controller.stop()

@pytest.mark.parametrize("content_type", ["plain", "html"])
def test_send_email(email_tester: EmailTester, tmp_path: Path, content_type: str) -> None:
    sender = f"user0@{email_tester.hostname}"
    receiver = f"user2@{email_tester.hostname}"
    conf = {
        "sender_email": sender,
        "receiver_emails": [],
        "maintainer_email": "",
        "password": "",
        "host": "127.0.0.1",
        "port": 1025,
    }
    (tmp_path / ".env").write_text(json.dumps(conf))
    subject = "Test Subject"
    content = "Test Content"
    send_email(receiver_email=receiver,
               subject=subject,
               content=MIMEText(content, content_type),
               config_path=tmp_path / ".env")
    messages = email_tester.received_messages()
    assert len(messages) == 1
    for message in messages:
        assert message['X-MailFrom'] == message['From'] == sender
        assert message['X-RcptTo'] == message['To'] == receiver
        assert message['Subject'] == subject
        assert content_type in str(message)
        assert content in str(message)
