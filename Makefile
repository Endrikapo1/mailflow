.PHONY: help dry-run send send-test test clean

help:
	@echo "Mail Merge - Available Commands:"
	@echo ""
	@echo "  make dry-run      - Simulate email sending (no emails sent)"
	@echo "  make send         - Send all emails and update CSV"
	@echo "  make send-test    - Send only first 5 emails (test mode)"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Remove log files"
	@echo ""

dry-run:
	python3 send_mail_merge.py \
		--csv contacts_hotels.csv \
		--subject subject.txt \
		--html email_template_italiano.html \
		--dry-run

send:
	python3 send_mail_merge.py \
		--csv contacts_hotels.csv \
		--subject subject.txt \
		--html email_template_italiano.html \
		--update-contacts

send-test:
	python3 send_mail_merge.py \
		--csv contacts_hotels.csv \
		--subject subject.txt \
		--html email_template_italiano.html \
		--max 5 \
		--dry-run

test:
	@echo "Running template rendering tests..."
	python3 tests/test_render.py
	@echo ""
	@echo "Running CLI tests..."
	python3 tests/test_cli_dry_run.py

clean:
	rm -f outbox_log.csv
	@echo "Log files cleaned"
