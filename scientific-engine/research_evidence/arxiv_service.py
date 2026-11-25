"""
HumanMol AI - Research Evidence Engine (arXiv API)
Fetches computational chemistry, machine learning, and quantitative biology preprints from arXiv.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

ARXIV_API_BASE = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

def search_arxiv_preprints(
    query: str,
    max_results: int = 5,
    sort_by: str = "relevance",
    sort_order: str = "descending"
) -> List[Dict[str, Any]]:
    """
    Queries the official arXiv REST API for scientific preprints.
    
    :param query: search term (e.g. 'de novo drug design', 'molecular docking')
    :param max_results: maximum number of records to return
    :param sort_by: 'relevance', 'lastUpdatedDate', 'submittedDate'
    :param sort_order: 'descending' or 'ascending'
    :return: list of structured preprint dictionaries
    """
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }
    
    url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "HumanMol-AI/1.0 (mailto:research@humanmol.ai)"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            
        root = ET.fromstring(content)
        entries = root.findall("atom:entry", ATOM_NS)
        
        preprints = []
        for entry in entries:
            title = entry.find("atom:title", ATOM_NS)
            summary = entry.find("atom:summary", ATOM_NS)
            published = entry.find("atom:published", ATOM_NS)
            entry_id = entry.find("atom:id", ATOM_NS)
            
            # Authors
            authors = [
                author.find("atom:name", ATOM_NS).text.strip()
                for author in entry.findall("atom:author", ATOM_NS)
                if author.find("atom:name", ATOM_NS) is not None
            ]
            
            # PDF Link
            pdf_link = None
            for link in entry.findall("atom:link", ATOM_NS):
                if link.attrib.get("title") == "pdf":
                    pdf_link = link.attrib.get("href")
                    break
                    
            preprints.append({
                "source": "arXiv",
                "id": entry_id.text.strip() if entry_id is not None else "",
                "title": title.text.strip().replace("\n", " ") if title is not None else "",
                "abstract": summary.text.strip().replace("\n", " ") if summary is not None else "",
                "authors": authors,
                "published": published.text.strip()[:10] if published is not None else "",
                "pdf_url": pdf_link or "",
            })
            
        return preprints
    except Exception as e:
        return [{"error": str(e), "source": "arXiv"}]

if __name__ == "__main__":
    test_query = "molecular property prediction graph neural network"
    results = search_arxiv_preprints(test_query, max_results=3)
    print(f"arXiv Query '{test_query}' returned {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r.get('title')}")
        print(f"     Authors: {', '.join(r.get('authors', [])[:3])}")
        print(f"     Date: {r.get('published')} | ID: {r.get('id')}")
