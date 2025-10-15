#!/usr/bin/env python3
"""
Mail Merge CLI Tool for Hotels
Send personalized mass emails with attachments
"""

import smtplib
import ssl
import csv
import argparse
import os
import sys
import time
import re
import socket
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from html.parser import HTMLParser
from io import StringIO


# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class HTMLToPlainText(HTMLParser):
    """Convert HTML to plain text by stripping tags"""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.text.write("\n")
        elif tag == "p":
            self.text.write("\n")

    def handle_endtag(self, tag):
        if tag == "p":
            self.text.write("\n")

    def get_text(self):
        return self.text.getvalue()


def html_to_plain_text(html_content):
    """Convert HTML content to plain text"""
    parser = HTMLToPlainText()
    parser.feed(html_content)
    text = parser.get_text()
    # Clean up multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def print_colored(message, color=Colors.RESET):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.RESET}")


def validate_email(email):
    """Validate email format and verify domain exists"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False

    # Verify domain exists (DNS lookup)
    try:
        domain = email.split("@")[1]
        socket.gethostbyname(domain)
        return True
    except (socket.gaierror, IndexError):
        return False


def load_env_config(env_path=None):
    """
    Load environment configuration.
    Priority: System environment variables > .env file
    """
    env_vars = {}

    # First, try to load from system environment variables
    required_vars = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASS",
        "SENDER_NAME",
        "SENDER_EMAIL",
    ]

    # Check if all required vars are in system environment
    system_vars = {var: os.environ.get(var) for var in required_vars}
    if all(system_vars.values()):
        print_colored("✓ Using credentials from system environment variables", Colors.GREEN)
        env_vars = system_vars
        # Also get SMTP_SSL if present, default to "true"
        env_vars["SMTP_SSL"] = os.environ.get("SMTP_SSL", "true")
        return env_vars

    # If not all in system env, fall back to .env file
    if env_path and os.path.exists(env_path):
        print_colored(f"✓ Loading credentials from {env_path}", Colors.YELLOW)
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

        # Validate required variables from file
        missing_vars = [var for var in required_vars if var not in env_vars]
        if missing_vars:
            print_colored(
                f"❌ Error: Missing required variables: {', '.join(missing_vars)}",
                Colors.RED,
            )
            sys.exit(1)

        return env_vars

    # Neither system env nor .env file has the credentials
    print_colored("❌ Error: No credentials found!", Colors.RED)
    print_colored("\nYou can provide credentials in two ways:", Colors.YELLOW)
    print_colored("\n1. System environment variables (Recommended):", Colors.CYAN)
    print_colored("   export SMTP_HOST='smtp.gmail.com'", Colors.RESET)
    print_colored("   export SMTP_PORT='465'", Colors.RESET)
    print_colored("   export SMTP_SSL='true'", Colors.RESET)
    print_colored("   export SMTP_USER='your_email@gmail.com'", Colors.RESET)
    print_colored("   export SMTP_PASS='your_app_password'", Colors.RESET)
    print_colored("   export SENDER_NAME='Your Name'", Colors.RESET)
    print_colored("   export SENDER_EMAIL='your_email@gmail.com'", Colors.RESET)
    print_colored("\n2. Using .env file:", Colors.CYAN)
    print_colored("   cp .env.example .env", Colors.RESET)
    print_colored("   # Edit .env with your credentials", Colors.RESET)
    sys.exit(1)


def load_template(template_path):
    """Load email template from file"""
    if not os.path.exists(template_path):
        print_colored(
            f"❌ Error: Template file not found at {template_path}", Colors.RED
        )
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def render_template(template, context):
    """Replace placeholders in template with context values"""
    result = template
    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def load_contacts(csv_path):
    """Load contacts from CSV file"""
    if not os.path.exists(csv_path):
        print_colored(f"❌ Error: Contacts CSV not found at {csv_path}", Colors.RED)
        sys.exit(1)

    contacts = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate CSV columns
        required_columns = {
            "email",
            "hotel_name",
            "city",
            "contact_name",
            "notes",
            "status",
            "sent_at",
        }

        if not reader.fieldnames:
            print_colored(
                "❌ Error: CSV file appears to be empty or malformed", Colors.RED
            )
            print_colored("Expected format:", Colors.YELLOW)
            print_colored(",".join(required_columns), Colors.YELLOW)
            sys.exit(1)

        if not required_columns.issubset(reader.fieldnames):
            missing = required_columns - set(reader.fieldnames)
            found = set(reader.fieldnames) - required_columns
            print_colored("❌ Error: CSV has incorrect columns", Colors.RED)
            print_colored(
                f"Missing required columns: {', '.join(missing)}", Colors.YELLOW
            )
            print_colored(f"Found extra columns: {', '.join(found)}", Colors.YELLOW)
            print_colored("\nExpected CSV format:", Colors.CYAN)
            print_colored(",".join(required_columns), Colors.CYAN)
            sys.exit(1)

        for row in reader:
            contacts.append(row)

    return contacts


def save_contacts(csv_path, contacts, fieldnames):
    """Save contacts back to CSV file"""
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contacts)


def log_to_file(
    log_path, email, hotel_name, city, contact_name, status, info, timestamp
):
    """Append log entry to CSV log file"""
    file_exists = os.path.exists(log_path)

    with open(log_path, "a", encoding="utf-8", newline="") as f:
        fieldnames = [
            "email",
            "hotel_name",
            "city",
            "contact_name",
            "status",
            "info",
            "timestamp",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "email": email,
                "hotel_name": hotel_name,
                "city": city,
                "contact_name": contact_name,
                "status": status,
                "info": info,
                "timestamp": timestamp,
            }
        )


def create_email_message(
    env_vars, subject, html_body, plain_body, to_email, to_name, attachment_path=None
):
    """Create email message with HTML, plain text alternative, and optional attachment"""
    msg = EmailMessage()

    # Set headers
    msg["Subject"] = subject
    msg["From"] = formataddr((env_vars["SENDER_NAME"], env_vars["SENDER_EMAIL"]))

    if to_name:
        msg["To"] = formataddr((to_name, to_email))
    else:
        msg["To"] = to_email

    # Set body with HTML and plain text alternative
    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(
                file_data, maintype="application", subtype="pdf", filename=file_name
            )

    return msg


def send_email(env_vars, msg, dry_run=False):
    """Send email via SMTP"""
    if dry_run:
        return True, "DRY RUN - Email not sent"

    try:
        smtp_host = env_vars["SMTP_HOST"]
        smtp_port = int(env_vars["SMTP_PORT"])
        smtp_user = env_vars["SMTP_USER"]
        smtp_pass = env_vars["SMTP_PASS"]
        use_ssl = env_vars.get("SMTP_SSL", "true").lower() == "true"

        if use_ssl:
            # Use SSL (port 465)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            # Use STARTTLS (port 587)
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        return True, "Email sent successfully"

    except smtplib.SMTPAuthenticationError as e:
        return False, f"Error de autenticación SMTP: {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"Error: destinatarios rechazados: {str(e)}"
    except smtplib.SMTPSenderRefused as e:
        return False, f"Error: remitente rechazado: {str(e)}"
    except ssl.SSLError as e:
        return False, f"Error de SSL: {str(e)}"
    except socket.gaierror as e:
        return False, f"Error de resolución DNS: {str(e)}"
    except ConnectionError as e:
        return False, f"Error de conexión: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"Error SMTP: {str(e)}"


def send_email_with_retry(env_vars, msg, dry_run=False, max_retries=3):
    """Send email with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        success, info = send_email(env_vars, msg, dry_run)

        if success:
            return success, info

        # Don't retry on authentication errors
        if "Authentication" in info or "auth" in info.lower():
            return success, info

        # Don't retry on invalid recipient errors
        if "recipient" in info.lower() or "address" in info.lower():
            return success, info

        # Retry on temporary errors (connection, timeout, rate limit)
        if attempt < max_retries - 1:
            wait_time = 5 * (2**attempt)  # Exponential backoff: 5s, 10s, 20s
            time.sleep(wait_time)
        else:
            return False, f"Failed after {max_retries} attempts: {info}"

    return False, "Max retries exceeded"


def main():
    parser = argparse.ArgumentParser(
        description="Send personalized mass emails to hotels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (simulate without sending)
  python send_mail_merge.py --csv contacts.csv --subject subject.txt --html template.html --dry-run

  # Send real emails with attachment
  python send_mail_merge.py --csv contacts.csv --subject subject.txt --html template.html --attachment cv.pdf

  # Send only first 5 emails
  python send_mail_merge.py --csv contacts.csv --subject subject.txt --html template.html --max 5

  # Send and update CSV with status
  python send_mail_merge.py --csv contacts.csv --subject subject.txt --html template.html --update-contacts
        """,
    )

    # Required arguments
    parser.add_argument("--csv", required=True, help="Path to contacts CSV file")
    parser.add_argument(
        "--subject", required=True, help="Path to subject template file"
    )
    parser.add_argument(
        "--html", required=True, help="Path to HTML email template file"
    )

    # Optional arguments
    parser.add_argument("--attachment", help="Path to PDF attachment")
    parser.add_argument(
        "--env", default=".env", help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--sleep", type=int, default=3, help="Seconds between emails (default: 3)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without sending emails"
    )
    parser.add_argument("--max", type=int, help="Maximum number of emails to send")
    parser.add_argument(
        "--from-row", type=int, default=0, help="Start from row N (0-indexed)"
    )
    parser.add_argument(
        "--update-contacts",
        action="store_true",
        help="Update CSV with status and sent_at",
    )
    parser.add_argument(
        "--log",
        default="outbox_log.csv",
        help="Path to log file (default: outbox_log.csv)",
    )

    args = parser.parse_args()

    # Print banner
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("  📧 MAIL MERGE - Hotel Contact System", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60 + "\n", Colors.CYAN)

    if args.dry_run:
        print_colored("⚠️  DRY RUN MODE - No emails will be sent\n", Colors.YELLOW)

    # Load configuration
    print_colored("📋 Loading configuration...", Colors.BLUE)
    env_vars = load_env_config(args.env)
    subject_template = load_template(args.subject)
    html_template = load_template(args.html)
    contacts = load_contacts(args.csv)

    print_colored(f"✓ Loaded {len(contacts)} contacts from CSV", Colors.GREEN)

    # Validate attachment if provided
    if args.attachment and not os.path.exists(args.attachment):
        print_colored(
            f"❌ Error: Attachment not found at {args.attachment}", Colors.RED
        )
        sys.exit(1)

    # Filter contacts
    contacts_to_send = []
    for idx, contact in enumerate(contacts):
        # Skip if before from_row
        if idx < args.from_row:
            continue

        # Skip if already sent or marked to skip
        status = contact.get("status", "").strip().upper()
        if status in ["SENT", "SKIP"]:
            print_colored(
                f"⏭️  Skipping {contact['email']} - Status: {status}", Colors.YELLOW
            )
            continue

        # Validate email
        if not validate_email(contact["email"]):
            print_colored(f"❌ Invalid email format: {contact['email']}", Colors.RED)
            log_to_file(
                args.log,
                contact["email"],
                contact["hotel_name"],
                contact["city"],
                contact["contact_name"],
                "ERROR",
                "Invalid email format",
                datetime.now().isoformat(),
            )
            continue

        contacts_to_send.append((idx, contact))

        # Limit if max specified
        if args.max and len(contacts_to_send) >= args.max:
            break

    if not contacts_to_send:
        print_colored("\n⚠️  No contacts to send emails to", Colors.YELLOW)
        sys.exit(0)

    print_colored(f"\n📤 Ready to send {len(contacts_to_send)} emails\n", Colors.BLUE)

    # Prepare context
    today = datetime.now().strftime("%d/%m/%Y")
    sender_name = env_vars["SENDER_NAME"]

    # Statistics
    stats = {"sent": 0, "failed": 0, "skipped": 0}

    # Send emails
    for idx, (original_idx, contact) in enumerate(contacts_to_send, 1):
        email = contact["email"]
        hotel_name = contact["hotel_name"]
        city = contact["city"]
        contact_name = contact.get("contact_name", "").strip()

        # Use generic greeting if no contact name
        if not contact_name:
            contact_name = "Responsabile delle risorse umane"

        print_colored(
            f"\n[{idx}/{len(contacts_to_send)}] Processing {hotel_name} ({city})",
            Colors.CYAN,
        )
        print_colored(f"    To: {email}", Colors.CYAN)

        # Prepare context for template rendering
        context = {
            "contact_name": contact_name,
            "hotel_name": hotel_name,
            "city": city,
            "sender_name": sender_name,
            "today": today,
        }

        # Render templates
        subject = render_template(subject_template, context)
        html_body = render_template(html_template, context)
        plain_body = html_to_plain_text(html_body)

        # Create email message
        msg = create_email_message(
            env_vars,
            subject,
            html_body,
            plain_body,
            email,
            contact_name if contact_name != "Responsabile delle risorse umane" else "",
            args.attachment,
        )

        # Send email with retry logic
        success, info = send_email_with_retry(env_vars, msg, args.dry_run)

        timestamp = datetime.now().isoformat()

        if success:
            print_colored(f"    ✓ {info}", Colors.GREEN)
            stats["sent"] += 1

            # Update contact status
            if args.update_contacts:
                contacts[original_idx]["status"] = "SENT"
                contacts[original_idx]["sent_at"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Log success
            log_to_file(
                args.log,
                email,
                hotel_name,
                city,
                contact_name,
                "SENT" if not args.dry_run else "DRY_RUN",
                info,
                timestamp,
            )
        else:
            print_colored(f"    ✗ Failed: {info}", Colors.RED)
            stats["failed"] += 1

            # Log failure
            log_to_file(
                args.log,
                email,
                hotel_name,
                city,
                contact_name,
                "ERROR",
                info,
                timestamp,
            )

        # Wait before next email (except for last one)
        if idx < len(contacts_to_send):
            time.sleep(args.sleep)

    # Update CSV if requested
    if args.update_contacts and stats["sent"] > 0:
        print_colored("\n💾 Updating contacts CSV...", Colors.BLUE)
        # Use the actual fieldnames from the CSV to preserve all columns
        with open(args.csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
        save_contacts(args.csv, contacts, fieldnames)
        print_colored("✓ CSV updated", Colors.GREEN)

    # Print summary
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("  📊 SUMMARY", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  ✓ Sent: {stats['sent']}", Colors.GREEN)
    if stats["failed"] > 0:
        print_colored(f"  ✗ Failed: {stats['failed']}", Colors.RED)
    print_colored(f"  📝 Log saved to: {args.log}", Colors.BLUE)
    if args.update_contacts and stats["sent"] > 0:
        print_colored("  💾 Contacts CSV updated", Colors.BLUE)
    print_colored("=" * 60 + "\n", Colors.CYAN)


if __name__ == "__main__":
    main()
