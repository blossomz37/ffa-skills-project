# Word Count Tracker Package

A professional word counting and tracking system for authors and writers.

## Installation

1. Clone or download this package
2. Place it in your project directory
3. Run: `python -m wordcount_tracker.cli --help`

## Quick Start

```bash
# Basic usage - scan drafts folder
python -m wordcount_tracker.cli --drafts drafts --csv word_count_tracker.csv

# Include subfolders
python -m wordcount_tracker.cli --drafts drafts --csv tracker.csv --recursive

# Generate report
python -m wordcount_tracker.cli --drafts drafts --report
```

## Features

- Track word counts across multiple markdown files
- Monitor writing progress over time
- CSV-based tracking for version control compatibility
- Support for recursive directory scanning
- Date tracking (creation and update dates)
- Cross-platform compatibility (macOS, Windows, Linux)

## Package Structure

```
wordcount_tracker/
  __init__.py      # Package initialization
  cli.py           # Command-line interface
  scanner.py       # File discovery
  counter.py       # Word counting logic
  dates.py         # Date handling
  tracker.py       # CSV management
  analytics.py     # Statistics and reporting (optional)
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## License

MIT License - Use freely in your projects

## Author

Created for fiction authors and professional writers who need reliable word count tracking.
