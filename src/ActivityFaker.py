import sqlite3
import random
import time
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect("data.db")
cursor = conn.cursor()


def update_help_status(location_id):
    current_time = datetime.now()
    help_expires_at = current_time + timedelta(hours=3)

    cursor.execute("UPDATE distributor SET help = 1, help_expires_at = ? WHERE location_id = ?", (help_expires_at.timestamp(), location_id))
    conn.commit()


# Infinite loop to update help status every 1 hour
while True:
    try:
        # Get a random list of 10-25 location_ids from the distributor table
        cursor.execute("SELECT location_id FROM distributor ORDER BY RANDOM() LIMIT ?", (random.randint(10, 25),))
        location_ids = [row[0] for row in cursor.fetchall()]

        # Update help status for each selected location_id
        for location_id in location_ids:
            update_help_status(location_id)

        print(f"Help status updated for {len(location_ids)} locations at {datetime.now()}")

        # Wait for 1 hour before the next update
        time.sleep(3600)

    except KeyboardInterrupt:
        # Close the database connection and exit on keyboard interrupt
        conn.close()
        break
