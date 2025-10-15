# 📧 Mailflow

A professional CLI application for sending personalized mass emails. Built with Python using only standard libraries - no external dependencies required.

## ✨ Features

- 📨 **Personalized emails** with mail-merge functionality
- 🔒 **Secure SMTP** support (SSL/TLS)
- 📎 **PDF attachments** (CV, cover letters, etc.)
- 🎨 **HTML emails** with automatic plain-text fallback
- 🚦 **Rate limiting** to avoid spam filters
- 📊 **CSV-based** contact management
- 📝 **Comprehensive logging** of all operations
- 🧪 **Dry-run mode** for testing
- 🎨 **Colored terminal output** for better UX
- ✅ **Status tracking** to avoid duplicate sends

## 🔧 Requirements

- Python 3.9 or higher
- Gmail account with App Password (or other SMTP server)
- No external dependencies - uses only Python standard library

## 📦 Installation

1. Clone or download this repository:
```bash
git clone https://github.com/gmodev/mailflow.git
cd mailflow
```

2. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

3. Edit `.env` with your SMTP credentials:
```bash
nano .env  # or use your preferred editor
```

## ⚙️ Configuration

### Setting up Gmail App Password

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password to your `.env` file

### .env File Structure

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_SSL=true
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_16_char_app_password

# Sender Information
SENDER_NAME=Your Full Name
SENDER_EMAIL=your_email@gmail.com
```

### CSV Contact File Format

Your `contacts_hotels.csv` should have these columns:

```csv
email,hotel_name,city,contact_name,notes,status,sent_at
hr@hotel.com,Hotel Name,City,Contact Person,,
```

- **email**: Recipient email (required)
- **hotel_name**: Name of the hotel (required)
- **city**: City location (required)
- **contact_name**: Person's name (optional - generic greeting used if empty)
- **notes**: Your internal notes (optional)
- **status**: SENT/SKIP/empty (managed by script)
- **sent_at**: Timestamp (managed by script)

### Template Placeholders

Available placeholders for `subject.txt` and `email_template_italiano.html`:

- `{{contact_name}}` - Recipient's name
- `{{hotel_name}}` - Hotel name
- `{{city}}` - Hotel city
- `{{sender_name}}` - Your name (from .env)
- `{{today}}` - Current date (DD/MM/YYYY)

## 🚀 Usage

### Basic Commands

**Dry run (simulate without sending):**
```bash
python3 send_mail_merge.py \
  --csv contacts_hotels.csv \
  --subject subject.txt \
  --html email_template_italiano.html \
  --dry-run
```

**Send emails with PDF attachment:**
```bash
python3 send_mail_merge.py \
  --csv contacts_hotels.csv \
  --subject subject.txt \
  --html email_template_italiano.html \
  --attachment cv.pdf
```

**Send and update CSV status:**
```bash
python3 send_mail_merge.py \
  --csv contacts_hotels.csv \
  --subject subject.txt \
  --html email_template_italiano.html \
  --update-contacts
```

### Using Makefile

```bash
# Simulate sending (dry-run)
make dry-run

# Send all emails
make send

# Test with only first 5 contacts
make send-test

# Run all tests
make test

# Clean log files
make clean
```

### Advanced Options

```bash
# Send only first 10 emails
--max 10

# Start from row 5 (0-indexed)
--from-row 5

# Wait 5 seconds between emails
--sleep 5

# Use custom log file
--log my_custom_log.csv

# Use different .env file
--env .env.production
```

### Complete Example

```bash
python3 send_mail_merge.py \
  --csv contacts_hotels.csv \
  --subject subject.txt \
  --html email_template_italiano.html \
  --attachment CV_Gonzalo_Medrano.pdf \
  --update-contacts \
  --sleep 5 \
  --max 20
```

## 📋 Command-Line Arguments

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--csv` | Path to contacts CSV file |
| `--subject` | Path to subject template file |
| `--html` | Path to HTML email template |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--attachment` | None | Path to PDF file to attach |
| `--env` | `.env` | Path to environment file |
| `--sleep` | `3` | Seconds to wait between emails |
| `--dry-run` | False | Simulate without sending |
| `--max` | None | Maximum emails to send |
| `--from-row` | `0` | Start from row N (0-indexed) |
| `--update-contacts` | False | Update CSV with status |
| `--log` | `outbox_log.csv` | Path to log file |

## 🧪 Testing

Run all tests:
```bash
make test
```

Or run individually:
```bash
# Test template rendering
python3 tests/test_render.py

# Test CLI functionality
python3 tests/test_cli_dry_run.py
```

## 📊 Logging

All email operations are logged to `outbox_log.csv` with:
- Email address
- Hotel name and city
- Contact name
- Status (SENT/ERROR/DRY_RUN)
- Error message (if any)
- Timestamp

## 🐳 Docker Support

Build the Docker image:
```bash
docker build -t mailflow .
```

Run with Docker:
```bash
docker run -v $(pwd)/data:/app/data mailflow \
  python3 send_mail_merge.py \
  --csv contacts_hotels.csv \
  --subject subject.txt \
  --html email_template_italiano.html \
  --dry-run
```

## 🔍 Troubleshooting

### "Authentication failed" error

- Verify your Gmail App Password is correct
- Make sure 2-Step Verification is enabled on your Google account
- Check that `SMTP_USER` and `SMTP_PASS` are set correctly in `.env`

### "Connection refused" error

- Check your internet connection
- Verify SMTP_HOST and SMTP_PORT are correct
- Some networks block port 465 - try port 587 with `SMTP_SSL=false`

### Emails going to spam

- Send fewer emails per session (use `--max`)
- Increase delay between emails (use `--sleep 10`)
- Personalize your template more
- Avoid spam trigger words
- Consider warming up your email account gradually

### "Invalid email format" errors

- Check that email addresses in CSV are valid
- Remove any extra spaces or special characters

### CSV not updating

- Make sure you use `--update-contacts` flag
- Check file permissions on the CSV file
- Verify CSV has correct column headers

## 🎯 Best Practices

1. **Always test first**: Use `--dry-run` to verify everything works
2. **Start small**: Use `--max 5` for initial real sends
3. **Respect rate limits**: Keep `--sleep` at 3-5 seconds minimum
4. **Monitor logs**: Check `outbox_log.csv` regularly
5. **Backup contacts**: Keep a backup of your CSV before using `--update-contacts`
6. **Personalize content**: Update templates for your specific use case
7. **Check spam folder**: Monitor where your emails land
8. **Warm up gradually**: Don't send hundreds of emails on day one

## 📁 Project Structure

```
mailflow/
├── send_mail_merge.py          # Main application script
├── .env.example                # Example environment configuration
├── subject.txt                 # Email subject template
├── email_template_italiano.html # HTML email template
├── contacts_hotels.csv         # Sample contact list
├── Makefile                    # Convenient make commands
├── Dockerfile                  # Docker configuration
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
└── tests/
    ├── test_render.py         # Template rendering tests
    └── test_cli_dry_run.py    # CLI functionality tests
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Gonzalo Medrano Ortiz**
- GitHub: [@gmodev](https://github.com/gmodev)
- Email: gonzalomeortiz@gmail.com
- Location: Italy

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## ⚠️ Disclaimer

This tool is for legitimate business communication only. Users are responsible for:
- Complying with anti-spam laws (CAN-SPAM, GDPR, etc.)
- Obtaining proper consent when required
- Following email service provider terms of service
- Respecting recipients' privacy and preferences

Misuse of this tool for spam or unsolicited bulk email is strictly prohibited and may be illegal in your jurisdiction.

## 📞 Support

For issues or questions:
1. Check this README first
2. Review the troubleshooting section
3. Check the issue tracker
4. Create a new issue with details about your problem

---

**Made with ❤️ for professional job seekers**
