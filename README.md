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

## Offer Endpoints

**GET** `/api/offers/`  
- List all offers (paginated).  
- Supports filters:  
  - `creator_id` (user who created the offer)  
  - `min_price` (minimum price)  
  - `max_delivery_time` (shorter than or equal to given days)  
  - `ordering` (`updated_at`, `min_price`)  
  - `search` (search in `title` and `description`)  

**POST** `/api/offers/`  
- Create a new offer (requires `business` user).  
- Body must include **3 details** (basic, standard, premium).

**GET** `/api/offers/{id}/`  
- Retrieve details of a specific offer, including nested offerdetails.  
- Requires authentication.  

**PATCH** `/api/offers/{id}/`  
- Update offer and/or details (only owner).  

**DELETE** `/api/offers/{id}/`  
- Delete offer (only owner).  

**GET** `/api/offerdetails/{id}/`  
- Retrieve one specific offer detail (requires authentication).  

---

## Admin

- Available at `/admin/`  
- Manage `User`, `Profile`, `Offer` and `OfferDetail`.  

---

## Requirements

- Python 3.11+  
- Django 5+  
- djangorestframework (+ authtoken)  
- django-filter 25.1  

---

## Notes

- Code is PEP8 compliant, clean and structured according to [DRF best practices](https://www.django-rest-framework.org/).  
- Test coverage >95% (unit + API tests).  
- Database files are excluded from version control.  
