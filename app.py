from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from functools import wraps
import os
import csv
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "esports_tournament_db"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def fetch_one(query, params=None):
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()



def csv_response(filename, rows):
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("No data found\n")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login as admin to use management features.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_login_status():
    return {"admin_logged_in": session.get("admin_logged_in", False)}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/")
def dashboard():
    try:
        stats = {
            "teams": fetch_one("SELECT COUNT(*) AS total FROM Teams")["total"],
            "players": fetch_one("SELECT COUNT(*) AS total FROM Players")["total"],
            "tournaments": fetch_one("SELECT COUNT(*) AS total FROM Tournaments")["total"],
            "matches": fetch_one("SELECT COUNT(*) AS total FROM Matches")["total"],
            "completed": fetch_one("SELECT COUNT(*) AS total FROM Matches WHERE match_status='Completed'")["total"],
            "upcoming": fetch_one("SELECT COUNT(*) AS total FROM Matches WHERE match_status='Scheduled'")["total"],
        }
        matches = fetch_all("SELECT * FROM v_match_results ORDER BY match_date DESC LIMIT 5")
        tournaments = fetch_all("""
            SELECT t.tournament_id, t.tournament_name, g.game_name, t.start_date, t.end_date, t.status
            FROM Tournaments t JOIN Games g ON t.game_id = g.game_id
            ORDER BY t.start_date LIMIT 5
        """)
        top_points = fetch_all(points_query() + " LIMIT 5")
        return render_template("dashboard.html", stats=stats, matches=matches, tournaments=tournaments, top_points=top_points)
    except Error as e:
        return render_template("error.html", error=e)


@app.route("/teams", methods=["GET", "POST"])
def teams():
    if request.method == "POST":
        if not session.get("admin_logged_in"):
            flash("Please login before adding a team.", "warning")
            return redirect(url_for("login"))
        try:
            team_name = request.form["team_name"].strip()
            city = request.form.get("city", "").strip()
            coach_name = request.form.get("coach_name", "").strip()
            if len(team_name) < 2:
                flash("Team name must be at least 2 characters.", "danger")
            else:
                execute_query(
                    "INSERT INTO Teams (team_name, city, coach_name) VALUES (%s, %s, %s)",
                    (team_name, city, coach_name),
                )
                flash("Team added successfully.", "success")
        except Error as e:
            flash(str(e), "danger")
        return redirect(url_for("teams"))

    q = request.args.get("q", "").strip()
    if q:
        rows = fetch_all("""
            SELECT * FROM Teams
            WHERE team_name LIKE %s OR city LIKE %s OR coach_name LIKE %s
            ORDER BY team_name
        """, (f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        rows = fetch_all("SELECT * FROM Teams ORDER BY team_name")
    return render_template("teams.html", teams=rows, q=q)


@app.route("/players", methods=["GET", "POST"])
def players():
    if request.method == "POST":
        if not session.get("admin_logged_in"):
            flash("Please login before adding a player.", "warning")
            return redirect(url_for("login"))
        try:
            player_name = request.form["player_name"].strip()
            gamer_tag = request.form["gamer_tag"].strip()
            email = request.form.get("email", "").strip() or None
            if len(player_name) < 2 or len(gamer_tag) < 2:
                flash("Player name and gamer tag must be at least 2 characters.", "danger")
            elif email and "@" not in email:
                flash("Please enter a valid email address.", "danger")
            else:
                execute_query(
                    """
                    INSERT INTO Players (player_name, gamer_tag, email, phone, country, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        player_name,
                        gamer_tag,
                        email,
                        request.form.get("phone", "").strip() or None,
                        request.form.get("country", "Pakistan").strip() or "Pakistan",
                        request.form.get("date_of_birth") or None,
                    ),
                )
                flash("Player added successfully.", "success")
        except Error as e:
            flash(str(e), "danger")
        return redirect(url_for("players"))

    q = request.args.get("q", "").strip()
    if q:
        rows = fetch_all("""
            SELECT * FROM Players
            WHERE player_name LIKE %s OR gamer_tag LIKE %s OR email LIKE %s OR country LIKE %s
            ORDER BY player_name
        """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        rows = fetch_all("SELECT * FROM Players ORDER BY player_name")
    return render_template("players.html", players=rows, q=q)


@app.route("/tournaments", methods=["GET", "POST"])
def tournaments():
    if request.method == "POST":
        if not session.get("admin_logged_in"):
            flash("Please login before adding a tournament.", "warning")
            return redirect(url_for("login"))
        try:
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            prize_pool = float(request.form.get("prize_pool") or 0)
            if end_date < start_date:
                flash("End date cannot be before start date.", "danger")
            elif prize_pool < 0:
                flash("Prize pool cannot be negative.", "danger")
            else:
                execute_query("""
                    INSERT INTO Tournaments (tournament_name, game_id, start_date, end_date, prize_pool, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request.form["tournament_name"].strip(),
                    request.form["game_id"],
                    start_date,
                    end_date,
                    prize_pool,
                    request.form.get("status", "Upcoming"),
                ))
                flash("Tournament added successfully.", "success")
        except (Error, ValueError) as e:
            flash(str(e), "danger")
        return redirect(url_for("tournaments"))

    q = request.args.get("q", "").strip()
    games = fetch_all("SELECT * FROM Games ORDER BY game_name")
    if q:
        rows = fetch_all("""
            SELECT t.*, g.game_name
            FROM Tournaments t JOIN Games g ON t.game_id = g.game_id
            WHERE t.tournament_name LIKE %s OR g.game_name LIKE %s OR t.status LIKE %s
            ORDER BY t.start_date
        """, (f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        rows = fetch_all("""
            SELECT t.*, g.game_name
            FROM Tournaments t JOIN Games g ON t.game_id = g.game_id
            ORDER BY t.start_date
        """)
    return render_template("tournaments.html", tournaments=rows, games=games, q=q)


@app.route("/matches", methods=["GET", "POST"])
def matches():
    if request.method == "POST":
        if not session.get("admin_logged_in"):
            flash("Please login before scheduling a match.", "warning")
            return redirect(url_for("login"))
        try:
            team1_id = request.form["team1_id"]
            team2_id = request.form["team2_id"]
            if team1_id == team2_id:
                flash("Team 1 and Team 2 cannot be the same.", "danger")
            else:
                execute_query("""
                    INSERT INTO Matches (tournament_id, venue_id, team1_id, team2_id, match_date, round_name, match_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    request.form["tournament_id"],
                    request.form.get("venue_id") or None,
                    team1_id,
                    team2_id,
                    request.form["match_date"],
                    request.form.get("round_name", "Round 1"),
                    request.form.get("match_status", "Scheduled"),
                ))
                flash("Match scheduled successfully.", "success")
        except Error as e:
            flash(str(e), "danger")
        return redirect(url_for("matches"))

    q = request.args.get("q", "").strip()
    if q:
        rows = fetch_all("""
            SELECT * FROM v_match_results
            WHERE tournament_name LIKE %s OR game_name LIKE %s OR team1 LIKE %s OR team2 LIKE %s OR winner LIKE %s OR round_name LIKE %s
            ORDER BY match_date
        """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        rows = fetch_all("SELECT * FROM v_match_results ORDER BY match_date")
    tournaments_list = fetch_all("SELECT tournament_id, tournament_name FROM Tournaments ORDER BY tournament_name")
    teams_list = fetch_all("SELECT team_id, team_name FROM Teams ORDER BY team_name")
    venues_list = fetch_all("SELECT venue_id, venue_name FROM Venues ORDER BY venue_name")
    return render_template("matches.html", matches=rows, q=q, tournaments_list=tournaments_list, teams_list=teams_list, venues_list=venues_list)


@app.route("/scores", methods=["GET", "POST"])
def scores():
    if request.method == "POST":
        if not session.get("admin_logged_in"):
            flash("Please login before recording a score.", "warning")
            return redirect(url_for("login"))
        try:
            match_id = request.form["match_id"]
            team1_score = int(request.form.get("team1_score") or 0)
            team2_score = int(request.form.get("team2_score") or 0)
            if team1_score < 0 or team2_score < 0:
                flash("Scores cannot be negative.", "danger")
            else:
                match = fetch_one("SELECT team1_id, team2_id FROM Matches WHERE match_id=%s", (match_id,))
                winner_team_id = None
                if team1_score > team2_score:
                    winner_team_id = match["team1_id"]
                elif team2_score > team1_score:
                    winner_team_id = match["team2_id"]
                execute_query("""
                    INSERT INTO MatchScores (match_id, team1_score, team2_score, winner_team_id, remarks)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    team1_score=VALUES(team1_score), team2_score=VALUES(team2_score),
                    winner_team_id=VALUES(winner_team_id), remarks=VALUES(remarks)
                """, (match_id, team1_score, team2_score, winner_team_id, request.form.get("remarks", "").strip()))
                execute_query("UPDATE Matches SET match_status='Completed' WHERE match_id=%s", (match_id,))
                flash("Score saved successfully.", "success")
        except (Error, ValueError, TypeError) as e:
            flash(str(e), "danger")
        return redirect(url_for("scores"))

    matches_list = fetch_all("""
        SELECT m.match_id, t.tournament_name, a.team_name AS team1, b.team_name AS team2, m.match_date
        FROM Matches m
        JOIN Tournaments t ON m.tournament_id=t.tournament_id
        JOIN Teams a ON m.team1_id=a.team_id
        JOIN Teams b ON m.team2_id=b.team_id
        ORDER BY m.match_date DESC
    """)
    results = fetch_all("SELECT * FROM v_match_results ORDER BY match_date DESC")
    return render_template("scores.html", matches_list=matches_list, results=results)


def points_query():
    return """
        SELECT
            t.tournament_name,
            tm.team_name,
            COUNT(ms.match_id) AS played,
            SUM(CASE WHEN ms.winner_team_id = tm.team_id THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN ms.match_id IS NOT NULL AND (ms.winner_team_id IS NULL OR ms.winner_team_id <> tm.team_id) THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN ms.winner_team_id = tm.team_id THEN 3 ELSE 0 END) AS points
        FROM Registrations r
        JOIN Tournaments t ON r.tournament_id = t.tournament_id
        JOIN Teams tm ON r.team_id = tm.team_id
        LEFT JOIN Matches m ON m.tournament_id = r.tournament_id AND (m.team1_id = tm.team_id OR m.team2_id = tm.team_id)
        LEFT JOIN MatchScores ms ON ms.match_id = m.match_id
        WHERE r.registration_status = 'Approved'
        GROUP BY t.tournament_name, tm.team_name
        ORDER BY t.tournament_name, points DESC, wins DESC, played DESC, tm.team_name
    """


@app.route("/points")
def points():
    rows = fetch_all(points_query())
    return render_template("points.html", points=rows)


@app.route("/registrations")
def registrations():
    rows = fetch_all("SELECT * FROM v_tournament_teams ORDER BY tournament_name, team_name")
    return render_template("registrations.html", registrations=rows)


@app.route("/sponsors")
def sponsors():
    rows = fetch_all("""
        SELECT t.tournament_name, s.sponsor_name, ts.sponsorship_amount
        FROM TournamentSponsors ts
        JOIN Tournaments t ON ts.tournament_id = t.tournament_id
        JOIN Sponsors s ON ts.sponsor_id = s.sponsor_id
        ORDER BY t.tournament_name
    """)
    return render_template("sponsors.html", sponsors=rows)


@app.route("/reports")
def reports():
    try:
        tournament_summary = fetch_all("""
            SELECT
                t.tournament_name,
                g.game_name,
                t.status,
                COUNT(DISTINCT r.team_id) AS registered_teams,
                COUNT(DISTINCT m.match_id) AS total_matches,
                SUM(CASE WHEN m.match_status='Completed' THEN 1 ELSE 0 END) AS completed_matches,
                t.prize_pool
            FROM Tournaments t
            JOIN Games g ON t.game_id = g.game_id
            LEFT JOIN Registrations r ON t.tournament_id = r.tournament_id
            LEFT JOIN Matches m ON t.tournament_id = m.tournament_id
            GROUP BY t.tournament_id, t.tournament_name, g.game_name, t.status, t.prize_pool
            ORDER BY t.start_date DESC
        """)
        recent_results = fetch_all("SELECT * FROM v_match_results ORDER BY match_date DESC LIMIT 10")
        return render_template("reports.html", tournament_summary=tournament_summary, recent_results=recent_results)
    except Error as e:
        return render_template("error.html", error=e)


@app.route("/export/<report_name>")
def export_report(report_name):
    if report_name == "players":
        rows = fetch_all("SELECT * FROM Players ORDER BY player_name")
    elif report_name == "teams":
        rows = fetch_all("SELECT * FROM Teams ORDER BY team_name")
    elif report_name == "tournaments":
        rows = fetch_all("""
            SELECT t.tournament_id, t.tournament_name, g.game_name, t.start_date, t.end_date, t.prize_pool, t.status
            FROM Tournaments t JOIN Games g ON t.game_id = g.game_id
            ORDER BY t.start_date
        """)
    elif report_name == "matches":
        rows = fetch_all("SELECT * FROM v_match_results ORDER BY match_date")
    elif report_name == "points":
        rows = fetch_all(points_query())
    else:
        flash("Invalid export report selected.", "danger")
        return redirect(url_for("reports"))
    return csv_response(f"{report_name}_report.csv", rows)


@app.route("/delete/<entity>/<int:item_id>", methods=["POST"])
@login_required
def delete_item(entity, item_id):
    delete_map = {
        "player": ("DELETE FROM Players WHERE player_id=%s", "Player deleted successfully."),
        "team": ("DELETE FROM Teams WHERE team_id=%s", "Team deleted successfully."),
        "tournament": ("DELETE FROM Tournaments WHERE tournament_id=%s", "Tournament deleted successfully."),
        "match": ("DELETE FROM Matches WHERE match_id=%s", "Match deleted successfully."),
    }
    if entity not in delete_map:
        flash("Invalid delete request.", "danger")
        return redirect(url_for("dashboard"))
    try:
        query, message = delete_map[entity]
        execute_query(query, (item_id,))
        flash(message, "success")
    except Error as e:
        flash("Cannot delete this record because it is connected to other records. Delete related records first.", "danger")
    return redirect(request.referrer or url_for("dashboard"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Page not found"), 404


if __name__ == "__main__":
    app.run(debug=True)
