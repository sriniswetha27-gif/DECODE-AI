import hashlib
import hmac
import os
import re
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("decode_ai.db")
PASSWORD_ITERATIONS = 310_000


def connect_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with connect_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                language TEXT NOT NULL,
                code_text TEXT NOT NULL,
                review_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    return password_hash.hex(), salt.hex()


def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return False, "Please enter your full name."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, password_salt = hash_password(password)

    try:
        with connect_database() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password_hash,
                    password_salt
                )
                VALUES (?, ?, ?, ?)
                """,
                (name, email, password_hash, password_salt),
            )

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "An account already exists with this email."


def authenticate_user(email, password):
    email = email.strip().lower()

    with connect_database() as connection:
        user = connection.execute(
            """
            SELECT id, name, email, password_hash, password_salt
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if user is None:
        return None

    user_id, name, saved_email, saved_hash, saved_salt = user

    entered_hash, _ = hash_password(
        password,
        bytes.fromhex(saved_salt),
    )

    if not hmac.compare_digest(entered_hash, saved_hash):
        return None

    return {
        "id": user_id,
        "name": name,
        "email": saved_email,
    }


def save_review(
    user_id,
    file_name,
    language,
    code_text,
    review_text,
):
    with connect_database() as connection:
        cursor = connection.execute(
            """
            INSERT INTO review_history (
                user_id,
                file_name,
                language,
                code_text,
                review_text
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                file_name,
                language,
                code_text,
                review_text,
            ),
        )

        return cursor.lastrowid


def get_review_history(user_id):
    with connect_database() as connection:
        reviews = connection.execute(
            """
            SELECT
                id,
                file_name,
                language,
                code_text,
                review_text,
                created_at
            FROM review_history
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()

    return [
        {
            "id": review[0],
            "file_name": review[1],
            "language": review[2],
            "code_text": review[3],
            "review_text": review[4],
            "created_at": review[5],
        }
        for review in reviews
    ]