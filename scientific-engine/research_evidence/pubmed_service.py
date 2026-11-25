"""
HumanMol AI - Research Evidence Engine (PubMed / Entrez)
Searches scientific literature, retrieves abstracts, and links clinical/preclinical evidence.
"""

from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

def search_pubmed_literature(query: str, max_results: int = 5, email: str = "humanmol@example.com") -> List[Dict[str, Any]]:
    """Searches PubMed via Biopython Entrez, retrieving full metadata and abstracts."""
    from Bio import Entrez
    Entrez.email = email
    
    # 1. Search PMIDs
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
    record = Entrez.read(handle)
    handle.close()
    
    id_list = record.get("IdList", [])
    if not id_list:
        return []

    # 2. Fetch Medline XML records for abstracts and complete metadata
    handle = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="xml", retmode="xml")
    xml_data = handle.read()
    handle.close()

    root = ET.fromstring(xml_data)
    articles = []
    
    for article_elem in root.findall(".//PubmedArticle"):
        medline = article_elem.find("MedlineCitation")
        if medline is None:
            continue
            
        pmid = medline.findtext("PMID", default="")
        art = medline.find("Article")
        if art is None:
            continue
            
        title = art.findtext("ArticleTitle", default="").strip()
        
        # Abstract
        abstract_elem = art.find("Abstract")
        abstract_text = ""
        if abstract_elem is not None:
            parts = [t.text for t in abstract_elem.findall("AbstractText") if t.text]
            abstract_text = " ".join(parts).strip()
            
        # Journal & Date
        journal = art.findtext("Journal/Title", default="")
        pub_year = art.findtext("Journal/JournalIssue/PubDate/Year", default="")
        
        # Authors
        authors = []
        author_list = art.find("AuthorList")
        if author_list is not None:
            for auth in author_list.findall("Author"):
                last = auth.findtext("LastName", default="")
                fore = auth.findtext("ForeName", default="")
                if last or fore:
                    authors.append(f"{fore} {last}".strip())
                    
        # DOI
        doi = ""
        article_ids = article_elem.findall(".//ArticleId")
        for aid in article_ids:
            if aid.attrib.get("IdType") == "doi" and aid.text:
                doi = aid.text.strip()
                break

        articles.append({
            "source": "PubMed",
            "pmid": pmid,
            "title": title,
            "abstract": abstract_text,
            "authors": authors,
            "journal": journal,
            "pub_year": pub_year,
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "doi_url": f"https://doi.org/{doi}" if doi else ""
        })
        
    return articles

if __name__ == "__main__":
    test_query = "EGFR tyrosine kinase inhibitor"
    print(f"Querying PubMed for '{test_query}'...")
    results = search_pubmed_literature(test_query, max_results=3)
    print(f"Retrieved {len(results)} articles:")
    for a in results:
        print(f"- [{a['pmid']}] {a['title']}")
        print(f"  Journal: {a['journal']} ({a['pub_year']})")
        print(f"  Abstract snippet: {a['abstract'][:150]}...")
        print(f"  URL: {a['url']}")

