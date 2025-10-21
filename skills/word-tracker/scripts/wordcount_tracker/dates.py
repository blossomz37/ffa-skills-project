# dates.py
# Purpose: return best-effort creation date as YYYY-MM-DD,
# and provide utilities for date handling.

from datetime import datetime, timedelta
from pathlib import Path
import platform
import re
from typing import Optional, Dict, Any

DATE_FMT = "%Y-%m-%d"

def iso_date(ts: float) -> str:
    """Convert timestamp to ISO date format."""
    return datetime.fromtimestamp(ts).strftime(DATE_FMT)

def file_created_date(path: Path) -> str:
    """
    macOS: uses st_birthtime when available
    Windows: st_ctime is creation time
    Linux: st_ctime is change time (fallback)
    """
    st = path.stat()
    birth = getattr(st, "st_birthtime", None)
    if birth:
        return iso_date(birth)
    return iso_date(st.st_ctime)

def file_modified_date(path: Path) -> str:
    """Get file's last modification date."""
    return iso_date(path.stat().st_mtime)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string in various formats."""
    formats = [
        DATE_FMT,  # Our standard format
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def extract_frontmatter_date(text: str) -> Optional[str]:
    """
    Extract date from YAML frontmatter if present.
    Looks for 'created', 'date', or 'created_at' fields.
    """
    if not text.startswith("---"):
        return None
    
    try:
        # Simple YAML parsing for date fields
        lines = text.split("\n")
        in_frontmatter = False
        
        for line in lines[1:]:  # Skip first ---
            if line.strip() == "---":
                break
            
            # Look for date fields
            patterns = [
                r'^created:\s*(.+)$',
                r'^date:\s*(.+)$',
                r'^created_at:\s*(.+)$',
                r'^creation_date:\s*(.+)$',
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip().strip('"').strip("'")
                    parsed = parse_date(date_str)
                    if parsed:
                        return parsed.strftime(DATE_FMT)
    except Exception:
        pass
    
    return None

def date_range(start_date: str, end_date: str) -> list[str]:
    """Generate list of dates between start and end (inclusive)."""
    start = datetime.strptime(start_date, DATE_FMT)
    end = datetime.strptime(end_date, DATE_FMT)
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime(DATE_FMT))
        current += timedelta(days=1)
    
    return dates

def today_str() -> str:
    """Get today's date in standard format."""
    return datetime.now().strftime(DATE_FMT)

def days_ago(n: int) -> str:
    """Get date n days ago."""
    date = datetime.now() - timedelta(days=n)
    return date.strftime(DATE_FMT)

def week_start_date() -> str:
    """Get the date of Monday of current week."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime(DATE_FMT)
