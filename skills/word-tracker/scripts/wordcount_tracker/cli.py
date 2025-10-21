# cli.py
# Purpose: command-line entry point that wires the modules together.

import argparse
import sys
from pathlib import Path
from typing import Optional

from .scanner import find_markdown_files
from .counter import count_words, count_words_advanced, get_reading_time
from .dates import file_created_date, extract_frontmatter_date
from .tracker import (
    Row, TrackerStats, ensure_tracker_exists, 
    load_rows, save_rows, upsert_row, get_tracker_summary
)

def read_text(path: Path) -> str:
    """Read file content as UTF-8 with a forgiving fallback."""
    return path.read_text(encoding="utf-8", errors="ignore")

def process_file(path: Path, 
                relative_to: Optional[Path] = None,
                use_frontmatter_date: bool = False,
                advanced_counting: bool = False) -> tuple[str, int, str]:
    """
    Process a single file and return (filename, word_count, date_created).
    
    Args:
        path: Path to the file
        relative_to: Base path for relative filename
        use_frontmatter_date: Whether to prefer frontmatter dates
        advanced_counting: Whether to use advanced word counting
    """
    # Determine filename
    filename = str(path.relative_to(relative_to)) if relative_to else path.name
    
    # Read and count words
    text = read_text(path)
    if advanced_counting:
        word_count = count_words_advanced(text)
    else:
        word_count = count_words(text)
    
    # Get creation date
    if use_frontmatter_date:
        date_created = extract_frontmatter_date(text) or file_created_date(path)
    else:
        date_created = file_created_date(path)
    
    return filename, word_count, date_created

def main() -> None:
    """Main entry point for the word count tracker."""
    parser = argparse.ArgumentParser(
        description="Track word counts for Markdown files in your writing projects.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --drafts drafts --csv tracker.csv
  %(prog)s --drafts novel/chapters --recursive
  %(prog)s --drafts . --report
  %(prog)s --drafts stories --advanced --frontmatter
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--drafts", 
        default="drafts", 
        help="Folder containing .md files (default: drafts)"
    )
    parser.add_argument(
        "--csv", 
        default="word_count_tracker.csv", 
        help="Tracker CSV path (default: word_count_tracker.csv)"
    )
    
    # Options
    parser.add_argument(
        "--recursive", 
        action="store_true", 
        help="Scan subfolders under drafts"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Show summary report after tracking"
    )
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Use advanced word counting (excludes frontmatter)"
    )
    parser.add_argument(
        "--frontmatter",
        action="store_true",
        help="Prefer dates from frontmatter when available"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup before updating tracker"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without saving changes"
    )
    
    args = parser.parse_args()
    
    drafts_dir = Path(args.drafts)
    csv_path = Path(args.csv)
    
    # Validate drafts directory
    if not drafts_dir.exists():
        print(f"Error: Folder '{drafts_dir}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Create or load tracker
    if not args.dry_run:
        ensure_tracker_exists(csv_path)
    
    rows = load_rows(csv_path) if csv_path.exists() else {}
    stats = TrackerStats()
    
    # Find markdown files
    files = list(find_markdown_files(drafts_dir, recursive=args.recursive))
    if not files:
        print("No markdown files found.")
        return
    
    stats.files_scanned = len(files)
    
    # Process each file
    for path in files:
        try:
            filename, word_count, date_created = process_file(
                path,
                relative_to=drafts_dir if args.recursive else None,
                use_frontmatter_date=args.frontmatter,
                advanced_counting=args.advanced
            )
            
            stats.total_words += word_count
            
            if filename in rows:
                if not args.dry_run:
                    upsert_row(rows, Row(filename, word_count, date_created), is_update=True)
                stats.updated_files += 1
                print(f"Updated: {filename} ({word_count:,} words)")
            else:
                if not args.dry_run:
                    upsert_row(rows, Row(filename, word_count, date_created), is_update=False)
                stats.new_files += 1
                print(f"Added: {filename} ({word_count:,} words)")
                
        except Exception as e:
            error_msg = f"Error processing {path}: {e}"
            stats.errors.append(error_msg)
            print(f"Warning: {error_msg}", file=sys.stderr)
    
    # Save changes
    if not args.dry_run:
        if args.backup and csv_path.exists():
            from .tracker import backup_tracker
            backup_path = backup_tracker(csv_path)
            if backup_path:
                print(f"Backup created: {backup_path}")
        
        save_rows(csv_path, rows)
    
    # Display summary
    print("\n" + "=" * 50)
    if args.dry_run:
        print("DRY RUN - No changes were saved")
    else:
        print(f"Tracker updated: {csv_path.resolve()}")
    
    print(f"Files scanned: {stats.files_scanned}")
    print(f"New files: {stats.new_files}")
    print(f"Updated files: {stats.updated_files}")
    print(f"Total words: {stats.total_words:,}")
    
    if stats.total_words > 0:
        reading_time = get_reading_time(stats.total_words)
        print(f"Reading time: {reading_time}")
    
    if stats.errors:
        print(f"\nWarnings: {len(stats.errors)} files had errors")
    
    # Show report if requested
    if args.report and not args.dry_run:
        summary = get_tracker_summary(rows)
        print("\n" + "=" * 50)
        print("PROJECT SUMMARY")
        print(f"Total files tracked: {summary['total_files']}")
        print(f"Total words: {summary['total_words']:,}")
        print(f"Average words per file: {summary['average_words']:,}")
        if summary['oldest_file']:
            print(f"Project started: {summary['oldest_file']}")
        if summary['newest_file']:
            print(f"Last updated: {summary['newest_file']}")

if __name__ == "__main__":
    main()
