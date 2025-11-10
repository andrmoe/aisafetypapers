import feedparser  # type: ignore
from urllib.parse import quote_plus
from typing import Generator
import time
from datetime import datetime, timedelta, UTC
from dataclasses import dataclass


@dataclass
class Paper:
    title: str
    publication_time: datetime
    authors: list[str]
    summary: str
    link: str


def fetch_papers() \
                    -> Generator[Paper, None, None]:
    paper_count = 0
    rss_url = "https://rss.arxiv.org/rss/cs"

    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        paper_count += 1
        pub_time = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
        print(pub_time.isoformat())
        paper = Paper(title=entry.title.strip().replace("\n", " "),
                        publication_time=pub_time,
                        authors=[str(author.name) for author in entry.authors],
                        summary=entry.summary,
                        link=entry.link)
        yield paper
    print(f"Found {paper_count} papers.")
    