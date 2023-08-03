import sqlite3
import datetime

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
                    user_id     BIGINT UNIQUE PRIMARY KEY,
                    full_name   TEXT,
                    email       TEXT,
                    password    TEXT,
                    dob         TEXT,
                    phone       TEXT,
                    token       TEXT,
                    time        REAL,
                    location_id BIGINT UNIQUE,
                    zip         TEXT,
                    location    BLOB
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
        self.cur.execute(

            """
            CREATE TABLE IF NOT EXISTS daily_data (
                id          INTEGER PRIMARY KEY,
                date        DATE NOT NULL,
                location_id INTEGER,
                num_fed     INTEGER,
                kgs_fed     INTEGER,
                kgs_wasted  INTEGER,
                manpower    INTEGER,
                FOREIGN KEY (location_id) REFERENCES distributor(location_id)
            );
            """
        )
        self.conn.commit()

    def shutdown(self):
        self.cur.commit()
        self.conn.close()

    def get_num_distribs(self):
        proc = self.cur.execute("SELECT COUNT(*) FROM distributor;")
        return proc.fetchone()[0]

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
            location_id = self.get_num_distribs() + 1
            self.cur.execute(
                f"""
                INSERT INTO distributor (full_name, email, password, dob, phone, token, time, location_id, zip, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    user["name"].title(),
                    user["email"],
                    user["password"],
                    user["dob"],
                    user["phone"],
                    user["token"],
                    user["time"],
                    location_id,
                    user["zip"],
                    user["location"],
                ),
            )
            ret = location_id
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
            ret = " "

        self.conn.commit()
        return ret

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

    def insert_daily_data(self, date, location_id, num_fed, kgs_fed, kgs_wasted, manpower):
        self.cur.execute(
            """
            INSERT INTO daily_data (date, location_id, num_fed, kgs_fed, kgs_wasted, manpower)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (date, location_id, num_fed, kgs_fed, kgs_wasted, manpower, ),
        )
        self.conn.commit()

    def get_total_data(self):
        proc = self.cur.execute("SELECT SUM(num_fed) FROM daily_data;")
        total_num_fed = proc.fetchone()[0]
        proc = self.cur.execute("SELECT SUM(kgs_fed) FROM daily_data;")
        total_kgs_fed = proc.fetchone()[0]

        return {"total_num_fed": total_num_fed, "total_kgs_fed": total_kgs_fed, "total_locations": self.get_num_distribs()}

    def get_distributor_by_token(self, token):
        proc = self.cur.execute("SELECT * FROM distributor WHERE token = ?;", (token,))
        return proc.fetchone()

    def get_daily_data_by_location_id(self, loc_id):
        proc = self.cur.execute("SELECT * FROM daily_data WHERE location_id = ?;", (loc_id,))
        return proc.fetchall()

    def get_locs_by_zip(self, zip):
        locations = []
        proc = self.cur.execute("SELECT full_name, phone, email, location_id FROM distributor WHERE zip = ?;", (zip,))
        distributors = proc.fetchall()
        for distributor in distributors:
            datas = self.get_daily_data_by_location_id(distributor[3])
            for data in datas:
                data.append(data[1])
                data[1] = datetime.datetime.strptime(data[1], "%m-%d-%Y").timestamp()
            req_entry = sorted(datas, key=lambda x: x[1], reverse=True)[0]
            req_entry_loc = self.cur.execute("SELECT location FROM distributor WHERE location_id = ?;", (req_entry[2],)).fetchone()[0]
            locations.append(
                {
                    "d": {
                        "n": distributor[0],
                        "c": {
                            "e": distributor[2],
                            "p": distributor[1],
                        }
                    },
                    "l": req_entry_loc,
                    "t": req_entry[-1],
                    "pf": req_entry[3],
                    "kg": req_entry[4],
                    "w": req_entry[5],
                    "m": req_entry[6]
                }
            )
        return locations

    def get_zips(self):
        return list(set([i[0] for i in self.cur.execute("SELECT zip FROM distributor;").fetchall()]))
