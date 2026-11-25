"""
HumanMol AI - Scientific Engine Server Entrypoint
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn
from scientific_engine.api.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting HumanMol AI Scientific Engine on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
