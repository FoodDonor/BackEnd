import sqlite3
import random
import time
from datetime import datetime, timedelta
import names
import string
import orjson
from base64 import b64encode
import requests

conn = sqlite3.connect("data.db")
cursor = conn.cursor()


def update_help_status(location_id):
    current_time = datetime.now()
    help_expires_at = current_time + timedelta(hours=3)

    cursor.execute("UPDATE distributor SET help = 1, help_expires_at = ? WHERE location_id = ?", (help_expires_at.timestamp(), location_id))
    conn.commit()


# Generate a random phone number
def generate_random_phone(country_code):
    if country_code == 'US':
        return f'+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}'
    elif country_code == 'CA':
        return f'+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}'
    elif country_code == 'UK':
        return f'+44-{random.randint(20, 79)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
    elif country_code == 'AU':
        return f'+61-4{random.randint(0, 9)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
    elif country_code == 'IN':
        return f'+91-{random.randint(7000, 9999)}-{random.randint(1000, 9999)}'
    else:
        return None

# Generate a random zip code
def generate_random_zip(country_code):
    if country_code == 'US':
        return f'{random.randint(10000, 99999)}'
    elif country_code == 'CA':
        return f'{random.choice("ABCEGHJKLMNPRSTVXY")}{random.randint(0, 9)}{random.choice("ABCEGHJKLMNPRSTVWXYZ")} {random.randint(0, 9)}{random.choice("ABCEGHJKLMNPRSTVWXYZ")}{random.randint(0, 9)}'
    elif country_code == 'UK':
        return f'{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")}{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")}9{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")}{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")} {random.randint(0, 9)}{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")}{random.choice("ABCDEFGHIJKLMNOPRSTUWXYZ")}'
    elif country_code == 'AU':
        return f'{random.randint(1000, 9999)}'
    elif country_code == 'IN':
        return f'{random.randint(100000, 999999)}'
    else:
        return None

# Generate a random location
def generate_random_location(country_code):
    if country_code == 'US':
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']
        states = ['NY', 'CA', 'IL', 'TX', 'FL']
        return f'{random.choice(cities)}, {random.choice(states)}, USA'
    elif country_code == 'CA':
        cities = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa']
        provinces = ['ON', 'BC', 'QC', 'AB', 'ON']
        return f'{random.choice(cities)}, {random.choice(provinces)}, Canada'
    elif country_code == 'UK':
        cities = ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Glasgow']
        return f'{random.choice(cities)}, UK'
    elif country_code == 'AU':
        cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide']
        states = ['NSW', 'VIC', 'QLD', 'WA', 'SA']
        return f'{random.choice(cities)}, {random.choice(states)}, Australia'
    elif country_code == 'IN':
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
        states = ['MH', 'DL', 'KA', 'TN', 'WB']
        return f'{random.choice(cities)}, {random.choice(states)}, India'
    else:
        return None


def create_new_user():
    country = random.choice(['US', 'CA', 'UK', 'AU', 'IN'])
    name = names.get_full_name()
    pl = {
        "name": name,
        "email": f'{name.replace(" ", "").lower()}@gmail.com',
        "password": ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10, 20)),
        "dob": f'{random.randint(1, 12)}-{random.randint(1, 28)}-{random.randint(1950, 2000)}',
        "phone": generate_random_phone(country),
        "zip": generate_random_zip(country),
        "location": random.choice([generate_random_location(country), None])
    }
    pl = {"encrypted": b64encode(orjson.dumps(pl)).decode()}
    requests.post("http://0.0.0.0:41849/auth/register", json=pl)


# Infinite loop to update help status every 4 hours
while True:
    try:
        # Get a random list of 10-25 location_ids from the distributor table
        cursor.execute("SELECT location_id FROM distributor ORDER BY RANDOM() LIMIT ?", (random.randint(10, 25),))
        location_ids = [row[0] for row in cursor.fetchall()]

        for i in range(random.randint(3, 10)):
            create_new_user()

        # Update help status for each selected location_id
        for location_id in location_ids:
            update_help_status(location_id)

        print(f"Faked data for {len(location_ids)} locations at {datetime.now()}")

        # Wait for 1 hour before the next update
        time.sleep(3600*4)

    except KeyboardInterrupt:
        # Close the database connection and exit on keyboard interrupt
        conn.close()
        break
