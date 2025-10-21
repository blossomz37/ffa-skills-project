#!/usr/bin/env python3
"""
Standalone Word Count Tracker Script
A self-contained version for quick deployment without package installation.

Usage:
    python word_tracker_standalone.py
    python word_tracker_standalone.py --drafts manuscripts --recursive
    python word_tracker_standalone.py --report --goal 50000
"""

from __future__ import annotations
import csv
import os
import re
import sys
import platform
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configuration
DATE_FMT = "%Y-%m-%d"
HEADER = ["Filename", "Word Count", "Date Created", "Date Updated"]

@dataclass
class Stats:
    files_scanned: int = 0
    new_files: int = 0  
    updated_files: int = 0
    total_words: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

# Utility functions
def count_words(text: str) -> int:
    """Count words using regex pattern."""
    return len(re.findall(r"\b\w+\b", text))

def read_markdown(path: Path) -> str:
    """Read UTF-8 text with fallback encoding."""
    return path.read_text(encoding="utf-8", errors="ignore")

def iso_date(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD."""
    return dt.strftime(DATE_FMT)

def file_created_date(path: Path) -> str:
    """Get file creation date (best effort across platforms)."""
    stat = path.stat()
    birthtime = getattr(stat, "st_birthtime", None)
    if birthtime:
        return iso_date(datetime.fromtimestamp(birthtime))
    return iso_date(datetime.fromtimestamp(stat.st_ctime))

def find_markdown_files(root: Path, recursive: bool = False) -> List[Path]:
    """Find all .md files in directory."""
    if not root.exists():
        return []
    pattern = "**/*.md" if recursive else "*.md"
    return [p for p in root.glob(pattern) if p.is_file()]

# CSV operations
def ensure_tracker_exists(csv_path: Path) -> None:
    """Create CSV with header if missing."""
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)

def load_tracker(csv_path: Path) -> Dict[str, Dict[str, str]]:
    """Load CSV into dictionary keyed by filename."""
    rows: Dict[str, Dict[str, str]] = {}
    if not csv_path.exists():
        return rows
    
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fn = row.get("Filename", "").strip()
            if fn:
                rows[fn] = {
                    "Filename": fn,
                    "Word Count": row.get("Word Count", "").strip(),
                    "Date Created": row.get("Date Created", "").strip(),
                    "Date Updated": row.get("Date Updated", "").strip(),
                }
    return rows

def save_tracker(csv_path: Path, rows: Dict[str, Dict[str, str]]) -> None:
    """Save tracker dictionary to CSV."""
    sorted_rows = [rows[k] for k in sorted(rows.keys(), key=str.lower)]
    
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(sorted_rows)

# Report generation
def generate_report(rows: Dict[str, Dict[str, str]], stats: Stats, goal: Optional[int] = None) -> None:
    """Print detailed progress report."""
    print("\n" + "=" * 50)
    print("WRITING PROGRESS REPORT")
    print("=" * 50)
    
    total_tracked_words = sum(
        int(r.get("Word Count", 0) or 0) 
        for r in rows.values()
    )
    
    print(f"Session Statistics:")
    print(f"  Files scanned: {stats.files_scanned}")
    print(f"  New files added: {stats.new_files}")
    print(f"  Files updated: {stats.updated_files}")
    print(f"  Session word count: {stats.total_words:,}")
    
    print(f"\nProject Totals:")
    print(f"  Total files tracked: {len(rows)}")
    print(f"  Total words: {total_tracked_words:,}")
    if rows:
        print(f"  Average per file: {total_tracked_words // len(rows):,}")
    
    if goal:
        progress = (total_tracked_words / goal * 100) if goal > 0 else 0
        remaining = max(0, goal - total_tracked_words)
        print(f"\nGoal Progress:")
        print(f"  Target: {goal:,} words")
        print(f"  Progress: {total_tracked_words:,} / {goal:,} ({progress:.1f}%)")
        print(f"  Remaining: {remaining:,} words")
        
        if remaining > 0:
            # Simple velocity calc based on recent updates
            recent_dates = [r["Date Updated"] for r in rows.values() if r.get("Date Updated")]
            if recent_dates:
                days_active = len(set(recent_dates))
                if days_active > 0:
                    avg_per_day = total_tracked_words / days_active
                    days_needed = int(remaining / avg_per_day) if avg_per_day > 0 else 0
                    if days_needed > 0:
                        completion = datetime.now() + timedelta(days=days_needed)
                        print(f"  Estimated completion: {completion.strftime(DATE_FMT)}")
    
    if stats.errors:
        print(f"\nWarnings ({len(stats.errors)}):")
        for err in stats.errors[:5]:  # Show first 5 errors
            print(f"  - {err}")

# Main function
def main():
    parser = argparse.ArgumentParser(
        description="Track word counts for markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--drafts", default="drafts",
                       help="Folder with .md files (default: drafts)")
    parser.add_argument("--csv", default="word_count_tracker.csv",
                       help="Tracker CSV file (default: word_count_tracker.csv)")
    parser.add_argument("--recursive", action="store_true",
                       help="Include subfolders")
    parser.add_argument("--report", action="store_true",
                       help="Show detailed report")
    parser.add_argument("--goal", type=int,
                       help="Word count goal for progress tracking")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without saving")
    
    args = parser.parse_args()
    
    drafts_dir = Path(args.drafts)
    csv_path = Path(args.csv)
    
    # Initialize
    if not drafts_dir.exists():
        print(f"Error: Folder '{drafts_dir}' not found.")
        sys.exit(1)
    
    if not args.dry_run:
        ensure_tracker_exists(csv_path)
    
    tracker = load_tracker(csv_path) if csv_path.exists() else {}
    stats = Stats()
    
    # Find and process files
    md_files = find_markdown_files(drafts_dir, args.recursive)
    if not md_files:
        print("No markdown files found.")
        return
    
    stats.files_scanned = len(md_files)
    today_str = iso_date(datetime.now())
    
    # Process each file
    for path in md_files:
        filename = str(path.relative_to(drafts_dir)) if args.recursive else path.name
        
        try:
            text = read_markdown(path)
            word_count = count_words(text)
            stats.total_words += word_count
            
            if filename in tracker:
                # Update existing
                tracker[filename]["Word Count"] = str(word_count)
                tracker[filename]["Date Updated"] = today_str
                if not tracker[filename]["Date Created"]:
                    tracker[filename]["Date Created"] = file_created_date(path)
                stats.updated_files += 1
                action = "Updated"
            else:
                # Add new
                tracker[filename] = {
                    "Filename": filename,
                    "Word Count": str(word_count),
                    "Date Created": file_created_date(path),
                    "Date Updated": "",
                }
                stats.new_files += 1
                action = "Added"
            
            print(f"{action}: {filename} ({word_count:,} words)")
            
        except Exception as e:
            error_msg = f"Error with {filename}: {e}"
            stats.errors.append(error_msg)
            print(f"Warning: {error_msg}", file=sys.stderr)
    
    # Save results
    if not args.dry_run:
        save_tracker(csv_path, tracker)
        print(f"\n✅ Tracker saved: {csv_path.resolve()}")
    else:
        print("\n⚠️  DRY RUN - No changes saved")
    
    # Show report if requested
    if args.report:
        generate_report(tracker, stats, args.goal)
    else:
        print(f"\nSummary: {stats.files_scanned} files, "
              f"{stats.new_files} new, {stats.updated_files} updated")

if __name__ == "__main__":
    main()
