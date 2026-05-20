-- eSports Tournament Management System
-- MySQL DDL Script
-- Create database
CREATE DATABASE IF NOT EXISTS esports_tournament_db;
USE esports_tournament_db;

-- Drop tables in dependency order
DROP TABLE IF EXISTS MatchScores;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS TournamentSponsors;
DROP TABLE IF EXISTS Registrations;
DROP TABLE IF EXISTS TeamMembers;
DROP TABLE IF EXISTS Sponsors;
DROP TABLE IF EXISTS Tournaments;
DROP TABLE IF EXISTS Games;
DROP TABLE IF EXISTS Venues;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Teams;

-- Main tables
CREATE TABLE Teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    city VARCHAR(80),
    coach_name VARCHAR(100),
    created_at DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    gamer_tag VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(25),
    country VARCHAR(60) DEFAULT 'Pakistan',
    date_of_birth DATE
);

CREATE TABLE TeamMembers (
    team_id INT NOT NULL,
    player_id INT NOT NULL,
    role VARCHAR(50) DEFAULT 'Player',
    join_date DATE DEFAULT (CURRENT_DATE),
    PRIMARY KEY (team_id, player_id),
    CONSTRAINT fk_teammembers_team FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_teammembers_player FOREIGN KEY (player_id) REFERENCES Players(player_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL UNIQUE,
    genre VARCHAR(80),
    platform VARCHAR(80) NOT NULL
);

CREATE TABLE Venues (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    address VARCHAR(255),
    capacity INT CHECK (capacity >= 0)
);

CREATE TABLE Tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(120) NOT NULL,
    game_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    prize_pool DECIMAL(12,2) DEFAULT 0 CHECK (prize_pool >= 0),
    status ENUM('Upcoming','Ongoing','Completed','Cancelled') DEFAULT 'Upcoming',
    CONSTRAINT chk_tournament_dates CHECK (end_date >= start_date),
    CONSTRAINT fk_tournament_game FOREIGN KEY (game_id) REFERENCES Games(game_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team_id INT NOT NULL,
    registration_date DATE DEFAULT (CURRENT_DATE),
    registration_status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    UNIQUE (tournament_id, team_id),
    CONSTRAINT fk_registration_tournament FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_registration_team FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Sponsors (
    sponsor_id INT AUTO_INCREMENT PRIMARY KEY,
    sponsor_name VARCHAR(120) NOT NULL UNIQUE,
    contact_email VARCHAR(120),
    phone VARCHAR(25)
);

CREATE TABLE TournamentSponsors (
    tournament_id INT NOT NULL,
    sponsor_id INT NOT NULL,
    sponsorship_amount DECIMAL(12,2) DEFAULT 0 CHECK (sponsorship_amount >= 0),
    PRIMARY KEY (tournament_id, sponsor_id),
    CONSTRAINT fk_ts_tournament FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ts_sponsor FOREIGN KEY (sponsor_id) REFERENCES Sponsors(sponsor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    venue_id INT,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    match_date DATETIME NOT NULL,
    round_name VARCHAR(60),
    match_status ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    CONSTRAINT fk_match_tournament FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_match_venue FOREIGN KEY (venue_id) REFERENCES Venues(venue_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_match_team1 FOREIGN KEY (team1_id) REFERENCES Teams(team_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_match_team2 FOREIGN KEY (team2_id) REFERENCES Teams(team_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);



-- MariaDB-compatible rule: team1 and team2 cannot be the same team
DELIMITER //
CREATE TRIGGER trg_matches_before_insert
BEFORE INSERT ON Matches
FOR EACH ROW
BEGIN
    IF NEW.team1_id = NEW.team2_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'team1_id and team2_id cannot be the same';
    END IF;
END//

CREATE TRIGGER trg_matches_before_update
BEFORE UPDATE ON Matches
FOR EACH ROW
BEGIN
    IF NEW.team1_id = NEW.team2_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'team1_id and team2_id cannot be the same';
    END IF;
END//
DELIMITER ;

CREATE TABLE MatchScores (
    match_id INT PRIMARY KEY,
    team1_score INT DEFAULT 0 CHECK (team1_score >= 0),
    team2_score INT DEFAULT 0 CHECK (team2_score >= 0),
    winner_team_id INT,
    remarks VARCHAR(255),
    CONSTRAINT fk_score_match FOREIGN KEY (match_id) REFERENCES Matches(match_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_score_winner FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- Helpful views for project demonstration
CREATE OR REPLACE VIEW v_match_results AS
SELECT
    m.match_id,
    t.tournament_name,
    g.game_name,
    team1.team_name AS team1,
    team2.team_name AS team2,
    ms.team1_score,
    ms.team2_score,
    winner.team_name AS winner,
    m.match_date,
    m.round_name,
    v.venue_name
FROM Matches m
JOIN Tournaments t ON m.tournament_id = t.tournament_id
JOIN Games g ON t.game_id = g.game_id
JOIN Teams team1 ON m.team1_id = team1.team_id
JOIN Teams team2 ON m.team2_id = team2.team_id
LEFT JOIN MatchScores ms ON m.match_id = ms.match_id
LEFT JOIN Teams winner ON ms.winner_team_id = winner.team_id
LEFT JOIN Venues v ON m.venue_id = v.venue_id;

CREATE OR REPLACE VIEW v_tournament_teams AS
SELECT
    r.registration_id,
    t.tournament_name,
    tm.team_name,
    r.registration_status,
    r.registration_date
FROM Registrations r
JOIN Tournaments t ON r.tournament_id = t.tournament_id
JOIN Teams tm ON r.team_id = tm.team_id;
