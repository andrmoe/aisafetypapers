import pytest
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox
from email.mime.text import MIMEText
from typing import Generator
import json
from mailbox import Maildir, MaildirMessage
from operator import itemgetter
from datetime import datetime
from lxml import html as lxml_html
import html
from feedparser import FeedParserDict  # type: ignore
from freezegun import freeze_time

from ai_safety_rss import load_authors, filter_for_alignment, create_html
from ai_safety_email import send_email
from latest_papers import Paper, fetch_papers

@pytest.fixture
def fake_author_file(tmpdir: Path) -> Path:
    file_path = tmpdir / "authors.txt"
    authors = "Adam Gleave\nAdam Shimi\nAdrià Garriga-Alonso\nAdrian Weller\nAidan Kierans\nAkbir Khan\n"
    file_path.write_text(authors, encoding="utf-8")
    return file_path

def test_load_authors(fake_author_file: Path) -> None:
    loaded_authors = list(load_authors(fake_author_file))
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


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    host = "127.0.0.1"
    conf = {
        "sender_email": f"sender@{host}",
        "receiver_emails": [f"receiver{i}@{host}" for i in range(2)],
        "maintainer_email": f"maintainer@{host}",
        "password": "badpassword",
        "host": host,
        "port": 1025,
    }
    config_path = tmp_path / ".env"
    config_path.write_text(json.dumps(conf))
    return config_path


@pytest.mark.parametrize("content_type", ["plain", "html"])
def test_send_email(email_tester: EmailTester, config_file: Path, content_type: str) -> None:
    config = json.loads(config_file.read_text(encoding="utf-8"))
    subject = "Test Subject"
    receiver = f"receiver@{config["host"]}"
    content = "Test Content"
    send_email(receiver_email=receiver,
               subject=subject,
               content=MIMEText(content, content_type),
               config_path=config_file)
    messages = email_tester.received_messages()
    assert len(messages) == 1
    for message in messages:
        assert message['X-MailFrom'] == message['From'] == config["sender_email"]
        assert message['X-RcptTo'] == message['To'] == receiver
        assert message['Subject'] == subject
        assert content_type in str(message)
        assert content in str(message)

@pytest.fixture
def fake_papers() -> list[Paper]:
    return [
        Paper("Dumb <script>experiment</script>", datetime(2024, 2, 29, 12, 15, 50),
                ["Andreas Polk", "Emily Tirol", "Warren Bender", "Adam Shimi"], 
                "Dumb summary", "https://fakelink.int/dumbpaper"),
        Paper("Smart experiment", datetime(2025, 2, 28, 17, 45, 52),
            ["Gillian Trouble", "Armen <script>Fury</script>"], 
            "Smart summary", "https://fakelink.int/smartpaper"),
        Paper("On the existence of ghosts", datetime(2025, 2, 27, 12, 0, 0),
            [], 
            "Summary: <script>I</script> am a ghost", "https://fakelink.int/ghosts"),
        Paper("Dumb Collaboration", datetime(2025, 2, 27, 12, 0, 0),
            [f"Author {i}" for i in range(10000)], 
            "Collaborative summary", "https://fakelink.int/<script>collaboration</script>"),
        Paper("On-line anti-robustness checkable bootstrapping supervisory scaling, through sub-quadratic recursive re-reduction", 
            datetime(2025, 2, 27, 12, 0, 0),
            ["Aidan Kierans", "Rune Filkony"], 
            "Summarisation through long fast-indexible glue search", 
            "https://fakelink.int/coolpaper"),
        ]

def test_filter_for_alignment(fake_author_file: Path, fake_papers: list[Paper]) -> None:
    alignment_papers = filter_for_alignment(fake_papers, 
                                            min_alignment_author_position=2, 
                                            author_file=fake_author_file)
    assert alignment_papers == [Paper("On-line anti-robustness checkable bootstrapping supervisory scaling, through sub-quadratic recursive re-reduction", 
            datetime(2025, 2, 27, 12, 0, 0),
            ["Aidan Kierans", "Rune Filkony"], 
            "Summarisation through long fast-indexible glue search", 
            "https://fakelink.int/coolpaper")]
    
def test_filter_for_alignment_no_papers(fake_author_file: Path, fake_papers: list[Paper]) -> None:
    alignment_papers = filter_for_alignment(fake_papers[:4], 
                                            min_alignment_author_position=2, 
                                            author_file=fake_author_file)
    assert alignment_papers == []

def test_create_html(fake_papers: list[Paper], fake_author_file: Path) -> None:
    html_page = create_html(fake_papers, fake_author_file)
    assert html_page is not None
    for paper in fake_papers:
        assert html.escape(paper.title) in html_page
        assert html.escape(paper.summary) in html_page
        assert f'<a href="{html.escape(paper.link)}"' in html_page
        for author in paper.authors:
            assert html.escape(author) in html_page
    
    assert f"<b>Andreas Polk</b>" not in html_page
    assert "<script>" not in html_page
    assert f"<b>Adam Shimi</b>" in html_page
    assert f"<b>Aidan Kierans</b>" in html_page
    lxml_html.fromstring(html_page)


def test_create_html_no_papers(fake_author_file: Path) -> None:
    html_page = create_html([], fake_author_file)
    assert html_page is None

@freeze_time("2025-11-10 15:00:00")
def test_fetch_papers(monkeypatch: pytest.MonkeyPatch) -> None:
    def test_parse(url: str) -> FeedParserDict:
        return FeedParserDict(entries=[
            FeedParserDict(published="2025-11-10T10:41:09Z",
                           title="Test Title",
                           authors=[],
                           summary="",
                           link=""),
            FeedParserDict(published="2025-10-10T23:41:09Z",
                           title="Test Title",
                           authors=[],
                           summary="",
                           link="")
                        ])
    monkeypatch.setattr("latest_papers.feedparser.parse", test_parse)
    for paper in fetch_papers():
        assert paper.title == "Test Title"
        assert paper.authors == []
        assert paper.link == ""
        assert paper.summary == ""
        # TODO: assert date