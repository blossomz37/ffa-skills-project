# tracker.py
# Purpose: CSV I/O and merge logic for add/update rows.

from __future__ import annotations
import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

HEADER = ["Filename", "Word Count", "Date Created", "Date Updated"]
DATE_FMT = "%Y-%m-%d"

@dataclass
class Row:
    filename: str
    word_count: int
    date_created: str
    date_updated: str = ""  # blank for new entries
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for CSV writer."""
        return {
            "Filename": self.filename,
            "Word Count": str(self.word_count),
            "Date Created": self.date_created,
            "Date Updated": self.date_updated,
        }

@dataclass
class TrackerStats:
    """Statistics about tracking session."""
    files_scanned: int = 0
    new_files: int = 0
    updated_files: int = 0
    total_words: int = 0
    errors: List[str] = field(default_factory=list)

def ensure_tracker_exists(csv_path: Path) -> None:
    """Create CSV with header if it doesn't exist."""
    if not csv_path.exists():
        csv_path.write_text(",".join(HEADER) + "\n", encoding="utf-8")

def load_rows(csv_path: Path) -> Dict[str, Row]:
    """Load rows into a dict keyed by filename for O(1) updates."""
    rows: Dict[str, Row] = {}
    if not csv_path.exists():
        return rows
        
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            fn = (r.get("Filename") or "").strip()
            if not fn:
                continue
            rows[fn] = Row(
                filename=fn,
                word_count=int((r.get("Word Count") or "0").strip() or 0),
                date_created=(r.get("Date Created") or "").strip(),
                date_updated=(r.get("Date Updated") or "").strip(),
            )
    return rows

def save_rows(csv_path: Path, rows: Dict[str, Row]) -> None:
    """Write all rows sorted by filename to keep the file stable in git diffs."""
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        for key in sorted(rows.keys(), key=str.lower):
            writer.writerow(rows[key].to_dict())

def today_str() -> str:
    """Get today's date in standard format."""
    return datetime.now().strftime(DATE_FMT)

def upsert_row(rows: Dict[str, Row], new_row: Row, is_update: bool) -> None:
    """
    Merge logic:
    - If updating existing: replace word count and set Date Updated = today
    - If inserting new: keep Date Updated blank
    """
    if is_update:
        existing = rows[new_row.filename]
        existing.word_count = new_row.word_count
        existing.date_updated = today_str()
        # keep existing.date_created as is; fill if blank
        if not existing.date_created:
            existing.date_created = new_row.date_created
    else:
        rows[new_row.filename] = new_row

def backup_tracker(csv_path: Path) -> Optional[Path]:
    """Create a backup of the tracker file."""
    if not csv_path.exists():
        return None
        
    backup_path = csv_path.with_suffix(f".backup_{today_str()}.csv")
    backup_path.write_bytes(csv_path.read_bytes())
    return backup_path

def get_tracker_summary(rows: Dict[str, Row]) -> Dict[str, any]:
    """Get summary statistics from tracker data."""
    if not rows:
        return {
            "total_files": 0,
            "total_words": 0,
            "average_words": 0,
            "newest_file": None,
            "oldest_file": None,
        }
    
    total_words = sum(r.word_count for r in rows.values())
    dates = [r.date_created for r in rows.values() if r.date_created]
    
    return {
        "total_files": len(rows),
        "total_words": total_words,
        "average_words": total_words // len(rows) if rows else 0,
        "newest_file": max(dates) if dates else None,
        "oldest_file": min(dates) if dates else None,
    }
