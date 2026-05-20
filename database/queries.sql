USE esports_tournament_db;

-- 1. Show all tournaments with game names
SELECT t.tournament_name, g.game_name, t.start_date, t.end_date, t.prize_pool, t.status
FROM Tournaments t
JOIN Games g ON t.game_id = g.game_id;

-- 2. Show team members
SELECT tm.team_name, p.player_name, p.gamer_tag, mb.role
FROM TeamMembers mb
JOIN Teams tm ON mb.team_id = tm.team_id
JOIN Players p ON mb.player_id = p.player_id
ORDER BY tm.team_name;

-- 3. Show teams registered in each tournament
SELECT tournament_name, team_name, registration_status
FROM v_tournament_teams
ORDER BY tournament_name, team_name;

-- 4. Show match schedule and results
SELECT * FROM v_match_results
ORDER BY match_date;

-- 5. Show sponsors for tournaments
SELECT t.tournament_name, s.sponsor_name, ts.sponsorship_amount
FROM TournamentSponsors ts
JOIN Tournaments t ON ts.tournament_id = t.tournament_id
JOIN Sponsors s ON ts.sponsor_id = s.sponsor_id;

-- 6. Count approved teams per tournament
SELECT t.tournament_name, COUNT(r.team_id) AS approved_teams
FROM Tournaments t
LEFT JOIN Registrations r ON t.tournament_id = r.tournament_id
    AND r.registration_status = 'Approved'
GROUP BY t.tournament_id, t.tournament_name;

-- 7. Winners list
SELECT tournament_name, team1, team2, team1_score, team2_score, winner
FROM v_match_results
WHERE winner IS NOT NULL;
