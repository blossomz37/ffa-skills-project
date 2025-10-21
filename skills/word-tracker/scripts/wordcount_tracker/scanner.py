# scanner.py
# Purpose: discover Markdown files under a root directory.

from pathlib import Path
from typing import Iterable, List, Set

def find_markdown_files(root: Path, recursive: bool = False) -> Iterable[Path]:
    """
    Return Markdown files under `root`.
    - If `recursive` is True, includes subfolders via rglob.
    """
    pattern = "**/*.md" if recursive else "*.md"
    return (p for p in root.glob(pattern) if p.is_file())

def find_files_by_extension(root: Path, extensions: List[str], recursive: bool = False) -> Iterable[Path]:
    """
    Find files with specified extensions.
    
    Args:
        root: Root directory to search
        extensions: List of extensions (e.g., ['.md', '.txt'])
        recursive: Whether to search subdirectories
    """
    for ext in extensions:
        pattern = f"**/*{ext}" if recursive else f"*{ext}"
        for p in root.glob(pattern):
            if p.is_file():
                yield p

def exclude_patterns(files: Iterable[Path], patterns: List[str]) -> Iterable[Path]:
    """
    Filter out files matching exclusion patterns.
    
    Args:
        files: Iterable of file paths
        patterns: List of glob patterns to exclude
    """
    exclude_set: Set[Path] = set()
    for pattern in patterns:
        for file in files:
            if file.match(pattern):
                exclude_set.add(file)
    
    for file in files:
        if file not in exclude_set:
            yield file
