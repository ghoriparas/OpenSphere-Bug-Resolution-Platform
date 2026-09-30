# OpenSphere - Bug Resolution Platform

OpenSphere is a full-stack open-source issue tracking and project management platform built with **Python**, **Flask**, and **SQLite**. It enables developer teams to organize repositories, log bug tickets, prioritize workloads, collaborate through ticket discussions, and manage tasks using an Agile Kanban board.

---

## Features

- **User Authentication & Role-Based Access (RBAC)**: Secure registration and login with Admin and Developer roles. Passwords are encrypted using salted PBKDF2-SHA256 hashing.
- **Project & Repository Hub**: Create and maintain software projects with technology stack tags, descriptions, and linked repository URLs.
- **Issue Tracking & Multi-Parameter Search**: Log bugs, feature requests, and technical tasks. Filter issues by Status (`Open`, `In Progress`, `Resolved`, `Closed`), Priority (`Low`, `Medium`, `High`, `Critical`), Project, or keywords.
- **Agile Kanban Board**: Visual drag-and-drop task workflow with asynchronous status updates via a REST API.
- **Developer Discussion Threads**: Real-time commenting on bug tickets for collaborative troubleshooting and fix verification.
- **Analytics Dashboard**: Interactive Chart.js visual telemetry including lifecycle doughnut charts and priority bar graphs.
- **CSV Report Export**: Single-click export of filtered issue data to CSV spreadsheets.

---

## Technology Stack

- **Backend**: Python 3.10+, Flask 3.x
- **Database & ORM**: SQLite 3, Flask-SQLAlchemy
- **Authentication**: Werkzeug Security (PBKDF2-SHA256)
- **Frontend**: Semantic HTML5, Custom CSS3, Vanilla JavaScript (ES6+)
- **Charts**: Chart.js 4.x

---

## Project Structure

```text
├── app.py              # Main Flask application with routes and API endpoints
├── models.py           # SQLAlchemy models (User, Project, Issue, Comment)
├── seed_data.py        # Database seeder script with demo data
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # Project documentation
├── templates/          # Jinja2 HTML templates
└── static/
    ├── css/style.css   # Custom CSS styling
    └── js/main.js      # Client-side scripts & Kanban drag-drop logic
```

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/ghoriparas/OpenSphere-Bug-Resolution-Platform.git
cd OpenSphere-Bug-Resolution-Platform
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database with Demo Data
```bash
python seed_data.py
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## Default Login Credentials

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Admin | Project Manager (Full administrative access) |
| `paras` | `paras123` | Developer | Developer (Report, update, and comment on issues) |
| `rahul` | `rahul123` | Developer | Developer account |

*(You can also create a new account from the Register page)*

---

## License

This project is open-source and available under the [MIT License](LICENSE).
