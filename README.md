# Soufflé — Baking Courses Web App 

Find, explore, and contact the owner for your favorite baking courses, all in one place.

## 📑 Table of Contents

-   [Overview](#-overview)
-   [Features](#-features)
-   [Tech Stack](#-tech-stack)
-   [Quick Start](#-quick-start)

---

## 📝 Overview

**Soufflé** is a lightweight web application built with **Django** where baking enthusiasts can:

-   Browse a catalog of courses by category.
-   View complete details for each course, including description and pricing.
-   Contact the owner directly via WhatsApp.
-   (Coming Soon) Schedule and purchase courses securely.

Whether you're looking to perfect a technique or start from scratch, Soufflé connects you with the training you need quickly and easily.

---

## ✨ Features

| Category              | What it does                                                                       |
| :-------------------- | :--------------------------------------------------------------------------------- |
| **Course Discovery** 🍰 | Lists all available courses with their image, a brief description, and price.      |
| **Detailed View** 📜    | A dedicated page for each course with full information on the course. |
| **Direct Contact** 📱   | A button to start a WhatsApp conversation with the owner to ask questions instantly. |
| **Authentication** 🔐   | Secure user registration, login, and logout system.                                |
| **Roadmap** 🛣️        | Coming Soon: online scheduling and user reviews.     |

---

## 🛠️ Tech Stack

-   **Language & Framework**: Python 3.12 · Django
-   **Frontend**: Bootstrap 5
-   **Database**: SQLite (swap for PostgreSQL/MySQL in production)

---

## 🚀 Quick Start

1.  **Clone the repository**
    ```bash
    git clone https://github.com/CSM-Coders/Souffle.git
    cd souffle
    ```

2.  **Set up the virtual environment**
    ```bash
    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # On Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server**
    ```bash
    python manage.py runserver
    ```
    Open your browser to **`http://127.0.0.1:8000/`**

---
