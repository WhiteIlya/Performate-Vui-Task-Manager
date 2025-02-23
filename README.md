# PerforMate - Persuasive Voice Assistant for Task Management

## Overview

**PerforMate** is a voice-driven task management assistant designed to help users effectively manage their time and productivity through persuasive voice interaction. By leveraging **OpenAI** and **Eleven Labs**, the assistant dynamically adapts to user preferences, providing motivational reminders, task organization, and behavioral nudges to support better time management. The assistant is customizable in tone, assertiveness, and personality, offering a tailored experience for each user.

The application is built with a **Django backend** and a **React (TypeScript) frontend**, ensuring a robust and scalable system that integrates voice input for seamless task management.

---

## Features

- **Voice-Driven Task Management**: Users can add, update, and delete tasks using voice commands.
- **Adaptive Personalization**: Customizable voice assistant behavior, including assertiveness, motivational feedback, and communication style.
- **Multi-Modal Notifications**: Audio reminders are reinforced with visual notifications for increased reliability.
- **Task Decomposition**: The assistant suggests breaking large tasks into smaller, manageable steps.
- **Cross-Platform Support**: Accessible via desktop and mobile browsers.
- **Context-Aware Interactions**: The assistant retains conversation context for more natural, efficient interactions.


---

## Installation Guide

### Backend (Django)

#### 1. Setup Environment Variables

Create a `.env` file in the `backend/` directory and add the following:

- DB_NAME=your_database_name
- DB_USER=your_database_user 
- DB_PASSWORD=your_database_password 
- DB_HOST=your_database_host 
- DB_PORT=your_database_port

- ELEVEN_LABS_API_KEY=your_eleven_labs_api_key
- OPENAI_API_KEY=your_openai_api_key

- SECRET_KEY=your_django_secret_key


#### 2. Install Dependencies

Ensure you have **Python 3.9+** and **PostgreSQL** installed. Then, run:

```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

3. Apply Migrations
```sh
python manage.py migrate
```
4. Create a Superuser (Optional)
```sh
python manage.py createsuperuser
```
5. Run the Server
```sh
python manage.py runserver

The backend will be accessible at http://127.0.0.1:8000/.
```

### Frontend (React + TypeScript + Vite)

#### 1. Setup Environment Variables

Create a .env file in the frontend/ directory and add:

- VITE_API_URL=http://127.0.0.1:8000/api

#### 2. Install Dependencies

Ensure you have Node.js (16+) installed, then run


```sh
cd frontend
npm install
```

3. Start the Development Server

```sh
npm run dev
```
