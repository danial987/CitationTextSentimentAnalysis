import psycopg2
import hashlib

class Database:
    def __init__(self, host="aws-0-ap-southeast-1.pooler.supabase.com", database="postgres", user="postgres.ehwcouriomweehffhtdo", password="Correctpass3421$", port=6543):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port


    def connect(self):
        """Create and return a new database connection."""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def initialize(self):
        """Initialize tables and default role."""
        with self.connect() as conn:
            with conn.cursor() as cur:
                self._create_tables(cur)
                self._initialize_user_role(cur) 
            conn.commit()

    def _create_tables(self, cur):
        """Create necessary tables if they don't exist."""
        cur.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role_id INTEGER REFERENCES roles(id),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

    def _initialize_user_role(self, cur):
        """Ensure the 'User' role exists."""
        cur.execute(
            'INSERT INTO roles (name) VALUES (%s) ON CONFLICT (name) DO NOTHING',
            ("User",)
        )

    @staticmethod
    def _hash_password(password):
        """Helper function to hash passwords securely."""
        return hashlib.sha256(password.encode()).hexdigest()