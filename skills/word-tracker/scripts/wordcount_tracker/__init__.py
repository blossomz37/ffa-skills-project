"""Word Count Tracker Package

A comprehensive word tracking system for authors and writers.
"""

__version__ = "2.0.0"
__author__ = "Word Tracker Skill"

from .scanner import find_markdown_files
from .counter import count_words, count_words_advanced
from .dates import file_created_date, iso_date
from .tracker import Row, ensure_tracker_exists, load_rows, save_rows, upsert_row

__all__ = [
    "find_markdown_files",
    "count_words",
    "count_words_advanced", 
    "file_created_date",
    "iso_date",
    "Row",
    "ensure_tracker_exists",
    "load_rows",
    "save_rows",
    "upsert_row",
]
