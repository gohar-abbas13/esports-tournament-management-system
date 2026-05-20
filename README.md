# eSports Tournament Management System

A complete 2nd-year database project using MySQL/MariaDB, Python Flask, and HTML/CSS.

## Improved Features

- Admin dashboard with total teams, players, tournaments, matches, completed matches, and upcoming matches
- Admin login/logout
- Search on teams, players, tournaments, and matches
- Add teams, players, tournaments, and matches from the website
- Record/update match scores
- Automatic winner calculation
- Points table calculated from match results
- Backend validation for same-team matches, invalid dates, negative scores, and invalid emails
- Improved UI with cards, badges, tables, navbar, and footer

## Admin Login

Default credentials:

- Username: `admin`
- Password: `admin123`

You can change these in `.env`.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Final Extra Improvements Added

This final version also includes:

- Reports page for tournament summary and recent results
- CSV export for Players, Teams, Tournaments, Matches, and Points Table
- Delete actions for admin users on Players, Teams, Tournaments, and Matches
- Safer delete handling when a record is connected through foreign keys

These features make the project stronger for demonstration because they show CRUD operations, reporting, and practical data export.
