---
name: bakerydemo-maintenance
description: Helps maintainers of wagtail/bakerydemo with ongoing maintenance tasks. Use when upgrading Wagtail or Django versions, handling deprecation warnings, fixing failing CI pipelines, auditing security vulnerabilities in dependencies, reviewing Dependabot PRs, or checking project health. Do NOT use this skill for setting up a development environment or adding new content to the site.
license: MIT
metadata:
  author: Abhi090907
  version: "1.0"
compatibility: Requires Python 3.11+, pip, and git. Scripts must be run from the root of a cloned wagtail/bakerydemo repository. Designed for Claude Code, Cursor, and other Agent Skills compatible tools.
allowed-tools: Bash(python:*) Bash(pip:*) Bash(git:*) Read
---

# Bakerydemo Maintainer Skill

This skill is for **maintainers** of https://github.com/wagtail/bakerydemo — the
official Wagtail demonstration and local development site.

It covers the recurring tasks that keep the project healthy, secure and compatible
with new releases of Wagtail, Django and Python over time.

This skill is NOT for contributors setting up a development environment or adding
new content. See the project README for those tasks.

---

## Quick Reference

| Task | Script | What it does |
|------|--------|-------------|
| Full health check | `scripts/maintain.py` | Runs all checks in one command |
| Check for upgrades | `scripts/maintain.py --check upgrades` | Finds available Wagtail/Django updates |
| Security audit | `scripts/maintain.py --check security` | Audits all dependencies for CVEs |
| CI health check | `scripts/maintain.py --check ci` | Replicates CI pipeline checks locally |
| Deprecation check | `scripts/maintain.py --check deprecations` | Finds deprecated API usage |

Run all checks at once:
```bash
python scripts/maintain.py
```

For detailed guidance on each task see [references/REFERENCE.md](references/REFERENCE.md).
For the Wagtail and Django compatibility matrix see [references/wagtail-versions.md](references/wagtail-versions.md).

---

## Upgrading Wagtail

Always read the upgrade considerations before starting:
https://docs.wagtail.org/en/latest/releases/index.html

```bash
# Step 1 — update the version pin in requirements/base.txt
# Example: wagtail>=5.2,<6.0  becomes  wagtail>=6.0,<7.0

# Step 2 — install and migrate
pip install -r requirements/development.txt
python manage.py migrate

# Step 3 — check for deprecation warnings (must all be fixed)
python -W error manage.py check
python -W error manage.py test

# Step 4 — run the full test suite
python manage.py test

# Step 5 — test manually
python manage.py runserver
# Visit http://127.0.0.1:8000/ and check all pages render correctly
```

PR title format: `Upgrade to Wagtail X.Y`
Always link the Wagtail release notes in the PR description.

---

## Upgrading Django

Before upgrading Django, confirm compatibility with the current Wagtail version.
See references/wagtail-versions.md or:
https://docs.wagtail.org/en/stable/releases/upgrading.html

```bash
# Update requirements/base.txt then:
pip install -r requirements/development.txt
python manage.py check
python manage.py migrate
python -W error::DeprecationWarning manage.py test
```

PR title format: `Upgrade to Django X.Y`

---

## Upgrading Python

Check that the new Python version is supported by both Django and Wagtail before
upgrading. Update the python-version matrix in .github/workflows/ to include the
new version. Test locally with the new Python version before updating CI.

---

## Handling Security Vulnerabilities

Run the security audit:
```bash
python scripts/maintain.py --check security
```

Or manually:
```bash
pip install pip-audit
pip-audit -r requirements/base.txt
pip-audit -r requirements/production.txt
```

Security fixes must be merged immediately.
PR title format: `Security: upgrade [package] to X.Y.Z`
Always reference the CVE number in the PR description.

---

## Fixing Failing CI

Run the CI health check locally first:
```bash
python scripts/maintain.py --check ci
```

Common causes of CI failures and how to fix them:

**Missing migration after a model change:**
```bash
python manage.py makemigrations --check
python manage.py makemigrations
python manage.py migrate
```

**Linting failure:**
```bash
flake8 .
black --check .
```

**Outdated GitHub Actions versions:**
Check .github/workflows/ for outdated versions. Current recommended versions:
- actions/checkout: v4
- actions/setup-python: v5
- actions/cache: v4

---

## Reviewing Dependabot PRs

```bash
git fetch origin
git checkout dependabot/pip/package-name-x.y.z
pip install -r requirements/development.txt
python manage.py test
```

If tests pass and no breaking changes exist, approve and merge.
If tests fail, leave a comment explaining the blocker.

---

## Reviewing Contributor PRs

Before merging any PR confirm all of the following:

- CI is passing — green checkmark on the PR
- No new deprecation warnings: `python -W error manage.py test`
- Migrations included if models changed: `python manage.py makemigrations --check`
- Change is backwards compatible with all supported versions in references/wagtail-versions.md
- Documentation or README updated if the change affects project setup

---

## Key Files for Maintainers

| File | Purpose |
|------|---------|
| `requirements/base.txt` | Core dependency version pins |
| `requirements/development.txt` | Development dependency pins |
| `requirements/production.txt` | Production dependency pins |
| `.github/workflows/` | CI/CD pipeline configuration |
| `.github/dependabot.yml` | Automated dependency update config |
| `bakerydemo/settings/base.py` | Core Django and Wagtail settings |
