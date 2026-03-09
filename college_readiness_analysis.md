# BrosDen-AV (NIRVANA) — College Presentation & PythonAnywhere Readiness Audit

> **Date**: March 2026 | **Scope**: Full project analysis for academic presentation and live hosting

---

## ✅ What's Already Strong (Impress-the-Professor Points)

| Area | Details |
|---|---|
| **Scale** | 20+ Django apps — this is an enterprise-grade architecture, not a toy project |
| **Role-Based Access** | Custom `AbstractUser` with ADMIN/TENANT/OWNER roles + custom decorators |
| **Full Business Flow** | Property listing → Booking → Payment → Contract → Onboarding → Feedback loop |
| **Payment System** | Security deposits, contract fees, monthly rent tracking with receipts |
| **Analytics** | Property view tracking, search activity logging, doughnut charts with Chart.js |
| **Real-Time Features** | Chat system, notifications (8 types), email integration |
| **Map Integration** | Geo-coordinates on properties, map explore view |
| **Vibe Check** | Overpass API integration to analyze neighborhood POIs — unique feature |
| **Gamification** | Owner badges, Pro/Gold membership tiers |
| **Clean Architecture** | DRY templates with `{% include %}` partials, proper app separation |

---

## 🔴 CRITICAL — Must Fix Before Presentation

### 1. `DEBUG = True` & Hardcoded `SECRET_KEY`
**Why it matters**: Your professors will look at `settings.py` first. A hardcoded secret key and debug mode screams "not production-ready."

**Fix**:
```python
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-dev-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### 2. `ALLOWED_HOSTS = []` (Empty)
**Why it matters**: The app will crash on PythonAnywhere with a `DisallowedHost` error.

**Fix**: Must include your PythonAnywhere domain:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']
```

### 3. Zero Unit Tests
Every single `tests.py` file across all 19 apps is empty (just the Django boilerplate `from django.test import TestCase`). Professors **will** ask about testing.

**Fix**: Write at least logic/smoke tests for critical apps like `accounts`, `property`, and `booking`.

### 4. Empty `static/` Directory
Your `STATICFILES_DIRS` points to `BASE_DIR / 'static'` but the folder is empty. This means all your CSS/JS is loaded from CDNs. On PythonAnywhere, you need local static files for `collectstatic`.

**Fix**: Run `python manage.py collectstatic` before deployment.

### 5. No `README.md`
This is the **first thing** anyone sees. You need one with project title, tech stack, features, and setup instructions.

---

## 🟡 IMPORTANT — Will Be Asked in Viva/Demo

### 6. Most `admin.py` Files Are Empty
Only a few apps have actual admin registrations. The remaining 15+ apps have empty `admin.py` files. 

**Fix**: Register critical models (Property, Booking, Payment) so you can manage them in the admin dashboard during the demo.

### 7. No Error Pages (404, 500)
Django shows an ugly default page when `DEBUG=False`. 

**Fix**: Create `templates/404.html` and `templates/500.html` with your project's branding.

### 8. SQLite Database
Fine for demo, but be ready to talk about scaling to PostgreSQL/MySQL.

### 9. No Data Fixtures / Seed Data
Deployment will start with an empty DB. 

**Fix**: Use `dumpdata` or a custom management command to seed demo data.

---

## 🟢 PythonAnywhere-Specific Setup Checklist

- Update **ALLOWED_HOSTS**
- Run **collectstatic**
- Configure **Static/Media URL mapping** in PA web tab
- Move **SECRET_KEY** to environment variables
- Ensure absolute paths for **SQLite DB**
- Use `console` email backend for demo if SMTP isn't set up

---

## 🎯 Quick Priority Hit-List

1. **Create `README.md`**
2. **Fix `settings.py` environment variables**
3. **Register models in Django Admin**
4. **Write basic unit tests**
5. **Prepare demo seed data**
6. **Deploy and verify live**
