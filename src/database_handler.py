import sqlite3


class DataBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()
        self.startup()

    def startup(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS distributor
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
            """
        )
        self.cur.execute(
            """
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

    def check_distributor_email_exists(self, email: str):
        proc = self.cur.execute("SELECT EXISTS(SELECT 1 FROM distributor WHERE email = ?);", (email,))
        return proc.fetchone()

    def check_distributor_phone_exists(self, phone: str):
        proc = self.cur.execute("SELECT EXISTS(SELECT 1 FROM distributor WHERE phone = ?);", (phone,))
        return proc.fetchone()

    def check_volunteer_email_exists(self, email: str):
        proc = self.cur.execute("SELECT EXISTS(SELECT 1 FROM volunteer WHERE email = ?);", (email,))
        return proc.fetchone()

    def check_volunteer_phone_exists(self, phone: str):
        proc = self.cur.execute("SELECT EXISTS(SELECT 1 FROM volunteer WHERE phone = ?);", (phone,))
        return proc.fetchone()

    def new_user(self, user):
        if user["location"]:
            self.cur.execute(
                f"""
                INSERT INTO distributor (full_name, email, password, dob, phone, token, time, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user["name"].title(),
                    user["email"],
                    user["password"],
                    user["dob"],
                    user["phone"],
                    user["token"],
                    user["time"],
                    user["location"],
                ),
            )
        else:
            self.cur.execute(
                f"""
                INSERT INTO volunteer (full_name, email, password, dob, phone, token, time)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user["name"].title(),
                    user["email"],
                    user["password"],
                    user["dob"],
                    user["phone"],
                    user["token"],
                    user["time"],
                ),
            )

        self.conn.commit()

    def get_user_by_phone(self, phone: str):
        proc = self.cur.execute("SELECT * FROM distributor WHERE phone = ?;", (phone,))
        data = proc.fetchone()
        if not data:
            proc = self.cur.execute("SELECT * FROM volunteer WHERE phone = ?;", (phone,))
            data = proc.fetchone()
        return data
    
    def get_user_by_email(self, email: str):
        proc = self.cur.execute("SELECT * FROM distributor WHERE email = ?;", (email,))
        data = proc.fetchone()
        if not data:
            proc = self.cur.execute("SELECT * FROM volunteer WHERE email = ?;", (email,))
            data = proc.fetchone()
        return data
    