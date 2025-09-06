# Coderr Backend

Backend for a freelancer developer platform.  
Built with **Django** and **Django REST Framework (DRF)**.

---

## Setup

```bash
git clone <repo-url>
cd Coderr-backend
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Authentication

**POST** `/api/registration/` – create user + profile (`type = customer|business`).  
**POST** `/api/login/` – returns token.  

Use token for all protected endpoints:

```
Authorization: Token <your-token>
```

---

## Profile Endpoints

**GET / PATCH** `/api/profile/{pk}/`  
- Own profile can be updated, all profiles can be viewed.  
- Fields: `user, username, first_name, last_name, file, location, tel, description, working_hours, type, email, created_at`  
- Empty values are returned as `""`, not `null`.  
- File upload supported, `uploaded_at` set automatically.

**GET** `/api/profiles/business/`  
- List of business profiles (no email, no uploaded_at).

**GET** `/api/profiles/customer/`  
- List of customer profiles (with `uploaded_at`).

---

## Admin

- Available at `/admin/`  
- Manage `User` and `Profile`.  

---

## Requirements

- Python 3.11+  
- Django 5+  
- djangorestframework (+ authtoken)  
