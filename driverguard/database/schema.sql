-- ============================================================================
-- DriverGuard Relational Database Schema (SQLite)
-- ============================================================================

-- Enable Foreign Key Constraint enforcement in SQLite
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. Users Table
-- Represents drivers, fleet operators, and system administrators.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'driver' CHECK (role IN ('driver', 'operator', 'admin')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Index for fast lookup by email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


-- ----------------------------------------------------------------------------
-- 2. Devices Table
-- Represents physical camera and telemetry hardware units installed in vehicles.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL UNIQUE,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'retired')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Index for fast hardware device serial number lookup
CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(serial_number);


-- ----------------------------------------------------------------------------
-- 3. Calibration Profiles Table
-- 1:1 Relationship with users (Each driver has exactly 1 active baseline profile).
-- Stores Computer Vision detection thresholds (EAR, MAR, Head Pitch).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calibration_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE, -- UNIQUE constraint enforces 1:1 relationship
    ear_threshold REAL NOT NULL DEFAULT 0.20,  -- Eye Aspect Ratio baseline
    mar_threshold REAL NOT NULL DEFAULT 0.50,  -- Mouth Aspect Ratio baseline
    head_pitch_threshold REAL NOT NULL DEFAULT 15.0, -- Head Tilt angle baseline
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for looking up driver calibration profiles
CREATE INDEX IF NOT EXISTS idx_calibration_profiles_user_id ON calibration_profiles(user_id);


-- ----------------------------------------------------------------------------
-- 4. Sessions Table
-- 1:N Relationship (1 User -> Many Sessions, 1 Device -> Many Sessions).
-- Represents an active driving trip monitored by DriverGuard.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    device_id INTEGER NOT NULL,
    start_time TEXT NOT NULL DEFAULT (datetime('now')),
    end_time TEXT,
    status TEXT NOT NULL DEFAULT 'ongoing' CHECK (status IN ('ongoing', 'completed', 'aborted')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE RESTRICT
);

-- Indexes for querying sessions by driver or device
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_device_id ON sessions(device_id);


-- ----------------------------------------------------------------------------
-- 5. Fatigue Events Table
-- 1:N Relationship (1 Session -> Many Fatigue Detection Events).
-- Logs real-time drowsiness, yawning, microsleeps, and distraction alerts.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fatigue_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('microsleep', 'yawn', 'distraction', 'head_nod')),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    score REAL NOT NULL, -- Detection confidence / metric score (e.g. 0.89)
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Composite index for fast filtering of session events by event type and severity
CREATE INDEX IF NOT EXISTS idx_fatigue_events_session_id ON fatigue_events(session_id);
CREATE INDEX IF NOT EXISTS idx_fatigue_events_type_severity ON fatigue_events(event_type, severity);
