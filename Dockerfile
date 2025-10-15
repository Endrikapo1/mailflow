FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY send_mail_merge.py .
COPY subject.txt .
COPY email_template_italiano.html .
COPY contacts_hotels.csv .
COPY .env.example .

# Create tests directory and copy tests
COPY tests/ tests/

# Make scripts executable
RUN chmod +x send_mail_merge.py tests/*.py

# Set up volume for persistent data
VOLUME ["/app/data"]

# Default command shows help
CMD ["python3", "send_mail_merge.py", "--help"]
