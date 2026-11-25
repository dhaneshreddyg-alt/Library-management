# Library Management System — Full Stack Web Application

This project converts the supplied Python/Tkinter Library Management System into a browser-based full-stack application.

## Technology stack
- **Frontend:** HTML5, CSS3, JavaScript, responsive dashboard
- **Backend:** Python Flask
- **Database:** SQLite (`library.db`, created automatically)

## Features
- Add books with title, author and total copy count
- Search inventory by book title or author
- Issue one or more copies to a named borrower
- Automatic 14-day due date
- Track active loans and overdue items
- Return issued copies and calculate late fine at ₹2 per copy per day
- Delete books when there are no active loans
- Dashboard counts for titles, copies, issued and available stock
- JSON endpoint: `GET /api/books`

## Run locally
1. Install Python 3.9 or newer.
2. Extract this ZIP and open a terminal in the project folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the website: `python app.py`
6. Open **http://127.0.0.1:5000** in your browser.

The database file is created in the project folder on first run. Back it up to preserve library data.

## Project structure
```
library_fullstack/
├── app.py
├── library.db             # created automatically
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

## Notes
This is a local development setup. Before public deployment, set a strong secret key, turn off Flask debug mode, and configure production hosting and backups.
