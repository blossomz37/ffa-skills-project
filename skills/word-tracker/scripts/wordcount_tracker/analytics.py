# analytics.py
# Purpose: Generate writing statistics and progress reports

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import csv

from .tracker import Row, load_rows
from .dates import DATE_FMT, parse_date, date_range, week_start_date

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
    
    def __post_init__(self):
        """Calculate daily target if not provided."""
        if not self.daily_target and self.deadline:
            days_left = (datetime.strptime(self.deadline, DATE_FMT) - datetime.now()).days
            if days_left > 0:
                self.daily_target = self.target_words // days_left

def calculate_daily_progress(rows: Dict[str, Row]) -> Dict[str, WritingSession]:
    """
    Calculate words written per day based on update dates.
    Note: This is approximate as we don't store historical word counts.
    """
    sessions: Dict[str, WritingSession] = {}
    
    for row in rows.values():
        if row.date_updated:
            date = row.date_updated
            if date not in sessions:
                sessions[date] = WritingSession(date, 0, 0)
            sessions[date].words_written += row.word_count
            sessions[date].files_modified += 1
    
    return sessions

def get_writing_streak(sessions: Dict[str, WritingSession]) -> int:
    """Calculate current consecutive days of writing."""
    if not sessions:
        return 0
    
    dates = sorted(sessions.keys(), reverse=True)
    today = datetime.now().date()
    streak = 0
    
    for date_str in dates:
        date = datetime.strptime(date_str, DATE_FMT).date()
        expected = today - timedelta(days=streak)
        
        if date == expected:
            streak += 1
        elif date < expected:
            break
    
    return streak

def calculate_velocity(sessions: Dict[str, WritingSession], days: int = 7) -> float:
    """Calculate average words per day over recent period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    total_words = 0
    for date_str, session in sessions.items():
        date = datetime.strptime(date_str, DATE_FMT)
        if start_date <= date <= end_date:
            total_words += session.words_written
    
    return total_words / days if days > 0 else 0

def project_completion(current_words: int, goal: WritingGoal, velocity: float) -> Optional[str]:
    """Project completion date based on current velocity."""
    if velocity <= 0:
        return None
    
    words_remaining = goal.target_words - current_words
    if words_remaining <= 0:
        return "Complete!"
    
    days_needed = int(words_remaining / velocity)
    completion_date = datetime.now() + timedelta(days=days_needed)
    
    return completion_date.strftime(DATE_FMT)

def generate_progress_report(csv_path: Path, 
                            goal: Optional[WritingGoal] = None,
                            period_days: int = 7) -> str:
    """Generate a comprehensive progress report."""
    rows = load_rows(csv_path)
    if not rows:
        return "No tracking data found."
    
    # Calculate statistics
    total_words = sum(r.word_count for r in rows.values())
    sessions = calculate_daily_progress(rows)
    streak = get_writing_streak(sessions)
    velocity = calculate_velocity(sessions, period_days)
    
    # Build report
    lines = [
        "=" * 50,
        "WRITING PROGRESS REPORT",
        "=" * 50,
        f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "PROJECT STATISTICS",
        "-" * 20,
        f"Total Files: {len(rows)}",
        f"Total Words: {total_words:,}",
        f"Average per File: {total_words // len(rows):,}" if rows else "Average per File: 0",
        "",
        f"RECENT ACTIVITY (Last {period_days} days)",
        "-" * 20,
        f"Writing Velocity: {velocity:.0f} words/day",
        f"Current Streak: {streak} days",
    ]
    
    # Recent sessions
    recent_sessions = sorted(
        [(k, v) for k, v in sessions.items()],
        key=lambda x: x[0],
        reverse=True
    )[:5]
    
    if recent_sessions:
        lines.extend([
            "",
            "Recent Writing Sessions:",
        ])
        for date, session in recent_sessions:
            lines.append(f"  {date}: {session.words_written:,} words ({session.files_modified} files)")
    
    # Goal progress
    if goal:
        progress_pct = (total_words / goal.target_words * 100) if goal.target_words > 0 else 0
        projected = project_completion(total_words, goal, velocity)
        
        lines.extend([
            "",
            "GOAL TRACKING",
            "-" * 20,
            f"Target: {goal.target_words:,} words",
            f"Progress: {total_words:,} / {goal.target_words:,} ({progress_pct:.1f}%)",
            f"Remaining: {max(0, goal.target_words - total_words):,} words",
            f"Daily Target: {goal.daily_target:,} words",
            f"Deadline: {goal.deadline}",
        ])
        
        if projected:
            lines.append(f"Projected Completion: {projected}")
            if projected != "Complete!" and goal.deadline:
                proj_date = datetime.strptime(projected, DATE_FMT)
                dead_date = datetime.strptime(goal.deadline, DATE_FMT)
                if proj_date > dead_date:
                    days_behind = (proj_date - dead_date).days
                    lines.append(f"⚠️  Behind schedule by {days_behind} days")
                else:
                    days_ahead = (dead_date - proj_date).days
                    lines.append(f"✅ Ahead of schedule by {days_ahead} days")
    
    lines.append("=" * 50)
    
    return "\n".join(lines)

def export_to_json(rows: Dict[str, Row], output_path: Path) -> None:
    """Export tracking data to JSON format."""
    import json
    
    data = {
        "export_date": datetime.now().isoformat(),
        "total_files": len(rows),
        "total_words": sum(r.word_count for r in rows.values()),
        "files": [
            {
                "filename": r.filename,
                "word_count": r.word_count,
                "date_created": r.date_created,
                "date_updated": r.date_updated,
            }
            for r in rows.values()
        ]
    }
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
