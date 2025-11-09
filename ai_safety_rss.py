from typing import Generator, Iterable
from latest_papers import Paper
from pathlib import Path


def load_authors(directory: Path = Path.home() / "aisafetypapers") -> Generator[str, None, None]:
    with open(directory / "authors.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            yield line[:-1]

def create_html(papers: Iterable[Paper], min_alignment_author_position: int = 4) -> str | None:
    alignment_authors = list(load_authors())
    alignment_papers: list[tuple[int, Paper]] = []
    alignment_positions: list[int] = []
    for paper in papers:
        if any((name in alignment_authors) for name in paper.authors):
            alignment_author = [name for name in paper.authors if name in alignment_authors][0]
            alignment_author_pos = paper.authors.index(alignment_author)
            alignment_positions.append(alignment_author_pos)
            if alignment_author_pos < min_alignment_author_position:
                alignment_papers.append((alignment_author_pos, paper))
    alignment_papers.sort(key=lambda x: x[0])

    if len(alignment_papers) == 0:
        print("No new papers")
        print(f"Smallest position: {'NaN' if not alignment_positions else min(alignment_positions)}")
        return None

    email_str = f"<html><body><h1>New Papers from AI Safety Researchers (based on this <a href=https://airtable.com/appWAkbSGU6x8Oevt/shraOj3kb8ESTOOmh/tblCiItlYmFQqOKat>list</a>)</h1>\n\n"
    for _, paper in alignment_papers:
        author_list = paper.authors
        author_list_str = ", ".join(author_list)
        for a in alignment_authors:
            author_list_str = author_list_str.replace(a, f'<b>{a}</b>')
        email_str += f'<h6>{paper.publication_time}</h6><h2><a href={paper.link}>{paper.title}</a></h2>\n'
        email_str += author_list_str+'<br/>\n'
        email_str += f'<p>Abstract: {paper.summary}</p>\n\n'

    email_str += "</body></html>"

    return email_str
