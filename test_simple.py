#!/usr/bin/env python3
"""Simple test for content-digest CLI."""

import subprocess
import sys

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def run_test(name: str, command: list) -> bool:
    """Run a test command and report result."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print('='*60)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"{GREEN}✓ PASSED{RESET}")
        print(f"Output:\n{result.stdout}")
        return True
    else:
        print(f"{RED}✗ FAILED{RESET}")
        print(f"Error:\n{result.stderr}")
        return False

def main():
    """Run all tests."""
    print(f"\n{GREEN}Content Digest CLI — Test Suite{RESET}\n")

    # Test 1: Help command
    run_test("Help command", ['python3', 'content-digest.py', '--help'])

    # Test 2: Scan non-existent directory
    run_test("Scan non-existent directory", ['python3', 'content-digest.py', 'scan', '/nonexistent/directory'])

    print(f"\n{GREEN}Test complete!{RESET}")
    print("Note: Full integration testing requires actual research files with tweet drafts and blog angles.")
    print("Usage examples:")
    print("  content-digest scan ~/.openclaw/learnings/")
    print("  content-digest extract ~/.openclaw/learnings/ digest.json")
    print("  content-digest compile ~/.openclaw/learnings/ daily-digest-2026-02-28.md")

if __name__ == '__main__':
    main()
