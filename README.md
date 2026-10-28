# 📚 Study Planner 

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web_Framework-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap">
</p>

<h3 align="center">
  🎯 Focus Smarter. Study Better. Achieve More.
</h3>

<p align="center">
  A modern, intelligent study planning web application designed to help students organize tasks, manage deadlines, and build structured study schedules.
  <br><br>
  Built with Python, Flask, and SQLite, featuring an automatic scheduling engine, interactive analytics, a visual study calendar, and an AI-powered study coach.
</p>

<p align="center">
  <strong>Plan your day. Stay consistent. Reach your goals. 🤍</strong>
</p>

---

## 📸 Screenshots

### 🏠 Dashboard

<p align="center">
 <img width="95%" alt="Study Planner Dashboard" src="https://github.com/user-attachments/assets/883d0105-d701-44a4-8eb2-8e78d0a12101" />

</p>

### 🔐 Authentication

<p align="center">
  <img src="https://github.com/user-attachments/assets/f9f07e7d-68b8-4bf2-91fe-62061362f8ee" width="45%" alt="Login Page">

  &nbsp;
  <img src="https://github.com/user-attachments/assets/8bb3c5f7-aa2d-424f-a722-d76241d756d3" width="45%" alt="Registration Page">

</p>

### 👑 Premium Experience

<p align="center">
  <img src="https://github.com/user-attachments/assets/1f289be1-41b5-403e-8f08-1a50c6d8d7da" width="45%" alt="Premium Activation Page">

  &nbsp;
  <img src="https://github.com/user-attachments/assets/70e9a758-7a9c-47e2-a8f7-21e1aa3bdb44" width="45%" alt="AI Study Coach">

</p>

---

## 📖 About the Project

**Study Planner** is a Flask-based web application that helps students take control of their academic workload through intelligent task organization and automated study scheduling.

Instead of manually deciding what to study next, students can manage their assignments, quizzes, and exams in one place while the scheduling engine organizes their tasks according to priority and upcoming deadlines.

The application also offers a Premium experience with interactive analytics, a calendar-based schedule, and an AI Study Coach to help students develop better study habits.

### 💡 Why Study Planner?

- 📌 **Stay Organized:** Keep all your academic tasks in one place.
- ⏰ **Never Miss a Deadline:** Identify overdue tasks and upcoming deadlines.
- 🧠 **Study Strategically:** Prioritize important tasks automatically.
- ☕ **Take Meaningful Breaks:** Include breaks between scheduled study sessions.
- 📊 **Track Your Progress:** Visualize task completion and remaining workload.
- 🤖 **Get Personalized Guidance:** Use the AI Study Coach for study planning advice.

---

## ✨ Features

### ⏱️ 1. Intelligent Study Scheduling

Turn your task list into an organized study plan.

- Automatically generates sequential study sessions.
- Prioritizes tasks according to priority and deadline.
- Schedules study blocks starting from the current time.
- Includes 15-minute breaks between study sessions.
- Recalculates the schedule when tasks are added, updated, or completed.

### 📝 2. Smart Task Management

Manage your academic responsibilities from a single dashboard.

- Create and organize assignments, quizzes, and exams.
- Track task status and completion.
- Identify overdue tasks.
- Highlight tasks due within the next 24 hours.
- Quickly mark tasks as completed or delete them.
- Keep your workload visible and manageable.

### 🔐 3. User Authentication

A personalized experience for managing study activities.

- User registration and login.
- Session-based authentication.
- Dedicated dashboard access.
- Account-specific task management, where supported by the application.

### 👑 4. Premium Pro Suite

Unlock additional tools designed to make studying more effective.

| Feature | Description |
|---|---|
| 📊 Analytics Dashboard | Visualize task distribution, completion rates, and estimated remaining study hours. |
| 📅 Interactive Calendar | Explore scheduled study sessions in a monthly or weekly calendar. |
| 🤖 AI Study Coach | Get AI-generated suggestions for prioritization, productivity, and study habits. |
| 🔓 Premium Activation | Access Premium features through the application's activation system. |

### 📊 5. Interactive Analytics

Understand your academic progress at a glance.

- Visual charts powered by Chart.js.
- Overview of task distribution.
- Progress and completion statistics.
- Estimated remaining study workload.

### 📅 6. Visual Study Calendar

See your study plan in a calendar-based interface.

- Display generated study sessions visually.
- Navigate between calendar views.
- Understand how study sessions are distributed over time.
- Plan your workload with a clearer view of upcoming activities.

### 🤖 7. AI Study Coach

Get study guidance with the help of an AI-powered assistant.

- Ask questions about study planning and productivity.
- Get suggestions for prioritizing academic tasks.
- Explore strategies for managing deadlines.
- Receive study recommendations through OpenRouter integration.

*AI responses depend on the configured API provider, model, and application implementation.*

---

## 🛠️ Tech Stack

Study Planner combines lightweight backend technologies with modern frontend libraries.

| Technology | Purpose |
|---|---|
| 🐍 Python | Core programming language |
| 🌶️ Flask | Web framework and application routing |
| 🗄️ SQLite | Relational database |
| 🎨 Bootstrap 5 | Responsive interface and UI components |
| 📈 Chart.js | Interactive analytics and charts |
| 📅 FullCalendar | Calendar-based study schedule |
| 🤖 OpenRouter API | AI Study Coach integration |
| 🧩 Jinja2 | Dynamic HTML templating |
| 🔐 Flask Sessions | User session management |

---

## 🏗️ Project Architecture

The application uses a straightforward structure that separates backend logic, database operations, and frontend templates.

```text
study-planner/
│
├── app.py
│   └── Flask application, routes, authentication,
│       session management, and scheduling logic
│
├── database.py
│   └── SQLite configuration, schema creation,
│       and database initialization
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── premium.html
│   ├── analytics.html
│   ├── calendar.html
│   └── ai_recommendations.html
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

Follow these steps to run Study Planner locally.

### 📋 Prerequisites

Make sure you have the following installed:

- Python 3.8 or later.
- Git.
- pip, Python's package installer.
- An OpenRouter API key if you want to use the AI Study Coach.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/study-planner.git
```

Replace `your-username` with your GitHub username.

### 2️⃣ Navigate to the Project Directory

```bash
cd study-planner
```

### 3️⃣ Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4️⃣ Install Dependencies

If your project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies required by your application. For a basic Flask setup:

```bash
pip install flask
```

Additional packages may be needed depending on your implementation.


### 5️⃣ Initialize the Database

If `database.py` creates the database and initializes the required tables, run:

```bash
python database.py
```

### 6️⃣ Start the Application

```bash
python app.py
```

### 7️⃣ Open the Application

Visit the following address in your browser:

**http://127.0.0.1:5000**

You're ready to start organizing your study schedule! 🎉

---

## 🔑 Demo Credentials

If you have initialized the database with the demo data described in your project, you can use the following credentials:

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `password123` |
| Premium Activation Code | `0000` |

> ⚠️ **Important:** These are example credentials, not verified live account details. Use them only if your database initialization script creates this demo account. Never use these credentials for a production deployment.

---

## 🗺️ Project Roadmap

### ✅ Implemented

- [x] Automatic study scheduling.
- [x] Task prioritization by priority and deadline.
- [x] Scheduled breaks between study sessions.
- [x] Task completion and deletion.
- [x] Overdue task indicators.
- [x] Upcoming deadline notifications.
- [x] User registration and login.
- [x] Session management.
- [x] Premium activation system.
- [x] Analytics dashboard with Chart.js.
- [x] Interactive study calendar.
- [x] OpenRouter-powered AI Study Coach.

### 🚧 Planned Improvements

- [ ] Customizable study session durations.
- [ ] User-defined break intervals.
- [ ] Push notifications for upcoming study sessions.
- [ ] Subject-based task filtering.
- [ ] Recurring study sessions.
- [ ] Improved mobile dashboard experience.
- [ ] Study streaks and daily goals.
- [ ] Export schedules to external calendars.
- [ ] Enhanced analytics and personalized progress reports.

---

## 🔒 Security Considerations

For a safer deployment, consider the following:

- Store passwords using a secure password-hashing method.
- Keep API keys in environment variables.
- Use a strong, randomly generated Flask secret key.
- Validate and sanitize user input.
- Ensure users can access only their own private tasks.
- Protect state-changing operations against CSRF attacks.
- Disable Flask debug mode in production.
- Replace demo credentials before deploying publicly.

---

## 🤝 Contributing

Contributions, suggestions, bug reports, and feature requests are welcome!

To contribute:

1. Fork the repository.
2. Create a new branch:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes.
4. Commit your work:

   ```bash
   git commit -m "Add: your feature"
   ```

5. Push your branch:

   ```bash
   git push origin feature/your-feature
   ```

6. Open a Pull Request.

Please ensure your changes are tested and documented where appropriate.

---


## 🌟 Support the Project

If you find Study Planner useful:

- ⭐ Star the repository on GitHub.
- 🐛 Report bugs and suggest improvements.
- 💡 Contribute new features.
- 📢 Share the project with other students.

Every contribution helps make studying more organized and productive!

---

<p align="center">
  <strong>📚 Study Planner</strong>
  <br>
  Focus Smarter. Study Better. Achieve More.
  <br><br>
  Made with 🤍 and Python.
</p>
