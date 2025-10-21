# counter.py
# Purpose: provide consistent word-count functions with various algorithms.

import re
from typing import Optional

# Basic word pattern - alphanumeric sequences
_WORD_RE = re.compile(r"\b\w+\b")

# More sophisticated patterns for different use cases
_WORD_HYPHEN_RE = re.compile(r"\b[\w'-]+\b")  # Includes hyphenated words
_WORD_NO_NUMBERS_RE = re.compile(r"\b[a-zA-Z]+\b")  # Excludes numbers

def count_words(text: str) -> int:
    """
    Count 'words' by a simple regex heuristic.
    Keeping it isolated lets you swap in a different approach later.
    """
    return len(_WORD_RE.findall(text))

def count_words_advanced(text: str, 
                        exclude_frontmatter: bool = True,
                        exclude_code_blocks: bool = False,
                        include_hyphenated: bool = True) -> int:
    """
    Advanced word counting with various options.
    
    Args:
        text: The text to count words in
        exclude_frontmatter: Skip YAML frontmatter if present
        exclude_code_blocks: Skip markdown code blocks
        include_hyphenated: Count hyphenated words correctly
    """
    # Handle frontmatter
    if exclude_frontmatter and text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    
    # Handle code blocks
    if exclude_code_blocks:
        # Remove fenced code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)
    
    # Choose word pattern
    if include_hyphenated:
        return len(_WORD_HYPHEN_RE.findall(text))
    else:
        return len(_WORD_RE.findall(text))

def count_manuscript_words(text: str) -> int:
    """
    Count words using manuscript format standards.
    Industry standard often uses: (characters with spaces) / 6
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Some publishers use character count / 6
    return len(text) // 6

def get_reading_time(word_count: int, wpm: int = 250) -> str:
    """
    Calculate estimated reading time.
    
    Args:
        word_count: Number of words
        wpm: Words per minute (default 250 for average reader)
    
    Returns:
        Formatted string like "5 min read" or "1 hr 30 min"
    """
    minutes = word_count / wpm
    if minutes < 60:
        return f"{int(minutes)} min read"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins > 0:
            return f"{hours} hr {mins} min"
        else:
            return f"{hours} hr"
