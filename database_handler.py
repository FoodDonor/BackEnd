import sqlite3


class DataBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()
        self.startup()

    def startup(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lister
                (
                    user_id   BIGINT UNIQUE PRIMARY KEY,
                    full_name TEXT,
                    email     TEXT,
                    password  TEXT,
                    dob       TEXT,
                    phone     TEXT,
                    token     TEXT,
                    time      REAL,
                    location  BLOB
                );
            """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS volunteer
                (
                    user_id   BIGINT UNIQUE PRIMARY KEY,
                    full_name TEXT,
                    email     TEXT,
                    password  TEXT,
                    dob       TEXT,
                    phone     TEXT,
                    token     TEXT,
                    time      REAL
                );
            """
        )
        self.conn.commit()

    def shutdown(self):
        self.cur.commit()
        self.conn.close()

    def check_lister_email_exists(self, email: str):
        proc = self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM lister WHERE email = ?);", (email,))
        return proc.fetchone()

    def check_lister_phone_exists(self, phone: str):
        proc = self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM lister WHERE phone = ?);", (phone,))
        return proc.fetchone()

    def check_volunteer_email_exists(self, email: str):
        proc = self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM volunteer WHERE email = ?);", (email,))
        return proc.fetchone()

    def check_volunteer_phone_exists(self, phone: str):
        proc = self.cur.execute(f"SELECT EXISTS(SELECT 1 FROM volunteer WHERE phone = ?);", (phone,))
        return proc.fetchone()

    def new_user(self, user):
        table = "lister" if user["location"] else "volunteer"
        self.cur.execute(
            f"""
            INSERT INTO {table} (full_name, email, password, dob, phone, location, details, token, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                user["name"].title(),
                user["email"],
                user["password"],
                user["dob"],
                user["phone"],
                user["location"],
                user["details"],
                user["token"],
                user["time"],
            ),
        )
        self.conn.commit()
