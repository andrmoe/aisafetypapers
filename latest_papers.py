import feedparser
from urllib.parse import quote_plus
from typing import Generator

def fetch_papers(max_results: int=200, categories: tuple[str, ...] = ("cs.AI", "cs.LG")) -> Generator[tuple[str, str, str, str, list[str]], None, None]:

    query = quote_plus(" OR ".join([f"cat:{cat}" for cat in categories]))

    rss_url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        yield entry.title.strip().replace("\n", " "), entry.published, entry.link, entry.summary, [str(author.name) for author in entry.authors]

if __name__ == "__main__":
    for title, date, link, authors in fetch_papers():
        print(title)
        print(authors)
        print(date)
        print(link)
        print()