---
name: word-tracker-reference
description: Detailed API reference and advanced usage for the word-tracker skill
---

# Word Tracker - Detailed Reference

## Package Structure

The word tracker provides both a modular package and standalone script:

```
scripts/
├── word_tracker_standalone.py    # Single-file solution
└── wordcount_tracker/            # Full package
    ├── __init__.py
    ├── cli.py                    # Command-line interface
    ├── scanner.py                # File discovery
    ├── counter.py                # Word counting algorithms
    ├── dates.py                  # Date handling
    ├── tracker.py                # CSV management
    └── analytics.py              # Reports & statistics
```

## Module Reference

### scanner.py - File Discovery

```python
def find_markdown_files(root: Path, recursive: bool = False) -> Iterable[Path]
    """Find all markdown files in directory."""

def find_files_by_extension(root: Path, extensions: List[str], recursive: bool = False) -> Iterable[Path]
    """Find files with specified extensions."""

def exclude_patterns(files: Iterable[Path], patterns: List[str]) -> Iterable[Path]
    """Filter out files matching exclusion patterns."""
```

### counter.py - Word Counting Algorithms

```python
def count_words(text: str) -> int
    """Basic word counting using regex."""

def count_words_advanced(text: str, exclude_frontmatter: bool = True,
                        exclude_code_blocks: bool = False,
                        include_hyphenated: bool = True) -> int
    """Advanced counting with various options."""

def count_manuscript_words(text: str) -> int
    """Industry-standard manuscript word count (characters/6)."""

def get_reading_time(word_count: int, wpm: int = 250) -> str
    """Calculate estimated reading time."""
```

### dates.py - Date Handling

```python
def file_created_date(path: Path) -> str
    """Get file creation date (cross-platform)."""

def file_modified_date(path: Path) -> str
    """Get file modification date."""

def extract_frontmatter_date(text: str) -> Optional[str]
    """Extract date from YAML frontmatter."""

def date_range(start_date: str, end_date: str) -> list[str]
    """Generate list of dates between start and end."""
```

### tracker.py - CSV Management

```python
@dataclass
class Row:
    filename: str
    word_count: int
    date_created: str
    date_updated: str = ""

def ensure_tracker_exists(csv_path: Path) -> None
def load_rows(csv_path: Path) -> Dict[str, Row]
def save_rows(csv_path: Path, rows: Dict[str, Row]) -> None
def upsert_row(rows: Dict[str, Row], new_row: Row, is_update: bool) -> None
def backup_tracker(csv_path: Path) -> Optional[Path]
def get_tracker_summary(rows: Dict[str, Row]) -> Dict[str, any]
```

### analytics.py - Reporting

```python
@dataclass
class WritingSession:
    date: str
    words_written: int
    files_modified: int

@dataclass
class WritingGoal:
    target_words: int
    deadline: str
    daily_target: int = 0

def calculate_daily_progress(rows: Dict[str, Row]) -> Dict[str, WritingSession]
def get_writing_streak(sessions: Dict[str, WritingSession]) -> int
def calculate_velocity(sessions: Dict[str, WritingSession], days: int = 7) -> float
def project_completion(current_words: int, goal: WritingGoal, velocity: float) -> Optional[str]
def generate_progress_report(csv_path: Path, goal: Optional[WritingGoal] = None, period_days: int = 7) -> str
def export_to_json(rows: Dict[str, Row], output_path: Path) -> None
```

## Command-Line Arguments

### Basic Arguments
- `--drafts PATH`: Directory containing markdown files (default: "drafts")
- `--csv PATH`: CSV file for tracking (default: "word_count_tracker.csv")

### Options
- `--recursive`: Include subdirectories
- `--report`: Show detailed progress report
- `--advanced`: Use advanced word counting (excludes frontmatter)
- `--frontmatter`: Prefer dates from YAML frontmatter
- `--backup`: Create backup before updating
- `--dry-run`: Preview changes without saving
- `--goal NUMBER`: Set word count goal for progress tracking

## CSV Format

The tracker CSV uses this schema:

```csv
Filename,Word Count,Date Created,Date Updated
chapter_01.md,2341,2024-10-01,2024-10-21
chapter_02.md,1856,2024-10-02,2024-10-21
chapter_03.md,2103,2024-10-03,
```

- **Filename**: Relative path from drafts directory
- **Word Count**: Current word count
- **Date Created**: YYYY-MM-DD format (from filesystem or frontmatter)
- **Date Updated**: YYYY-MM-DD when last modified (blank for new files)

## Advanced Usage Examples

### Custom Word Counting

```python
from scripts.wordcount_tracker.counter import count_words_advanced

# Exclude frontmatter and code blocks
text = open("manuscript.md").read()
words = count_words_advanced(
    text,
    exclude_frontmatter=True,
    exclude_code_blocks=True,
    include_hyphenated=True
)
```

### Programmatic Progress Tracking

```python
from pathlib import Path
from scripts.wordcount_tracker.tracker import load_rows, get_tracker_summary
from scripts.wordcount_tracker.analytics import generate_progress_report, WritingGoal

# Load existing tracking data
csv_path = Path("word_count_tracker.csv")
rows = load_rows(csv_path)

# Get summary
summary = get_tracker_summary(rows)
print(f"Total words: {summary['total_words']:,}")

# Generate report with goal
goal = WritingGoal(
    target_words=70000,
    deadline="2024-12-31"
)
report = generate_progress_report(csv_path, goal, period_days=7)
print(report)
```

### Batch Processing Multiple Projects

```python
#!/usr/bin/env python3
from pathlib import Path
from scripts.wordcount_tracker import cli

projects = [
    {"name": "novel", "path": "novel/chapters"},
    {"name": "stories", "path": "short_stories"},
    {"name": "blog", "path": "blog_posts"},
]

for project in projects:
    print(f"\nProcessing {project['name']}...")
    csv_file = f"{project['name']}_tracker.csv"
    
    # Run tracking for each project
    import sys
    sys.argv = [
        "cli.py",
        "--drafts", project["path"],
        "--csv", csv_file,
        "--recursive",
        "--report"
    ]
    cli.main()
```

## Configuration File Support

Create a `wordtracker.yaml` for project settings:

```yaml
# wordtracker.yaml
drafts_dir: manuscripts/drafts
csv_path: project_tracker.csv
recursive: true

exclude_patterns:
  - "*.backup.md"
  - "notes/*"
  - "_archive/*"

word_count:
  method: advanced
  exclude_frontmatter: true
  exclude_code_blocks: true
  include_hyphenated: true

goals:
  daily: 1000
  weekly: 5000
  project: 70000
  deadline: 2024-12-31

reporting:
  show_streak: true
  show_velocity: true
  velocity_days: 14
```

Load configuration:

```python
import yaml
from pathlib import Path

def load_config(config_path="wordtracker.yaml"):
    if Path(config_path).exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
drafts_dir = config.get("drafts_dir", "drafts")
```

## Integration Examples

### Git Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python scripts/word_tracker_standalone.py --drafts drafts
git add word_count_tracker.csv
```

### Daily Cron Job

```bash
# Add to crontab -e
0 9 * * * cd /path/to/project && python scripts/word_tracker_standalone.py --report >> writing_log.txt
```

### VS Code Task

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Update Word Count",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/scripts/word_tracker_standalone.py",
        "--drafts", "${workspaceFolder}/drafts",
        "--report"
      ],
      "problemMatcher": []
    }
  ]
}
```

## Performance Optimization

### Large Projects (1000+ files)

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def parallel_word_count(files, max_workers=4):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_file, files)
    return list(results)
```

### Incremental Updates

Only process files modified since last run:

```python
def get_modified_files(directory, since_date):
    cutoff = datetime.strptime(since_date, DATE_FMT)
    for path in Path(directory).glob("**/*.md"):
        if datetime.fromtimestamp(path.stat().st_mtime) > cutoff:
            yield path
```

## Troubleshooting

### Common Issues and Solutions

1. **Encoding Errors**
   ```python
   text = path.read_text(encoding='utf-8', errors='replace')
   ```

2. **Permission Errors**
   ```python
   try:
       text = path.read_text()
   except PermissionError:
       print(f"Skipping {path}: Permission denied")
   ```

3. **Large Files (>10MB)**
   ```python
   def read_large_file(path, chunk_size=1024*1024):
       with open(path, 'r', encoding='utf-8') as f:
           while chunk := f.read(chunk_size):
               yield chunk
   ```

4. **Memory Issues**
   Use generators instead of lists:
   ```python
   # Bad - loads all files into memory
   files = list(Path("drafts").glob("**/*.md"))
   
   # Good - processes one at a time
   for file in Path("drafts").glob("**/*.md"):
       process_file(file)
   ```

## API Usage

```python
from scripts.wordcount_tracker import (
    find_markdown_files,
    count_words,
    Row,
    ensure_tracker_exists,
    load_rows,
    save_rows,
    upsert_row
)

# Complete workflow
drafts_dir = Path("my_novel")
csv_path = Path("novel_tracker.csv")

ensure_tracker_exists(csv_path)
rows = load_rows(csv_path)

for md_file in find_markdown_files(drafts_dir, recursive=True):
    text = md_file.read_text(errors='ignore')
    words = count_words(text)
    
    row = Row(
        filename=md_file.name,
        word_count=words,
        date_created=file_created_date(md_file)
    )
    
    is_update = row.filename in rows
    upsert_row(rows, row, is_update)

save_rows(csv_path, rows)
```
