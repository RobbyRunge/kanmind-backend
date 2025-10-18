# Kanmind - Kanban Board Backend API

A Django REST Framework-based backend for a collaborative Kanban board application. This API allows users to manage boards, tasks, and comments with role-based permissions.

## 🚀 Features

- **User Authentication**: Token-based authentication system
- **Board Management**: Create and manage Kanban boards with members
- **Task Management**: Full CRUD operations for tasks with status tracking
- **Comments System**: Add, view, and delete comments on tasks
- **Role-Based Permissions**: Owner and member-based access control
- **Task Assignment**: Assign tasks to specific users and reviewers
- **Priority & Status Tracking**: Organize tasks by priority and workflow status

## 📋 Table of Contents

- [Requirements](#-requirements)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Running the Server](#-running-the-server)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Authentication](#-authentication)
- [Special Features](#-special-features)
- [Troubleshooting](#-troubleshooting)
- [Development Notes](#-development-notes)
- [Contributing](#-contributing)

## 🛠️ Requirements

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd modul-8.1-kanmind
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Current Dependencies:**
- Django 5.2.7
- djangorestframework 3.16.1
- djangorestframework-authtoken (included)

### 4. Environment Variables (Optional)

For production, consider creating a `.env` file for sensitive settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🗄️ Database Setup

This project uses SQLite by default (`db.sqlite3`). No additional database configuration is required for development.

### 1. Apply Migrations

```bash
python manage.py migrate
```

This will create all necessary database tables for:
- User authentication
- Boards
- Tasks
- Comments

### 2. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account for accessing the Django Admin panel.

### 3. (Optional) Load Sample Data

You can create sample data through the Django Admin panel at `http://127.0.0.1:8000/admin/`

## 🏃 Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at: **`http://127.0.0.1:8000/`**

### Access Django Admin

Navigate to: **`http://127.0.0.1:8000/admin/`**

Use your superuser credentials to log in and manage data.

## 📚 API Documentation

### Base URL

```
http://127.0.0.1:8000/api/
```

### Authentication

All API endpoints require authentication via Token Authentication.

#### Obtain Token

**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "your-auth-token-here",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Register New User

**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Using Authentication Token

Include the token in all subsequent requests:

```
Authorization: Token your-auth-token-here
```

### Main API Endpoints

#### Boards

- **GET** `/api/boards/` - List all boards where user is a member
- **POST** `/api/boards/` - Create a new board
- **GET** `/api/boards/{id}/` - Get board details
- **PATCH** `/api/boards/{id}/` - Update board
- **DELETE** `/api/boards/{id}/` - Delete board (owner only)

#### Tasks

- **GET** `/api/tasks/assigned-to-me/` - Get tasks assigned to current user
- **GET** `/api/tasks/reviewing/` - Get tasks where user is reviewer
- **POST** `/api/tasks/` - Create a new task
- **PATCH** `/api/tasks/{id}/` - Update task
- **DELETE** `/api/tasks/{id}/` - Delete task (creator or board owner only)

#### Comments

- **GET** `/api/tasks/{task_id}/comments/` - Get all comments for a task
- **POST** `/api/tasks/{task_id}/comments/` - Add a comment to a task
- **DELETE** `/api/tasks/{task_id}/comments/{comment_id}/` - Delete a comment (author only)

### Example API Calls

#### Create a Board

```bash
curl -X POST http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Project Board",
    "description": "Project management board"
  }'
```

#### Create a Task

```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "board": 1,
    "title": "Implement login feature",
    "description": "Create user authentication system",
    "status": "to-do",
    "priority": "high",
    "assignee_id": 2,
    "due_date": "2025-11-01"
  }'
```

#### Add a Comment

```bash
curl -X POST http://127.0.0.1:8000/api/tasks/1/comments/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This task needs to be prioritized"
  }'
```

## 📁 Project Structure

```
modul-8.1-kanmind/
├── core/                      # Main project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI configuration
├── boards_app/               # Board management
│   ├── models.py             # Board model
│   ├── api/
│   │   ├── views.py          # Board API views
│   │   ├── serializers.py    # Board serializers
│   │   ├── permissions.py    # Board permissions
│   │   └── urls.py           # Board URL routing
│   └── migrations/           # Database migrations
├── tasks_app/                # Task management
│   ├── models.py             # Task and Comment models
│   ├── api/
│   │   ├── views.py          # Task API views
│   │   ├── serializers.py    # Task serializers
│   │   ├── permissions.py    # Task permissions
│   │   └── urls.py           # Task URL routing
│   └── migrations/           # Database migrations
├── user_auth_app/            # User authentication
│   ├── models.py             # User models (if extended)
│   ├── api/
│   │   ├── views.py          # Auth API views
│   │   ├── serializers.py    # User serializers
│   │   └── urls.py           # Auth URL routing
│   └── migrations/           # Database migrations
├── db.sqlite3                # SQLite database
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔐 Authentication

This project uses **Token Authentication** provided by Django REST Framework.

### How It Works

1. **Register** a new user via `/api/auth/register/`
2. **Login** to receive an authentication token via `/api/auth/login/`
3. **Include the token** in the `Authorization` header for all API requests
4. **Logout** (optional) via `/api/auth/logout/` to invalidate the token

### Token Format

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## ⚡ Special Features

### 1. Author Name Display

Comments display the **full name** of the author (first name + last name). If the user hasn't set their name, the **username** is displayed as a fallback.

**Example:**
```json
{
  "id": 1,
  "author": "Max Mustermann",  // or "max_mustermann" if name not set
  "content": "Great work!",
  "created_at": "2025-10-18T10:30:00Z"
}
```

### 2. Comments Count on Tasks

Tasks include a `comments_count` field that automatically calculates the number of comments.

```json
{
  "id": 1,
  "title": "Implement feature",
  "comments_count": 5
}
```

### 3. Role-Based Permissions

- **Board Owner**: Can delete the board and manage all tasks
- **Board Members**: Can create, view, and update tasks
- **Task Creator**: Can delete their own tasks
- **Comment Author**: Can delete their own comments

### 4. Nested URL Structure

Comments use a nested URL structure for better REST semantics:
```
/api/tasks/{task_id}/comments/{comment_id}/
```

### 5. Automatic Field Population

- **Task Creator**: Automatically set to the current user on task creation
- **Comment Author**: Automatically set to the current user on comment creation
- **Timestamps**: `created_at` and `updated_at` are automatically managed

## 🧪 Testing with Postman

### Setup

1. Import the API endpoints into Postman
2. Create an environment with:
   - `base_url`: `http://127.0.0.1:8000`
   - `token`: Your authentication token

### Test Flow

1. **Register** a new user
2. **Login** to get a token
3. **Create** a board
4. **Create** tasks on the board
5. **Add** comments to tasks
6. **Test** permissions (try to delete other users' comments)

## 🐛 Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
python manage.py runserver 8080
```

### Migration Issues

If you encounter migration errors:
```bash
python manage.py migrate --run-syncdb
```

### Reset Database

To start fresh (⚠️ **Warning**: This deletes all data):
```bash
# Delete the database file
rm db.sqlite3

# Recreate migrations
python manage.py migrate

# Create a new superuser
python manage.py createsuperuser
```

### Token Authentication Not Working

Make sure you're including the token correctly:
```
Authorization: Token <your-token-here>
```

**NOT:**
- `Bearer <token>`
- `Token: <token>`

## 🔧 Development Notes

### Creating Usernames in Admin

When creating users in Django Admin, remember:
- **Username**: Cannot contain spaces (use `max_mustermann` or `max.mustermann`)
- **First Name**: Can contain spaces (use `Max`)
- **Last Name**: Can contain spaces (use `Mustermann`)

### Task Status Choices

Available statuses:
- `to-do`
- `in-progress`
- `review`
- `done`

### Priority Choices

Available priorities:
- `low`
- `medium`
- `high`

## 📝 Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run migrations if you've changed models
4. Test your changes
5. Submit a pull request

## 📄 License

This project is part of a Developer Academy course.

## 👥 Contact

For questions or support, please me.

---

**Happy Coding! 🚀**
