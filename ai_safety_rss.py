from typing import Generator, Iterable
import html
from latest_papers import Paper
from pathlib import Path


def load_authors(file: Path = Path.home()) -> Generator[str, None, None]:
    with open(file, "r", encoding="utf-8") as f:
        for line in f.readlines():
            yield line[:-1]


def filter_for_alignment(papers: Iterable[Paper], min_alignment_author_position: int = 4,
                         author_file: Path = Path.home() / "aisafetypapers" / "authors.txt") -> list[Paper]:
    alignment_authors = list(load_authors(author_file))
    alignment_papers: list[tuple[int, Paper]] = []
    alignment_positions: list[int] = []
    for paper in papers:
        if any((name in alignment_authors) for name in paper.authors):
            alignment_author = [name for name in paper.authors if name in alignment_authors][0]
            alignment_author_pos = paper.authors.index(alignment_author)
            alignment_positions.append(alignment_author_pos)
            if alignment_author_pos < min_alignment_author_position:
                alignment_papers.append((alignment_author_pos, paper))
            print(paper.title)
            print(paper.authors)
            print(alignment_author)
    alignment_papers.sort(key=lambda x: x[0])
    if len(alignment_papers) == 0:
        print("No new papers")
        print(f"Smallest position: {'NaN' if not alignment_positions else min(alignment_positions)}")
    return [paper for _, paper in alignment_papers]


def create_html(papers: Iterable[Paper], 
                author_file: Path = Path.home() / "aisafetypapers" / "authors.txt") \
                    -> str | None:
    if not papers:
        return None
    alignment_authors = list(load_authors(author_file))
    email_str = f'<html><body><h1>New Papers from AI Safety Researchers (based on this <a href="https://airtable.com/appWAkbSGU6x8Oevt/shraOj3kb8ESTOOmh/tblCiItlYmFQqOKat">list</a>)</h1>\n\n'
    for paper in papers:
        author_list = paper.authors
        author_list_str = html.escape(", ".join(author_list))
        for a in alignment_authors:
            author_list_str = author_list_str.replace(a, f'<b>{a}</b>')
        email_str += f'<h6>{html.escape(str(paper.publication_time))}</h6><h2><a href="{html.escape(paper.link)}">{html.escape(paper.title)}</a></h2>\n'
        email_str += author_list_str+'<br/>\n'
        email_str += f'<p>Abstract: {html.escape(paper.summary)}</p>\n\n'

    email_str += "</body></html>"

    return email_str
