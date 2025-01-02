import pandas as pd
from scholarly import scholarly
from time import sleep

# Load author list
authors_df = pd.read_csv('authors.txt')  # Adjust column name as needed
author_names = authors_df['AuthorName'].tolist()
print(author_names)
# Collect recent papers
papers = set()

for name in ["Evan Hubinger", "Chris van Merwijk", "Vladimir Mikulik", "Joar Skalse", "Scott Garrabrant"]:
    print(name, len(papers))
    search_query = scholarly.search_author(name)
    try:
        author = next(search_query)
        scholarly.fill(author, sections=["publications"])
        for pub in author['publications']:
            if 'pub_year' in pub['bib']:
                # print((pub['bib']['title'], int(pub['bib']['pub_year'])))
                if int(pub['bib']['pub_year']) >= 2019 and pub['bib']['title'] not in papers:
                    pub_query = scholarly.search_pubs(pub['bib']['title'])
                    scholarly.pprint(next(search_query))

                    papers.add(pub['bib']['title'])
        print(papers)
    except StopIteration:
        continue

print(papers)
