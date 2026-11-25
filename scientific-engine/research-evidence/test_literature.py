import time
import os
import sys

from pubmed_service import search_pubmed_literature
from arxiv_service import search_arxiv_preprints

query = "EGFR tyrosine kinase inhibitor"

print("=== 1. PUBMED EVIDENCE RETRIEVAL ===")
t0 = time.time()
pubmed_results = search_pubmed_literature(query, max_results=3)
t1 = time.time()
print(f"Query: '{query}'")
print(f"Execution Time: {round(t1 - t0, 3)} seconds")
print(f"Results Count: {len(pubmed_results)}")
for idx, p in enumerate(pubmed_results, 1):
    print(f"\n[{idx}] PMID: {p.get('pmid')} | Source: {p.get('journal')} ({p.get('pub_year')})")
    print(f"    Title: {p.get('title')}")
    print(f"    DOI: {p.get('doi')}")
    print(f"    URL: {p.get('url')}")
    print(f"    Abstract: {p.get('abstract')[:160]}...")

print("\n=== 2. ARXIV PREPRINT RETRIEVAL ===")
t2 = time.time()
arxiv_results = search_arxiv_preprints(query, max_results=3)
t3 = time.time()
print(f"Query: '{query}'")
print(f"Execution Time: {round(t3 - t2, 3)} seconds")
print(f"Results Count: {len(arxiv_results)}")
for idx, a in enumerate(arxiv_results, 1):
    print(f"\n[{idx}] arXiv ID: {a.get('id')} | Published: {a.get('published')}")
    print(f"    Title: {a.get('title')}")
    print(f"    PDF URL: {a.get('pdf_url')}")
    print(f"    Authors: {', '.join(a.get('authors', [])[:3])}")
    print(f"    Abstract: {a.get('abstract')[:160]}...")
