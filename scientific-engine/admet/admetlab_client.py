"""
HumanMol AI - ADMET Engine (ADMETlab 3.0 API Client)
Provides absorption, distribution, metabolism, excretion, and toxicity evaluation
via the verified ADMETlab 3.0 REST service.
"""

import time
import requests
from typing import Dict, Any, List, Optional

class ADMETService:
    def __init__(self, base_url: str = "https://admetlab3.scbdd.com"):
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/single/admet"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"{self.base_url}/"
        })
        self._initialized = False

    def _ensure_session(self):
        if not self._initialized:
            try:
                self.session.get(f"{self.base_url}/", timeout=10)
                self._initialized = True
            except Exception:
                pass

    def predict_properties(self, smiles: str) -> Dict[str, Any]:
        """
        Sends SMILES for comprehensive ADMET profiling via ADMETlab 3.0.
        Includes automatic retry for transient 429 rate-limiting.
        """
        self._ensure_session()
        payload = {"SMILES": smiles}
        
        t0 = time.time()
        resp = None
        for attempt in range(3):
            try:
                resp = self.session.post(self.endpoint, json=payload, timeout=25)
                if resp.status_code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    try:
                        self.session.get(f"{self.base_url}/", timeout=10)
                    except Exception:
                        pass
                    continue
                break
            except Exception as e:
                if attempt == 2:
                    return {"success": False, "smiles": smiles, "error": str(e)}
                time.sleep(1)

        t1 = time.time()
        if resp is not None and resp.status_code == 200:
            try:
                raw_json = resp.json()
                data_dict = raw_json.get("data", {}).get("data", {})
                
                # Extract summary endpoints
                summary = {}
                for category, items in data_dict.items():
                    summary[category] = {item.get("name"): item.get("value") for item in items if isinstance(item, dict)}
                
                return {
                    "success": True,
                    "smiles": smiles,
                    "execution_time_seconds": round(t1 - t0, 3),
                    "categories": list(data_dict.keys()),
                    "summary": summary,
                    "raw_data": data_dict
                }
            except Exception as e:
                return {"success": False, "smiles": smiles, "error": f"JSON parse error: {e}"}
        else:
            status = resp.status_code if resp is not None else 500
            err_msg = resp.text[:200] if resp is not None else "No response"
            return {
                "success": False,
                "smiles": smiles,
                "status_code": status,
                "error": f"HTTP {status}: {err_msg}"
            }

if __name__ == "__main__":
    service = ADMETService()
    test_smi = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    print(f"Querying ADMETlab 3.0 for {test_smi}...")
    res = service.predict_properties(test_smi)
    print("Success:", res.get("success"))
    print("Execution time:", res.get("execution_time_seconds"), "s")
    if res.get("success"):
        summary = res.get("summary", {})
        print("\n--- Key Predictions ---")
        for cat in ["absorption", "distribution", "metabolism", "toxicity"]:
            if cat in summary:
                print(f"[{cat.upper()}]", list(summary[cat].items())[:4])
