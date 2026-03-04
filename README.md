# 📚 EPIC EVENTS CRM

**Epic Events CRM** is a command-line Customer Relationship Management application designed to manage clients, contracts, and events for the Epic Events company.

The application allows different departments (Management, Sales, and Support) to collaborate while respecting strict role-based permissions.
Sales teams manage clients and contracts, management supervises operations, and support teams handle event logistics once a contract is signed.

The system provides secure authentication, role-based access control, and a structured workflow to ensure that clients, contracts, and events are managed consistently throughout their lifecycle.

---

## 📚 Table of Contents

- [Features](#-features)
- [Application Architecture](#-application-architecture)
- [Installation Guide](#-installation-guide)
- [Launch the Application](#-launch-the-application)
- [Security and Permissions](#-security-and-permissions)
- [Logging (Sentry)](#-logging-sentry)
- [Tests](#-tests)
- [Built With](#-built-with)
- [Author](#-author)
- [License](#-license)

---

## 🚀 Features

- Secure CLI authentication with role-based access control
  (Management, Sales, Support).

- Client management
  - Create new clients (assigned automatically to the logged-in sales contact)
  - Update client information with ownership restrictions
  - View the list of all registered clients

- Contract management
  - Create new contracts linked to clients
  - Update contracts depending on user permissions
  - Track contract status (signed / unsigned)
  - Identify unpaid contracts

- Event management
  - Create events only for signed contracts
  - Assign support contacts to events
  - Update event information
  - Filter events (e.g., events without support contact)

- Department workflow
  - Sales manage clients and commercial relationships
  - Management supervises contracts and event assignments
  - Support teams manage operational event details

- Secure database interactions using SQLAlchemy ORM to prevent SQL injection.

- Error monitoring and logging with Sentry.

## 🧠 Application Architecture

Epic Events CRM is a Python command-line application organized around a
layered architecture inspired by the MVC pattern. This structure promotes
clear separation of responsibilities between data models, business logic,
and user interaction.

- **Models** define database entities (User, Client, Contract, Event).
- **Controllers** implement application business logic.
- **Views** manage the command-line user interface.
- **Repositories** handle database access.
- **Services** provide shared business utilities (auth, permissions).
- **Database** manages connection and session configuration.
- **Tests** validate authentication, permissions, and workflows.

Here is the overall project layout:

epic_events_crm/
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── config/                   # Application configuration
├── database/                 # Database setup and initialization
├── models/                   # ORM entities
├── controllers/              # Business logic
├── repositories/             # Data access layer
├── services/                 # Shared services (auth, permissions, logging)
├── views/                    # CLI user interface
├── tests/                    # Automated tests
└── main.py                   # Application entry point

---

## 🚀 Installation Guide

#### Prerequisites
- Python 3.11+ installed and available as `python3`
- `pip` available (`python3 -m pip`)
- MySQL server installed (configuration covered in the next section)

> 🐧 **Note macOS/Linux**
> On Linux/Mac, the `python` command may not be available by default.
> Use `python3` instead:

Clone the repository from GitHub:

```bash
git clone https://github.com/DomiCarr/OCR_P12_CRM
cd OCR_P12_CRM
```

### 🛠️ Set up the virtual environment

Create and activate the virtual environment before installing packages or running the application.

Create:

```bash
python -m venv env
# If python doesn't work, use python3:
python3 -m venv env
```

Activate:

- **On macOS/Linux**
  ```bash
  source env/bin/activate
  ```

- **On Windows (CMD)**
  ```cmd
  env\Scripts\activate
  ```

- **On Windows (PowerShell)**
  ```powershell
  .\env\Scripts\Activate.ps1
  ```

> 📝 **Note (PowerShell)**
> If you get an error like
> **“running scripts is disabled on this system”**,
> open PowerShell as administrator and run:
>
> ```powershell
> Set-ExecutionPolicy RemoteSigned
> ```
>
> Then confirm with `Y` to allow local scripts to run.


### 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### ✅ Verify installation

Run the following to confirm packages are installed:

```bash
pip freeze
```

Expected output includes:

```text
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
certifi==2026.1.4
cffi==2.0.0
coverage==7.13.4
iniconfig==2.3.0
mysql-connector-python==9.6.0
packaging==26.0
pluggy==1.6.0
pycparser==3.0
Pygments==2.19.2
PyJWT==2.11.0
pytest==9.0.2
pytest-cov==7.0.0
python-dotenv==1.2.1
sentry-sdk==2.53.0
SQLAlchemy==2.0.46
typing_extensions==4.15.0
urllib3==2.6.3
```

### ⚙️ Configure environment variables

Create the `.env` file from the provided example:

```bash
cp .env_example .env
```

Then edit the file to configure your environment variables:

```env
# =========================
# Database Configuration
# =========================

# MySQL database username used by the application
DB_USER=

# Password associated with DB_USER
DB_PASSWORD=

# Database host (localhost when running locally)
DB_HOST=

# MySQL server port
DB_PORT=

# Database name used by the CRM
DB_NAME=


# =========================
# Security and Authentication
# =========================

# Global secret used for application security features
SECRET_KEY=


# =========================
# JWT Configuration
# =========================

# Secret used to sign and verify JWT tokens
JWT_SECRET=

# Algorithm used for JWT token signing
JWT_ALGORITHM=


# =========================
# Error Monitoring (Sentry)
# =========================

# Sentry DSN used to send error reports to the monitoring service
SENTRY_DSN=
```


### 🏃 Prepare the database and run the Django Development Server

From the project root:

```bash
# If python doesn't work, use python3

# Apply all migrations to initialize the database
python manage.py migrate

# (Optional) Create a superuser for Django admin
# You will be prompted to enter username, email, and password
python manage.py createsuperuser

# Run the Django development server
python manage.py runserver

```

### 🗄️ Database Setup

The project provides SQL scripts in the `database/` directory to create the
database, create the application user, and seed initial employees.

#### 1) Start MySQL and connect as an admin user

```bash
mysql --version
```

Connect (adjust host/port if needed):

```bash
mysql -u root -p -h localhost -P 3307
```

#### 2) Create the database and application user

From the MySQL prompt:

```sql
SOURCE database/create_database.sql;
```

Or from your shell (alternative):

```bash
mysql -u root -p -h localhost -P 3307 < database/create_database.sql
```

#### 3) Create initial departments and employees

From the MySQL prompt:

```sql
USE epic_events_db;
SOURCE database/init_db_employees.sql;
```

Or from your shell (alternative):

```bash
mysql -u root -p -h localhost -P 3307 epic_events_db \
  < database/init_db_employees.sql
```

#### 4) Update your `.env`

Ensure your `.env` values match your MySQL configuration:

```env
DB_HOST=localhost
DB_PORT=3307
DB_NAME=epic_events_db
DB_USER=crm_user
DB_PASSWORD=...
```

🌐 Access the application

Open your browser and go to http://127.0.0.1:8000/

---

## 🧪 Code Quality Report (Flake8)
To ensure code quality and compliance with PEP8 standards, this project uses
**Flake8** through the **VSCode Flake8 extension**, which provides real-time
linting directly in the editor during development.

---

## 📡 Logging (Sentry)

This project uses **Sentry** to capture and report runtime exceptions.

### Configuration

Set the `SENTRY_DSN` variable in your `.env`:

```env
SENTRY_DSN=
```

- If `SENTRY_DSN` is empty, Sentry reporting is disabled.
- If `SENTRY_DSN` is set, unhandled exceptions are sent to Sentry.

### Verify

To validate the integration, run the application and trigger an error
intentionally (e.g., invalid command). Check your Sentry dashboard for the
event.


## 🧪 Tests

The project uses **pytest** for automated testing.

### Run the test suite with coverage

```bash
python -m pytest --cov=app --cov-report=term tests/
```

This command:

- runs all tests located in the `tests/` directory
- measures coverage on the `app` package
- displays the coverage report directly in the terminal

## 🧰 Built With

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

- **Python** — main programming language
- **MVC (Model–View–Controller)** — architectural pattern used to separate concerns between data (Model), user interface (View), and logic (Controller)
**Cross-platform compatibility** — works on 🐧 Linux, 🍎 macOS, and 🪟 Windows


---

## 📦 Releases

- **Version 1.0** — Initial release

---

## 👤 Author

**Dominique Carrasco**
GitHub: [@DomiCarr](https://github.com/DomiCarr)

---

## 📄 License

This project is licensed under the [OpenClassrooms Terms & Conditions](https://openclassrooms.com/fr/policies/terms-conditions)
