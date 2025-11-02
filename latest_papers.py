import feedparser
from urllib.parse import quote_plus
from typing import Generator
import time
from datetime import datetime, timedelta, UTC

def fetch_papers(max_results: int=10000, time_cutoff: timedelta=timedelta(hours=48), categories: tuple[str, ...] = ("cs.AI", "cs.LG", "stat.ML")) \
                    -> Generator[tuple[str, str, str, str, list[str]], None, None]:
    page_size = 100
    query = quote_plus(" OR ".join([f"cat:{cat}" for cat in categories]))
    cutoff = datetime.now(UTC) - time_cutoff

    for index in range(0, max_results, page_size):
        rss_url = (
            f"https://export.arxiv.org/api/query?"
            f"search_query={query}&sortBy=submittedDate&sortOrder=descending&start={index}&max_results={page_size}"
        )

        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            pub_time = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
            if pub_time < cutoff:
                # All remaining entries are older
                return 
            yield entry.title.strip().replace("\n", " "), entry.published, \
                entry.link, entry.summary, [str(author.name) for author in entry.authors]

        time.sleep(0.5)
    raise EnvironmentError(f"All {max_results} most recent papers are newer than the cutoff = {time_cutoff}. "
                           f"The program might be stuck in an infinite loop.")
