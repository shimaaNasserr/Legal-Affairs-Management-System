# Legal Affairs Backend

Backend for the Legal Affairs application, built with Django and Django REST Framework.

### 1. User Management

* Custom `User` model with `role` and `department`.
* JWT Authentication (`LoginView`) using `djangorestframework-simplejwt`.
* Registration endpoint (`RegisterView`) with email, first name, last name, password.
* User detail endpoint (`UserDetailView`) to view/update own data with proper permissions.
* Roles management via `Role` model and `/api/accounts/roles/` endpoint.

### 2. Secretary Management

* `InviteSecretaryView` endpoint to assign existing users as secretaries to lawyers.
* Only lawyers can assign secretaries.
* Permissions ensure only related users can view/edit data.

### 3. Permissions

* Admin/superuser and president roles can manage all users.
* Lawyer can manage only their secretaries.
* Regular users can only view/update their own info.
* Role, department, and assigned lawyer fields are read-only for normal users.

### 4. Cloudinary Integration

* Configured Cloudinary for media storage.
* `DEFAULT_FILE_STORAGE` set to `cloudinary_storage.storage.MediaCloudinaryStorage`.

### 5. REST API Endpoints
| Method  | Endpoint                          | Description                | Permissions                                      | Postman Example                                                                                                           |
| ------- | --------------------------------- | -------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| POST    | `/api/accounts/register/`         | Create new user            | Public                                           | `{ "username": "user1", "email": "user1@mail.com", "first_name": "User", "last_name": "One", "password": "password123" }` |
| POST    | `/api/accounts/login/`            | Login with JWT             | Public                                           | `{ "email": "user1@mail.com", "password": "password123" }`                                                                |
| GET/PUT | `/api/accounts/users/{id}/`       | Retrieve or update user    | Authenticated (user itself / lawyer / president) | Header: `Authorization: Bearer <token>`                                                                                   |
| POST    | `/api/accounts/invite-secretary/` | Assign secretary to lawyer | Authenticated (lawyer)                           | `{ "email": "sec@mail.com" }`                                                                                             |
| GET     | `/api/accounts/roles/`            | List all roles             | Authenticated                                    | Header: `Authorization: Bearer <token>`                                                                                   |


### 6. Project Setup

* PostgreSQL database configured via `.env`.
* CORS allowed for all origins.
* Environment variables loaded via `python-dotenv`.

## Tech Stack

* Django 5.2
* Django REST Framework
* SimpleJWT
* Cloudinary
* PostgreSQL
* Python 3.13

## How to run

1. Clone the repo

```bash
git clone <repo-url>
cd legal_affairs_backend
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set environment variables in `.env` file
5. Run migrations

```bash
python manage.py migrate
```

6. Run server

```bash
python manage.py runserver
```

## Notes

* All endpoints require JWT authentication except registration and login.
* Permissions are enforced based on user role.
