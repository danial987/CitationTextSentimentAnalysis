import hashlib
import psycopg2
from psycopg2 import errors
from db import Database

class AuthService:
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def hash_password(password):
        """Hash the password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, full_name, username, email, password, role_name="User"):
        """Register a new user."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id FROM roles WHERE name = %s', (role_name,))
                role = cur.fetchone()
                if not role:
                    raise ValueError(f"Role '{role_name}' not found. Ensure roles are initialized.")

                hashed_password = self.hash_password(password)

                try:
                    cur.execute(
                        '''
                        INSERT INTO users (full_name, username, email, password, role_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ''',
                        (full_name, username, email, hashed_password, role[0])
                    )
                    conn.commit()
                except errors.UniqueViolation as e:
                    conn.rollback()
                    if "users_username_key" in str(e):
                        raise ValueError("The username is already taken. Please choose another.")
                    if "users_email_key" in str(e):
                        raise ValueError("The email is already registered. Please use a different email.")
                    raise e

    def authenticate_user(self, username, password):
        """Authenticate a user by username and password."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                hashed_password = self.hash_password(password)
                cur.execute(
                    '''
                    SELECT users.id, users.full_name, users.username, users.email, roles.name AS role
                    FROM users
                    INNER JOIN roles ON users.role_id = roles.id
                    WHERE users.username = %s AND users.password = %s
                    ''',
                    (username, hashed_password)
                )
                return cur.fetchone()

    def check_username_exists(self, username):
        """Check if a username already exists in the database."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username FROM users WHERE username = %s", (username,))
                return cur.fetchone() is not None

    def check_email_exists(self, email):
        """Check if an email already exists in the database."""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM users WHERE email = %s", (email,))
                return cur.fetchone() is not None

    @staticmethod
    def is_valid_email(email):
        """Validate email format."""
        import re
        email_regex = (
            r"^(?!\.)"
            r"[a-zA-Z0-9_.+-]+"
            r"(?<!\.)@"
            r"[a-zA-Z0-9-]+"
            r"(\.[a-zA-Z]{2,})+$"
        )
        return bool(re.match(email_regex, email)) and ".." not in email

    @staticmethod
    def is_valid_password(password):
        """Validate password strength."""
        import re
        if len(password) < 8:
            return False
        if not re.search(r"[a-zA-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[@$!%*?&#]", password):
            return False
        return True
