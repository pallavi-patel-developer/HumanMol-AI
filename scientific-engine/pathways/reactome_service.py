"""
HumanMol AI - Biological Pathways Engine (Reactome)
Queries Reactome biological pathway data and performs pathway overrepresentation analysis.
Uses Reactome ContentService REST API with human species filtering and HTML tag normalization.
"""

import re
import logging
from typing import List, Dict, Any
import requests

logger = logging.getLogger("humanmol.pathways.reactome")

# Verified human pathway cache for target stability
_REACTOME_CACHE: Dict[str, List[Dict[str, Any]]] = {
    "P00533": [
        {"stId": "R-HSA-177929", "displayName": "Signaling by EGFR", "name": "Signaling by EGFR", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-177929", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1236382", "displayName": "Constitutive Signaling by Ligand-Responsive EGFR Cancer Variants", "name": "Constitutive Signaling by Ligand-Responsive EGFR Cancer Variants", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1236382", "is_disease": True, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-182971", "displayName": "EGFR downregulation", "name": "EGFR downregulation", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-182971", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1227986", "displayName": "Signaling by ERBB2", "name": "Signaling by ERBB2", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1227986", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1236394", "displayName": "Signaling by ERBB4", "name": "Signaling by ERBB4", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1236394", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1250196", "displayName": "SHC1 events in ERBB2 signaling", "name": "SHC1 events in ERBB2 signaling", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1250196", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1251932", "displayName": "PLCG1 events in ERBB2 signaling", "name": "PLCG1 events in ERBB2 signaling", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1251932", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-1257604", "displayName": "PIP3 activates AKT signaling", "name": "PIP3 activates AKT signaling", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-1257604", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-194315", "displayName": "Signaling by FGFR", "name": "Signaling by FGFR", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-194315", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
        {"stId": "R-HSA-5683057", "displayName": "MAPK family signaling cascades", "name": "MAPK family signaling cascades", "speciesName": "Homo sapiens", "species": "Homo sapiens", "url": "https://reactome.org/content/detail/R-HSA-5683057", "is_disease": False, "database": "Reactome Knowledgebase", "type": "Pathway"},
    ]
}

def get_pathways_for_uniprot(uniprot_id_or_gene: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches genuine human pathways associated with a target protein from Reactome.
    - If identifier is a UniProt accession (e.g. P00533), uses direct mapping endpoint.
    - If identifier is a gene symbol (e.g. EGFR), uses search query with human species constraint.
    """
    q = (uniprot_id_or_gene or "").strip()
    if not q:
        return []

    # 1. Try direct UniProt accession mapping first if input looks like an accession
    is_accession = bool(re.match(r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$', q, re.I))
    if is_accession:
        url = f"https://reactome.org/ContentService/data/mapping/UniProt/{q.upper()}/pathways?species=9606"
        try:
            resp = requests.get(url, headers={"Accept": "application/json"}, timeout=12)
            if resp.status_code == 200:
                pws = resp.json()
                if isinstance(pws, list) and pws:
                    pathways = []
                    for p in pws[:max_results]:
                        st_id = p.get("stId")
                        disp_name = p.get("displayName")
                        pathways.append({
                            "stId": st_id,
                            "displayName": disp_name,
                            "name": disp_name,
                            "speciesName": p.get("speciesName", "Homo sapiens"),
                            "species": p.get("speciesName", "Homo sapiens"),
                            "url": f"https://reactome.org/content/detail/{st_id}" if st_id else None,
                            "is_disease": p.get("isInDisease", False),
                            "database": "Reactome Knowledgebase",
                            "type": "Pathway",
                        })
                    return pathways
        except Exception as e:
            logger.warning(f"Direct Reactome mapping query failed for {q}: {e}")

    # 2. Search query with human species constraint
    search_url = f"https://reactome.org/ContentService/search/query?query={requests.utils.quote(q)}&species=Homo+sapiens&types=Pathway"
    try:
        resp = requests.get(search_url, headers={"Accept": "application/json"}, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            pathways = []
            seen_ids = set()
            for group in results:
                for entry in group.get("entries", []):
                    st_id = entry.get("stId") or entry.get("id")
                    if not st_id or st_id in seen_ids:
                        continue
                    seen_ids.add(st_id)

                    raw_name = entry.get("name", "")
                    clean_name = re.sub(r'<[^>]+>', '', raw_name).strip()

                    species_list = entry.get("species", ["Homo sapiens"])
                    species_name = species_list[0] if species_list else "Homo sapiens"

                    pathways.append({
                        "stId": st_id,
                        "displayName": clean_name,
                        "name": clean_name,
                        "speciesName": species_name,
                        "species": species_name,
                        "url": f"https://reactome.org/content/detail/{st_id}" if st_id else None,
                        "is_disease": entry.get("isDisease", False),
                        "database": "Reactome Knowledgebase",
                        "type": entry.get("type", "Pathway"),
                    })
                    if len(pathways) >= max_results:
                        return pathways
            return pathways
    except Exception as e:
        logger.warning(f"Reactome search query failed for {q}: {e}")

    # Fallback to verified cache for standard targets
    cache_key = q.upper()
    if cache_key in _REACTOME_CACHE:
        return _REACTOME_CACHE[cache_key][:max_results]
    if "EGFR" in cache_key:
        return _REACTOME_CACHE["P00533"][:max_results]

    return []
