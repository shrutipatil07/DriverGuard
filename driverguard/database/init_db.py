"""
Database initializer script for DriverGuard SQLite database.
Executes schema.sql and populates sample data for testing.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "driverguard.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def init_db():
    print(f"[*] Initializing database at: {DB_PATH}")

    # Remove existing db file for clean recreation
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    print("[*] Schema created successfully.")

    # --- Insert Sample Data within a Transaction ---
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION;")

        # Insert Users
        cursor.execute("INSERT INTO users (name, email, role) VALUES ('Rajesh Kumar', 'rajesh@driverguard.com', 'driver');")
        user1_id = cursor.lastrowid

        cursor.execute("INSERT INTO users (name, email, role) VALUES ('Priya Sharma', 'priya@driverguard.com', 'driver');")
        user2_id = cursor.lastrowid

        cursor.execute("INSERT INTO users (name, email, role) VALUES ('Vikram Singh', 'vikram@driverguard.com', 'operator');")

        # Insert Devices
        cursor.execute("INSERT INTO devices (serial_number, model, status) VALUES ('CAM-1001', 'GuardVision-v2', 'active');")
        device1_id = cursor.lastrowid

        cursor.execute("INSERT INTO devices (serial_number, model, status) VALUES ('CAM-1002', 'GuardVision-v2', 'active');")
        device2_id = cursor.lastrowid

        # Insert Calibration Profiles (1:1 with Users)
        cursor.execute(
            "INSERT INTO calibration_profiles (user_id, ear_threshold, mar_threshold, head_pitch_threshold) VALUES (?, 0.21, 0.48, 14.5);",
            (user1_id,)
        )
        cursor.execute(
            "INSERT INTO calibration_profiles (user_id, ear_threshold, mar_threshold, head_pitch_threshold) VALUES (?, 0.19, 0.52, 16.0);",
            (user2_id,)
        )

        # Insert Sessions (1:N with Users and Devices)
        cursor.execute(
            "INSERT INTO sessions (user_id, device_id, status) VALUES (?, ?, 'completed');",
            (user1_id, device1_id)
        )
        session1_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO sessions (user_id, device_id, status) VALUES (?, ?, 'ongoing');",
            (user2_id, device2_id)
        )
        session2_id = cursor.lastrowid

        # Insert Fatigue Events (1:N with Sessions)
        cursor.execute(
            "INSERT INTO fatigue_events (session_id, event_type, severity, score) VALUES (?, 'yawn', 'low', 0.65);",
            (session1_id,)
        )
        cursor.execute(
            "INSERT INTO fatigue_events (session_id, event_type, severity, score) VALUES (?, 'microsleep', 'high', 0.91);",
            (session1_id,)
        )
        cursor.execute(
            "INSERT INTO fatigue_events (session_id, event_type, severity, score) VALUES (?, 'head_nod', 'medium', 0.78);",
            (session1_id,)
        )
        cursor.execute(
            "INSERT INTO fatigue_events (session_id, event_type, severity, score) VALUES (?, 'microsleep', 'critical', 0.96);",
            (session2_id,)
        )

        conn.commit()
        print("[*] Sample data seeded successfully!")

    except Exception as e:
        conn.rollback()
        print(f"[!] Error seeding data, transaction rolled back: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
