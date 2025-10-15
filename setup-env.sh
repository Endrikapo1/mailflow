#!/bin/bash
# Setup script for environment variables
# This script helps you export the required environment variables securely

echo "🔐 Mail Merge - Secure Environment Setup"
echo "========================================="
echo ""
echo "This script will help you set environment variables for the current session."
echo "These variables will NOT be saved to any file."
echo ""

# SMTP Configuration
echo -n "SMTP Host [smtp.gmail.com]: "
read SMTP_HOST
SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}

echo -n "SMTP Port [465]: "
read SMTP_PORT
SMTP_PORT=${SMTP_PORT:-465}

echo -n "Use SSL [true]: "
read SMTP_SSL
SMTP_SSL=${SMTP_SSL:-true}

# User credentials
echo -n "SMTP User (your email): "
read SMTP_USER

echo "SMTP Password (App Password - won't be displayed):"
read -s SMTP_PASS
echo ""

# Sender information
echo -n "Sender Name: "
read SENDER_NAME

echo -n "Sender Email [$SMTP_USER]: "
read SENDER_EMAIL
SENDER_EMAIL=${SENDER_EMAIL:-$SMTP_USER}

# Export all variables
export SMTP_HOST="$SMTP_HOST"
export SMTP_PORT="$SMTP_PORT"
export SMTP_SSL="$SMTP_SSL"
export SMTP_USER="$SMTP_USER"
export SMTP_PASS="$SMTP_PASS"
export SENDER_NAME="$SENDER_NAME"
export SENDER_EMAIL="$SENDER_EMAIL"

echo ""
echo "✅ Environment variables have been set for this session!"
echo ""
echo "You can now run:"
echo "  python3 send_mail_merge.py --csv contacts_hotels.csv --subject subject.txt --html email_template_italiano.html --dry-run"
echo ""
echo "⚠️  Note: These variables will be lost when you close the terminal."
echo "    To make them persistent, add the exports to your ~/.bashrc or ~/.zshrc"
echo ""
