# Smart-Task-Manager

Overview
The Smart Task Management System is a robust, full-stack Python web application designed to help users efficiently track and manage their daily workflows. Built with Flask and PostgreSQL, it features secure user authentication and persistent data storage.

Beyond standard CRUD operations, this project implements advanced features including real-time, bi-directional client-server communication via WebSockets, allowing the dashboard to update instantaneously across multiple browser windows. Additionally, it leverages Python's powerful data science libraries (Pandas and NumPy) to provide users with a live, calculating analytics dashboard of their productivity.

Key Features:

Secure Authentication: User registration and login utilizing Flask-Session and Werkzeug password hashing.

Real-Time Synchronization: Live updates using Flask-SocketIO. When a task is added, updated, or deleted, the DOM is dynamically manipulated via JavaScript to reflect changes instantly without page reloads.

Analytics Engine: Utilizes Pandas DataFrames and NumPy to calculate and render real-time statistics (Total Tasks, Completed/Pending counts, and Completion Percentage).

Relational Database: Designed and integrated a PostgreSQL database using Flask-SQLAlchemy to handle one-to-many relationships between Users and Tasks.

Clean UI: A lightweight, responsive HTML/CSS frontend with a focus on usability and clear data presentation.

Technology Stack:

Backend: Python, Flask, Flask-SQLAlchemy, Flask-SocketIO

Database: PostgreSQL

Data Analytics: Pandas, NumPy

Frontend: HTML5, CSS, Vanilla JavaScript