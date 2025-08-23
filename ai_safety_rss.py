from typing import Generator
import reader
import os

dir = os.path.dirname(__file__)

def load_authors() -> Generator[str, None, None]:
    with open(f"{dir}/authors.txt", "r", encoding="utf-8") as f:
        for line in f.readlines():
            yield line[:-1]

def create_html(min_alignment_author_position: int = 2) -> str | None:
    r = reader.make_reader('db.sqlite')
    #r.add_feed("https://rss.arxiv.org/rss/cs.ai")
    r.update_feeds()
    entries = r.get_entries(read=False)
    authors = list(load_authors())
    alignment_papers = []
    for e in entries:
        if any((name in authors) for name in e.author.split(', ')):
            alignment_author = [name for name in e.author.split(', ') if name in authors][0]
            alignment_author_pos = e.author.split(', ').index(alignment_author)
            if alignment_author_pos < min_alignment_author_position:
                alignment_papers.append((alignment_author_pos, e))
                r.mark_entry_as_read(e)
    alignment_papers.sort(key=lambda x: x[0])

    if len(alignment_papers) == 0:
        print("No new papers")
        return None

    email_str = f"<html><body><h1>New Papers from AI Safety Researchers (based on this <a href=https://airtable.com/appWAkbSGU6x8Oevt/shraOj3kb8ESTOOmh/tblCiItlYmFQqOKat>list</a>)</h1>\n\n"
    for _, paper in alignment_papers:
        author_list = paper.author
        for a in authors:
            author_list = author_list.replace(a, f'<b>{a}</b>')
        email_str += f'<h2><a href={paper.link}>{paper.title}</a></h2>\n'
        email_str += author_list+'<br/>\n'
        email_str += f'<p>Abstract: {paper.summary.split("Abstract: ")}</p>\n\n'

    email_str += "</body></html>"

    with open("email.html", "w") as f:
        f.write(email_str)

    return email_str


if __name__ == '__main__':
    create_html()