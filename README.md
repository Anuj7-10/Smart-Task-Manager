# Smart Task Manager System

This is a Python-based web application built with Flask, PostgreSQL, and WebSockets.
Video Demonstration link - https://drive.google.com/file/d/1eg_pdVPQf02vX_TbdoAL421JllLzjidY/view?usp=sharing

## Setup Instructions
1. Clone this repository to your computer.
2. Create a virtual environment and activate it.
3. Install the required libraries: `pip install Flask Flask-SQLAlchemy psycopg2-binary pandas numpy Flask-SocketIO`
4. Create a PostgreSQL database named `task_manager_db`.
5. Open `app.py` and update the database password on line 10 to match your local PostgreSQL password.
6. Run the application: `python app.py`
7. Open your browser and navigate to `http://127.0.0.1:5000`