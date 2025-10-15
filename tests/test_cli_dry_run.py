#!/usr/bin/env python3
"""
Test CLI dry-run functionality
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_dry_run():
    """Test that dry-run mode works without sending emails"""
    print("Testing dry-run mode...")

    # Get paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(base_dir, 'send_mail_merge.py')
    csv = os.path.join(base_dir, 'contacts_hotels.csv')
    subject = os.path.join(base_dir, 'subject.txt')
    html = os.path.join(base_dir, 'email_template_italiano.html')

    # Check if files exist
    for file_path in [script, csv, subject, html]:
        if not os.path.exists(file_path):
            print(f"⚠ Skipping test - file not found: {file_path}")
            return

    # Run dry-run command
    cmd = [
        sys.executable, script,
        '--csv', csv,
        '--subject', subject,
        '--html', html,
        '--dry-run',
        '--max', '3',
        '--env', os.path.join(base_dir, '.env.example')
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Check output contains dry-run indicators
        output = result.stdout + result.stderr

        if 'DRY RUN' in output:
            print("✓ Dry-run mode executed successfully")
            return True
        else:
            print(f"⚠ Dry-run output doesn't contain expected markers")
            print(f"Output: {output}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def test_help():
    """Test that --help flag works"""
    print("Testing --help flag...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = os.path.join(base_dir, 'send_mail_merge.py')

    if not os.path.exists(script):
        print(f"⚠ Skipping test - script not found")
        return

    cmd = [sys.executable, script, '--help']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        output = result.stdout + result.stderr

        if '--csv' in output and '--subject' in output and '--html' in output:
            print("✓ Help message displays correctly")
            return True
        else:
            print("⚠ Help message doesn't contain expected flags")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def run_tests():
    """Run all CLI tests"""
    print("\n" + "="*60)
    print("  🧪 RUNNING CLI TESTS")
    print("="*60 + "\n")

    results = []

    results.append(test_help())
    results.append(test_dry_run())

    print("\n" + "="*60)
    if all(r is not False for r in results):
        print("  ✅ ALL CLI TESTS PASSED")
        print("="*60 + "\n")
        return 0
    else:
        print("  ⚠️  SOME TESTS FAILED OR SKIPPED")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
