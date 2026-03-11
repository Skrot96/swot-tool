"""
Hantering av sparade analyser med JSON-fil.
"""

import json
import os
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "analyses.json"


def ensure_data_dir():
    """Skapa data-katalogen om den inte finns."""
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def save_analysis(name: str, data: dict) -> None:
    """
    Spara en analys med angivet namn.
    """
    ensure_data_dir()
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        analyses = json.load(f)
    
    analyses[name] = {
        **data,
        "saved_at": datetime.now().isoformat()
    }
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)


def load_analysis(name: str) -> dict | None:
    """
    Ladda en sparad analys.
    """
    ensure_data_dir()
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        analyses = json.load(f)
    
    return analyses.get(name)


def list_analyses() -> list[str]:
    """
    Lista alla sparade analyser.
    """
    ensure_data_dir()
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        analyses = json.load(f)
    
    return list(analyses.keys())


def delete_analysis(name: str) -> bool:
    """
    Ta bort en sparad analys.
    """
    ensure_data_dir()
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        analyses = json.load(f)
    
    if name in analyses:
        del analyses[name]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)
        return True
    
    return False
