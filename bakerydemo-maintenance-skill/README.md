# bakerydemo-maintenance-skill

An AI agent skill for maintainers of the
[wagtail/bakerydemo](https://github.com/wagtail/bakerydemo) repository.

Built as part of a Google Summer of Code 2026 application for the
Wagtail Demo Website Redesign project.

---

## What this skill does

This skill helps AI coding assistants guide maintainers through the
recurring tasks that keep the bakerydemo project healthy, secure and
compatible with new releases of Wagtail, Django and Python over time.

It covers version upgrades, security vulnerability handling, CI failure
diagnosis, deprecation warning detection, Dependabot PR reviews and
contributor PR reviews.

This skill is NOT for contributors setting up a development environment
or adding new content to the site. See the project README for those tasks.

---

## Repository structure

```
bakerydemo-maintenance-skill/
├── SKILL.md                          main skill instructions
├── scripts/
│   └── maintain.py                   all-in-one maintenance script
├── references/
│   ├── REFERENCE.md                  detailed maintainer reference
│   └── wagtail-versions.md           Wagtail/Django compatibility matrix
└── README.md
```

---

## Using the skill with an AI agent

Load `SKILL.md` into any Agent Skills compatible tool such as Claude Code
or Cursor, then ask maintenance related questions.

Example prompt:
```
Using the bakerydemo maintenance skill at [URL], help me upgrade the
bakerydemo from Wagtail 5.2 to Wagtail 6.0. What are the steps and
what do I need to check?
```

---

## Running the maintenance script

The `scripts/maintain.py` script must be run from the root of a cloned
[wagtail/bakerydemo](https://github.com/wagtail/bakerydemo) repository.

```bash
# Clone bakerydemo first
git clone https://github.com/wagtail/bakerydemo.git
cd bakerydemo

# Copy the maintain.py script into the scripts folder
# Then run:

# Run all maintenance checks
python scripts/maintain.py

# Run a specific check
python scripts/maintain.py --check upgrades
python scripts/maintain.py --check security
python scripts/maintain.py --check ci
python scripts/maintain.py --check deprecations
```

### What each check does

| Flag | What it checks |
|------|---------------|
| `--check upgrades` | Compares installed Wagtail and Django versions against latest available |
| `--check security` | Runs pip-audit against base and production requirements |
| `--check ci` | Replicates the CI pipeline checks locally before pushing |
| `--check deprecations` | Runs tests with deprecation warnings as errors |
| *(no flag)* | Runs all four checks in sequence with a summary |

---

## Example output

```
==================================================
Bakerydemo Full Maintenance Check
==================================================

==================================================
Upgrade Check
==================================================

WARNING wagtail: 5.2.3 installed, 6.0.1 available
         Release notes: https://docs.wagtail.org/en/latest/releases/index.html
         To upgrade: update requirements/base.txt
         Then run: pip install -r requirements/development.txt
         Then run: python manage.py migrate && python manage.py test

PASSED  Django: 5.1.4 — up to date

==================================================
Security Audit
==================================================

Auditing requirements/base.txt...
PASSED  No vulnerabilities found in requirements/base.txt
Auditing requirements/production.txt...
PASSED  No vulnerabilities found in requirements/production.txt

==================================================
CI Health Check
==================================================

PASSED  Django system check
PASSED  Missing migrations check
PASSED  Full test suite

CI Results: 3/3 checks passed
All CI checks passed. Safe to push.

==================================================
Summary
==================================================

WARNING Upgrade check
PASSED  Security audit
PASSED  CI health check
PASSED  Deprecation check

3/4 checks passed
Issues found in: Upgrade check
```

---

## Author

Abhishek Bijjargi
GitHub: https://github.com/Abhi090907
Blog: https://dev.to/abhi090907
