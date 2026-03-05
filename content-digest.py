#!/usr/bin/env python3
"""
Content Digest CLI — Research-to-Content Pipeline

Scans Marcus/Galen research outputs, extracts tweet drafts and blog angles,
compiles a daily digest for Seneca.

Usage:
    content-digest scan <directory>              # Scan directory for research files
    content-digest extract <directory> <output>   # Extract tweet drafts and blog angles
    content-digest compile <directory> <output>    # Compile daily digest

Example:
    content-digest scan ~/.openclaw/learnings/
    content-digest extract ~/.openclaw/learnings/ digest.md
    content-digest compile ~/.openclaw/learnings/ daily-digest-2026-02-28.md
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log_info(message: str) -> None:
    """Print informational message."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")


def log_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def log_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def log_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {message}", file=sys.stderr)


def get_file_age(file_path: Path) -> str:
    """Calculate human-readable file age."""
    if not file_path.exists():
        return "N/A"

    mtime = file_path.stat().st_mtime
    age = datetime.now() - datetime.fromtimestamp(mtime)

    if age.days > 0:
        return f"{age.days}d ago"
    elif age.seconds > 3600:
        hours = age.seconds // 3600
        return f"{hours}h ago"
    else:
        minutes = age.seconds // 60
        return f"{minutes}m ago"


def scan_directory(directory: Path) -> List[Path]:
    """Scan directory for markdown research files."""
    if not directory.exists():
        log_error(f"Directory does not exist: {directory}")
        return []

    research_files = []
    md_files = list(directory.glob('*.md'))

    for md_file in md_files:
        # Skip if name matches this script or test files
        if md_file.name.startswith('content-digest') or md_file.name.startswith('test'):
            continue

        # Read file and check for research content
        try:
            content = md_file.read_text()
            # Check for common research patterns
            has_research_content = any(pattern in content.lower() for pattern in [
                '## key findings',
                '## methodology',
                '## research',
                '## findings',
                'tweet draft:',
                'blog angle:',
                'signup:'
            ])

            if has_research_content:
                research_files.append(md_file)

        except Exception as e:
            log_warning(f"Failed to read {md_file.name}: {e}")

    log_success(f"Found {len(research_files)} research file(s) in {directory}")
    return research_files


def extract_content(directory: Path) -> Dict[str, Dict[str, List[str]]]:
    """Extract tweet drafts and blog angles from research files."""
    research_files = scan_directory(directory)

    if not research_files:
        log_warning("No research files found")
        return {}

    extracted = {
        'tweet_drafts': {},
        'blog_angles': {},
        'signup_links': {},
        'summaries': {}
    }

    for md_file in research_files:
        try:
            content = md_file.read_text()

            # Extract tweet drafts (matches lines starting with "Tweet Draft:" or "Tweet Drafts:")
            tweet_pattern = r'^Tweet Drafts?:\s*(.+)$'
            tweets = re.findall(tweet_pattern, content, re.IGNORECASE | re.MULTILINE)
            for tweet in tweets:
                tweet_text = tweet.strip()
                if tweet_text and len(tweet_text) > 0:
                    agent_name = md_file.name.split('-')[0] if '-' in md_file.name else md_file.stem
                    if agent_name not in extracted['tweet_drafts']:
                        extracted['tweet_drafts'][agent_name] = []
                    extracted['tweet_drafts'][agent_name].append({
                        'file': md_file.name,
                        'tweet': tweet_text,
                        'date': get_file_age(md_file)
                    })

            # Extract blog angles
            blog_pattern = r'^Blog Angle:\s*(.+)$'
            angles = re.findall(blog_pattern, content, re.IGNORECASE | re.MULTILINE)
            for angle in angles:
                angle_text = angle.strip()
                if angle_text and len(angle_text) > 0:
                    agent_name = md_file.name.split('-')[0] if '-' in md_file.name else md_file.stem
                    if agent_name not in extracted['blog_angles']:
                        extracted['blog_angles'][agent_name] = []
                    extracted['blog_angles'][agent_name].append({
                        'file': md_file.name,
                        'angle': angle_text,
                        'date': get_file_age(md_file)
                    })

            # Extract signup links
            signup_pattern = r'^SIGNUP:\s*(.+)$'
            signups = re.findall(signup_pattern, content, re.IGNORECASE | re.MULTILINE)
            for signup in signups:
                signup_text = signup.strip()
                if signup_text and len(signup_text) > 0:
                    agent_name = md_file.name.split('-')[0] if '-' in md_file.name else md_file.stem
                    if agent_name not in extracted['signup_links']:
                        extracted['signup_links'][agent_name] = []
                    extracted['signup_links'][agent_name].append({
                        'file': md_file.name,
                        'signup': signup_text,
                        'date': get_file_age(md_file)
                    })

            # Extract summaries
            summary_patterns = [
                r'## Executive Summary[:](.+?)\n',
                r'## Key Findings[:](.+?)\n',
                r'## Summary[:](.+?)\n'
            ]

            for pattern in summary_patterns:
                summaries = re.findall(pattern, content)
                for summary in summaries:
                    summary_text = summary.strip()
                    if summary_text and len(summary_text) > 10:
                        agent_name = md_file.name.split('-')[0] if '-' in md_file.name else md_file.stem
                        if agent_name not in extracted['summaries']:
                            extracted['summaries'][agent_name] = []
                        extracted['summaries'][agent_name].append({
                            'file': md_file.name,
                            'summary': summary_text[:200],  # Truncate long summaries
                            'date': get_file_age(md_file)
                        })

        except Exception as e:
            log_warning(f"Failed to extract from {md_file.name}: {e}")

    # Log extraction results
    total_tweets = sum(len(tweets) for tweets in extracted['tweet_drafts'].values())
    total_angles = sum(len(angles) for angles in extracted['blog_angles'].values())
    total_signups = sum(len(signups) for signups in extracted['signup_links'].values())

    log_success(f"Extracted: {total_tweets} tweet drafts, {total_angles} blog angles, {total_signups} signup links")

    return extracted


def compile_digest(directory: Path, output_file: Path) -> bool:
    """Compile daily digest for Seneca."""
    extracted = extract_content(directory)

    if not extracted:
        return False

    # Create digest content
    digest_lines = []
    date_str = datetime.now().strftime("%B %d, %Y")

    digest_lines.append(f"# Squad Research Digest — {date_str}\n")
    digest_lines.append(f"Compiled by content-digest CLI\n")
    digest_lines.append(f"Source directory: `{directory}`\n")
    digest_lines.append("\n---\n")

    # Tweet Drafts section
    if extracted['tweet_drafts']:
        digest_lines.append("## 🐦 Tweet Drafts\n")
        for agent, tweets in extracted['tweet_drafts'].items():
            digest_lines.append(f"\n### {agent.title()}\n")
            for tweet in tweets:
                tweet_preview = tweet['tweet'][:100] + "..." if len(tweet['tweet']) > 100 else tweet['tweet']
                digest_lines.append(f"- {tweet_preview} ({tweet['date']}, from {tweet['file']})")
        digest_lines.append("\n")

    # Blog Angles section
    if extracted['blog_angles']:
        digest_lines.append("## ✍️ Blog Angles\n")
        for agent, angles in extracted['blog_angles'].items():
            digest_lines.append(f"\n### {agent.title()}\n")
            for angle in angles:
                angle_preview = angle['angle'][:150] + "..." if len(angle['angle']) > 150 else angle['angle']
                digest_lines.append(f"- {angle_preview} ({angle['date']}, from {angle['file']})")
        digest_lines.append("\n")

    # Signup Links section
    if extracted['signup_links']:
        digest_lines.append("## 🔗 Signup Links\n")
        for agent, signups in extracted['signup_links'].items():
            digest_lines.append(f"\n### {agent.title()}\n")
            for signup in signups:
                signup_preview = signup['signup'][:80] + "..." if len(signup['signup']) > 80 else signup['signup']
                digest_lines.append(f"- {signup_preview} ({signup['date']}, from {signup['file']})")
        digest_lines.append("\n")

    # Summary section
    total_items = (
        sum(len(tweets) for tweets in extracted['tweet_drafts'].values()) +
        sum(len(angles) for angles in extracted['blog_angles'].values()) +
        sum(len(signups) for signups in extracted['signup_links'].values())
    )

    digest_lines.append("---\n")
    digest_lines.append(f"## 📊 Summary\n")
    digest_lines.append(f"- Total files scanned: {len(scan_directory(directory))}")
    digest_lines.append(f"- Tweet drafts: {sum(len(tweets) for tweets in extracted['tweet_drafts'].values())}")
    digest_lines.append(f"- Blog angles: {sum(len(angles) for angles in extracted['blog_angles'].values())}")
    digest_lines.append(f"- Signup links: {sum(len(signups) for signups in extracted['signup_links'].values())}")
    digest_lines.append(f"- Total actionable items: {total_items}")
    digest_lines.append(f"\nCompiled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Write digest to file
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text('\n'.join(digest_lines))
        log_success(f"Digest compiled: {output_file}")
        return True
    except Exception as e:
        log_error(f"Failed to write digest: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Content Digest CLI — Research-to-Content Pipeline for Seneca',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  content-digest scan ~/.openclaw/learnings/
  content-digest extract ~/.openclaw/learnings/ digest.md
  content-digest compile ~/.openclaw/learnings/ daily-digest-2026-02-28.md

This tool compiles daily research digests from Marcus/Galen outputs for Seneca.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan directory for research files')
    scan_parser.add_argument('directory', help='Path to directory containing research files')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract tweet drafts and blog angles')
    extract_parser.add_argument('directory', help='Path to directory containing research files')
    extract_parser.add_argument('output', help='Output file path (default: digest.md)', nargs='?', default='digest.md')

    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile daily digest')
    compile_parser.add_argument('directory', help='Path to directory containing research files')
    compile_parser.add_argument('output', help='Output digest file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Resolve directory path
    dir_path = Path(args.directory).expanduser()

    if not dir_path.exists():
        log_error(f"Directory does not exist: {dir_path}")
        return 1

    # Execute command
    success = False
    if args.command == 'scan':
        scan_directory(dir_path)
        success = True
    elif args.command == 'extract':
        output_path = Path(args.output).expanduser()
        extract_content(dir_path)
        if args.output != 'digest.md':
            # Save to JSON if specified output
            try:
                with open(output_path, 'w') as f:
                    json.dump(extract_content(dir_path), f, indent=2)
                log_success(f"Extracted to JSON: {output_path}")
                success = True
            except Exception as e:
                log_error(f"Failed to write JSON: {e}")
                success = False
        else:
            # Save to markdown by default
            extracted = extract_content(dir_path)
            if extracted:
                success = True

    elif args.command == 'compile':
        output_path = Path(args.output).expanduser()
        success = compile_digest(dir_path, output_path)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
