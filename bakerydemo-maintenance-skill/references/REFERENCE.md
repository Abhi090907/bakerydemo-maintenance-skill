# Bakerydemo Maintainer Reference

Detailed reference for maintainers of https://github.com/wagtail/bakerydemo.

---

## Project Overview

The bakerydemo is the official Wagtail demonstration and local development
site. It serves two purposes: demonstrating Wagtail to developers and
organisations evaluating the CMS, and providing the standard development
environment for Wagtail core contributors.

### Repository structure

```
bakerydemo/
├── bakerydemo/
│   ├── settings/
│   │   ├── base.py           base settings shared across environments
│   │   ├── dev.py            development settings
│   │   ├── production.py     production settings
│   │   └── local.py          local overrides (not committed)
│   ├── base/                 base page models and mixins
│   ├── blog/                 blog index and blog page models
│   ├── breads/               bread page models
│   ├── locations/            location page models
│   ├── people/               person snippet models
│   ├── recipes/              recipe page models
│   ├── templates/            base templates
│   └── static/               static assets
├── requirements/
│   ├── base.txt              core dependency pins
│   ├── development.txt       development dependency pins
│   └── production.txt        production dependency pins
├── .github/
│   ├── workflows/            CI/CD pipeline configuration
│   └── dependabot.yml        automated dependency update config
└── manage.py
```

---

## Release Cadence

Wagtail releases a new version every three months. Each release may
introduce deprecation warnings for APIs that will be removed in future
releases. The bakerydemo must be updated within a reasonable time of
each new Wagtail release to stay current.

LTS releases receive security fixes for 24 months and are the safest
upgrade targets for the bakerydemo.

---

## Dependency Management

### Understanding the requirements files

- `requirements/base.txt` — packages required in all environments
- `requirements/development.txt` — additional packages for local development
- `requirements/production.txt` — additional packages for production deployment

When updating a dependency, always update the correct file and test
in both development and production configurations.

### Version pinning strategy

Use compatible release specifiers where possible:
```
wagtail>=6.0,<7.0
Django>=5.0,<6.0
```

This allows patch releases to be installed automatically while
preventing unexpected major version upgrades.

### After any dependency update

Always run the full sequence:
```bash
pip install -r requirements/development.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

Confirm the site renders correctly before submitting the PR.

---

## CI/CD Pipeline

The bakerydemo uses GitHub Actions for CI. The pipeline runs on every
push and pull request. Key jobs include running the test suite,
checking for missing migrations, and linting.

### Viewing CI results

Go to the Actions tab on GitHub to view the result of each job.
Click into a failing job to see the full log output.

### Common CI failure patterns

**Test failure after a dependency update**
Run `python manage.py test` locally to reproduce. Fix the failing
test or update the code to work with the new dependency version.

**Missing migration**
Run `python manage.py makemigrations --check`. If it exits non-zero,
a migration is missing. Run `python manage.py makemigrations` to
generate it and include it in the PR.

**Linting failure**
Run `flake8 .` and `black --check .` locally to identify issues.
Fix all formatting and style issues before pushing.

**Outdated GitHub Actions**
Check .github/workflows/ for uses: references with outdated version
tags. Update to the latest stable version of each action.

---

## Pull Request Review Checklist

Before merging any pull request:

1. CI is passing — all checks show green
2. Tests pass locally: `python manage.py test`
3. No new deprecation warnings: `python -W error manage.py test`
4. No missing migrations: `python manage.py makemigrations --check`
5. Change is backwards compatible with all supported Wagtail/Django versions
6. README or documentation updated if the change affects project setup
7. Fixtures updated if the change affects content structure

---

## Dependabot Configuration

Dependabot is configured in `.github/dependabot.yml` to automatically
open pull requests when dependencies have updates or security patches.

### Reviewing a Dependabot PR

1. Read the changelog linked in the PR description
2. Check for breaking changes in the new version
3. Pull the branch and run the test suite locally
4. If tests pass, approve and merge
5. If tests fail, investigate and leave a comment explaining the blocker

### Adjusting Dependabot behaviour

To ignore a specific package or version range:
```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /requirements
    schedule:
      interval: weekly
    ignore:
      - dependency-name: "package-name"
        versions: ["2.x"]
```

---

## Security Response Process

When a security advisory is published for a package the bakerydemo depends on:

1. Run `python scripts/maintain.py --check security` to confirm the exposure
2. Read the advisory to understand the affected versions and the fix
3. Update the version pin in the appropriate requirements file
4. Run `pip install -r requirements/development.txt && python manage.py test`
5. Submit a PR immediately — do not wait for the normal review cycle
6. Title the PR: `Security: upgrade [package] to X.Y.Z`
7. Reference the CVE number in the PR description

Security fixes take priority over all other work.
