USE esports_tournament_db;

INSERT INTO Teams (team_name, city, coach_name) VALUES
('Alpha Strikers', 'Lahore', 'Usman Khan'),
('Cyber Wolves', 'Karachi', 'Bilal Ahmed'),
('Falcon Esports', 'Islamabad', 'Hassan Ali'),
('Royal Gamers', 'Peshawar', 'Adeel Raza');

INSERT INTO Players (player_name, gamer_tag, email, phone, country, date_of_birth) VALUES
('Ali Raza', 'AliX', 'ali@example.com', '03000000001', 'Pakistan', '2003-02-11'),
('Hamza Khan', 'HamzaPro', 'hamza@example.com', '03000000002', 'Pakistan', '2004-05-20'),
('Ahmed Shah', 'Shadow99', 'ahmed@example.com', '03000000003', 'Pakistan', '2002-09-03'),
('Zain Malik', 'ZainOP', 'zain@example.com', '03000000004', 'Pakistan', '2003-07-15'),
('Fahad Noor', 'NoorFire', 'fahad@example.com', '03000000005', 'Pakistan', '2004-12-10'),
('Saad Tariq', 'SaadClutch', 'saad@example.com', '03000000006', 'Pakistan', '2001-11-09');

INSERT INTO TeamMembers (team_id, player_id, role) VALUES
(1, 1, 'Captain'), (1, 2, 'Player'),
(2, 3, 'Captain'), (2, 4, 'Player'),
(3, 5, 'Captain'),
(4, 6, 'Captain');

INSERT INTO Games (game_name, genre, platform) VALUES
('PUBG Mobile', 'Battle Royale', 'Mobile'),
('FIFA', 'Sports', 'PC/Console'),
('Valorant', 'FPS', 'PC');

INSERT INTO Venues (venue_name, city, address, capacity) VALUES
('FAST Gaming Arena', 'Lahore', 'FAST NUCES Lahore Campus', 300),
('Expo Gaming Hall', 'Karachi', 'Expo Center Karachi', 1000),
('Online Server', 'Online', 'Discord + Custom Room', 0);

INSERT INTO Tournaments (tournament_name, game_id, start_date, end_date, prize_pool, status) VALUES
('Spring PUBG Championship', 1, '2026-05-20', '2026-05-25', 150000.00, 'Upcoming'),
('FIFA Campus Cup', 2, '2026-06-01', '2026-06-03', 50000.00, 'Upcoming');

INSERT INTO Registrations (tournament_id, team_id, registration_status) VALUES
(1, 1, 'Approved'), (1, 2, 'Approved'), (1, 3, 'Approved'),
(2, 2, 'Approved'), (2, 4, 'Pending');

INSERT INTO Sponsors (sponsor_name, contact_email, phone) VALUES
('TechZone Pakistan', 'sponsor@techzone.pk', '03111111111'),
('GameHub', 'contact@gamehub.pk', '03222222222');

INSERT INTO TournamentSponsors (tournament_id, sponsor_id, sponsorship_amount) VALUES
(1, 1, 50000.00),
(1, 2, 25000.00),
(2, 2, 20000.00);

INSERT INTO Matches (tournament_id, venue_id, team1_id, team2_id, match_date, round_name, match_status) VALUES
(1, 3, 1, 2, '2026-05-20 18:00:00', 'Semi Final', 'Completed'),
(1, 3, 3, 1, '2026-05-21 18:00:00', 'Final', 'Scheduled'),
(2, 1, 2, 4, '2026-06-01 14:00:00', 'Round 1', 'Scheduled');

INSERT INTO MatchScores (match_id, team1_score, team2_score, winner_team_id, remarks) VALUES
(1, 15, 10, 1, 'Alpha Strikers won by 5 points');
