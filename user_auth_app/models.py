from django.contrib.auth.models import User
from django.db import models

"""
User Authentication App Models

This app uses Django's built-in User model for authentication.
No custom user models or profiles are currently implemented.

The Django User model provides:
- username: Unique username for login
- email: User's email address
- password: Hashed password
- first_name, last_name: Optional name fields
- is_staff, is_superuser: Permission flags
- date_joined, last_login: Timestamp fields

Authentication is handled via Token Authentication (DRF).
"""
