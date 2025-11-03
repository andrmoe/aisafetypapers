import pytest
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox
from typing import Generator

from ai_safety_rss import load_authors

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
        self.controller = Controller(Mailbox(mailbox_dir))
        self.controller.start()

pytest.fixture
def email_tester(tmp_path: Path) -> Generator[EmailTester, None, None]:
    email_tester_inst = EmailTester(tmp_path)
    yield email_tester_inst
    email_tester_inst.controller.stop()
