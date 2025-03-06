my_project/
│── app/
│   ├── server.py           # Flask API (Handles user submissions)
│   ├── tasks.py            # Celery Worker (Processes AI tasks)
│   ├── config.py           # Configuration settings (PostgreSQL, Redis, AI)
│── database/
│   ├── schema.sql          # SQL script to create tables in PostgreSQL
│   ├── db_setup.py         # Python script to initialize the database
│── .venv/                  # Virtual environment (Python dependencies)
│── requirements.txt        # Python dependencies (Flask, Celery, Redis, PostgreSQL)
│── README.md               # Documentation (How to set up and run)
│── docker-compose.yml      # (Optional) To deploy Redis, Celery, PostgreSQL together
