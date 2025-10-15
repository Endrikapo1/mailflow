#!/usr/bin/env python3
"""
Test template rendering functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from send_mail_merge import render_template, html_to_plain_text


def test_render_template():
    """Test that placeholders are replaced correctly"""
    print("Testing template rendering...")

    template = "Hello {{name}}, welcome to {{city}}!"
    context = {
        'name': 'Mario Rossi',
        'city': 'Milano'
    }

    result = render_template(template, context)
    expected = "Hello Mario Rossi, welcome to Milano!"

    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Template rendering works correctly")


def test_html_to_plain_text():
    """Test HTML to plain text conversion"""
    print("Testing HTML to plain text conversion...")

    html = """
    <html>
        <body>
            <h1>Title</h1>
            <p>This is a paragraph.</p>
            <p>Another paragraph with <strong>bold text</strong>.</p>
            <br>
            <p>Final paragraph.</p>
        </body>
    </html>
    """

    result = html_to_plain_text(html)

    # Check that HTML tags are removed
    assert '<html>' not in result
    assert '<body>' not in result
    assert '<h1>' not in result
    assert '<p>' not in result
    assert '<strong>' not in result

    # Check that text content is preserved
    assert 'Title' in result
    assert 'This is a paragraph.' in result
    assert 'bold text' in result
    assert 'Final paragraph.' in result

    print("✓ HTML to plain text conversion works correctly")


def test_multiple_placeholders():
    """Test template with multiple occurrences of same placeholder"""
    print("Testing multiple placeholder occurrences...")

    template = "{{name}} is from {{city}}. {{name}} loves {{city}}!"
    context = {
        'name': 'Luigi',
        'city': 'Roma'
    }

    result = render_template(template, context)
    expected = "Luigi is from Roma. Luigi loves Roma!"

    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Multiple placeholder occurrences work correctly")


def test_email_template():
    """Test actual email template rendering"""
    print("Testing email template rendering...")

    # Read actual template
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_template_italiano.html')
    if not os.path.exists(template_path):
        print("⚠ Skipping email template test - file not found")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    context = {
        'contact_name': 'Marco Bianchi',
        'hotel_name': 'Hotel Test',
        'city': 'Torino',
        'sender_name': 'Gonzalo Medrano Ortiz',
        'today': '10/05/2025'
    }

    result = render_template(template, context)

    # Verify all placeholders are replaced
    assert '{{contact_name}}' not in result
    assert '{{hotel_name}}' not in result
    assert '{{city}}' not in result
    assert '{{sender_name}}' not in result
    assert '{{today}}' not in result

    # Verify values are present
    assert 'Marco Bianchi' in result
    assert 'Hotel Test' in result
    assert 'Torino' in result
    assert 'Gonzalo Medrano Ortiz' in result
    assert '10/05/2025' in result

    print("✓ Email template rendering works correctly")


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  🧪 RUNNING TEMPLATE RENDERING TESTS")
    print("="*60 + "\n")

    try:
        test_render_template()
        test_html_to_plain_text()
        test_multiple_placeholders()
        test_email_template()

        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
