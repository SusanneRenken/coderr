# Coderr Backend

Backend for a freelancer developer platform.  
Built with **Django** and **Django REST Framework (DRF)**.

This project provides an API that is consumed by a separate frontend.

---

## Setup

1. Clone the repository and switch into the project directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   env\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser (for the admin panel):
   ```bash
   python manage.py createsuperuser
   ```
6. Start the server:
   ```bash
   python manage.py runserver
   ```

---

## Authentication Endpoints

All endpoints are located under `/api/`.

### Registration

**POST** `/api/registration/`

Request:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "secret123",
  "repeated_password": "secret123",
  "type": "customer"
}
```

Response (201):
```json
{
  "token": "123abc...",
  "username": "newuser",
  "email": "newuser@example.com",
  "user_id": 5
}
```

- `type` can be `"customer"` or `"business"`.  
- If `type` is omitted, it defaults to `"customer"`.

---

### Login

**POST** `/api/login/`

Request:
```json
{
  "username": "newuser",
  "password": "secret123"
}
```

Response (200):
```json
{
  "token": "123abc...",
  "username": "newuser",
  "email": "newuser@example.com",
  "user_id": 5
}
```

---

### Token Usage

All protected endpoints require the token in the header:

```
Authorization: Token 123abc...
```

---

## Admin

- Django admin available at `/admin/`  
- `User` and `Profile` can be managed there.  

---

## Tests

Run tests with the Django test runner:

```bash
python manage.py test
```

- Test coverage for Registration and Login is close to 100%.  
- Includes Happy Path, validation errors, and side-effect checks.

---

## Requirements

- Python 3.11+
- Django 5+
- djangorestframework
- djangorestframework-authtoken

All dependencies are listed in `requirements.txt`.
