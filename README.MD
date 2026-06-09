# Habit Tracker

A full-stack Habit Tracking Web Application built using Python, Flask, MongoDB Atlas, and REST APIs.

## Features

* User Registration and Login
* Create New Habits
* View All Habits
* Update Existing Habits
* Delete Habits
* Habit Tracking Dashboard
* MongoDB Database Integration
* REST API Architecture

## Technologies Used

* Python
* Flask
* MongoDB Atlas
* Flask-PyMongo
* HTML
* CSS
* JavaScript
* Render (Deployment)
* Git & GitHub

## Project Structure

```text
HabitTracker/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── __init__.py
│
├── requirements.txt
├── Procfile
├── run.py
└── README.md
```

## Live Demo

https://habittracker-1-wyji.onrender.com

## GitHub Repository

https://github.com/bhavadharini786-ux/HabitTracker

## Installation

1. Clone the repository

```bash
git clone https://github.com/bhavadharini786-ux/HabitTracker.git
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the environment

```bash
venv\Scripts\activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Configure environment variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_connection_string
```

6. Run the application

```bash
python run.py
```

## Author

Bhavadharini

Developed as a CRUD-based Habit Tracking application using Flask, MongoDB Atlas, and REST APIs.
