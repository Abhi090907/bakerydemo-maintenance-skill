# Wagtail and Django Compatibility Matrix

Use this reference when planning upgrades to confirm compatibility between
Wagtail, Django and Python versions.

Always verify against the official documentation at:
https://docs.wagtail.org/en/stable/releases/upgrading.html

---

## Supported combinations (as of early 2026)

| Wagtail | Django | Python | Status |
|---------|--------|--------|--------|
| 6.x | 4.2, 5.0, 5.1 | 3.11, 3.12, 3.13 | Current |
| 5.2 (LTS) | 4.2, 5.0 | 3.11, 3.12 | Long Term Support |
| 5.1 | 4.2, 5.0 | 3.11, 3.12 | Security fixes only |

---

## Long Term Support releases

Wagtail LTS releases receive security fixes for 24 months.
Current LTS: Wagtail 5.2

The bakerydemo should always be compatible with the current LTS release
as a minimum requirement.

---

## Upgrade path

When upgrading both Wagtail and Django, always upgrade Wagtail first.
Test on the lowest supported Python version first to catch any
compatibility issues early.

Upgrade order: Wagtail first, then Django, then Python.

---

## End of life schedule

| Version | End of life |
|---------|-------------|
| Python 3.10 | October 2026 |
| Python 3.11 | October 2027 |
| Django 4.2 LTS | April 2026 |
| Django 5.2 LTS | April 2028 |

When a version reaches end of life, drop support for it in the
bakerydemo CI matrix and update the requirements files accordingly.
