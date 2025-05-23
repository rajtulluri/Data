import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database credentials
HOST = "localhost"
USER = "postgres"
PASSWORD = "postgres"  # Change this
CSV_PATH = "Mamatwan.csv"  # Path to your CSV file

# Step 1: Connect to default 'postgres' database to create 'minedb'
conn = psycopg2.connect(host=HOST, user=USER, password=PASSWORD, dbname='postgres')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("DROP DATABASE IF EXISTS minedb")
cur.execute("CREATE DATABASE minedb")
cur.close()
conn.close()

# Step 2: Connect to the new 'minedb'
conn = psycopg2.connect(host=HOST, user=USER, password=PASSWORD, dbname='minedb')
cur = conn.cursor()

# Step 3: Load CSV into pandas
df = pd.read_csv(CSV_PATH, sep=",")

# Step 4: Create a table with appropriate column types
create_table_sql = """
CREATE TABLE mining_data (
    AccountName TEXT,
    Truck TEXT,
    Loader TEXT,
    LoadingArea TEXT,
    DumpingArea TEXT,
    Material TEXT,
    Tonnage FLOAT,
    BCM FLOAT,
    QueueDurationSeconds FLOAT,
    FillDurationSeconds FLOAT,
    LoadingDurationSeconds FLOAT,
    DumpingDurationSeconds FLOAT,
    CycleDelaySeconds FLOAT,
    OtherDelaySeconds FLOAT,
    TravelSecondsLaden FLOAT,
    TravelDistanceLadenM FLOAT,
    TravelSecondsUnladen FLOAT,
    TravelDistanceUnladenM FLOAT,
    AverageMovementSpeedLadenKmH FLOAT,
    AverageMovementSpeedUnladenKmH FLOAT,
    StartTimestamp TIMESTAMPTZ,
    LoadingTimestamp TIMESTAMPTZ,
    DumpingTimestamp TIMESTAMPTZ,
    EndTimestamp TIMESTAMPTZ
)
"""
cur.execute("DROP TABLE IF EXISTS mining_data")
cur.execute(create_table_sql)
conn.commit()

# Ensure all NaNs are converted to None
df = df.where(pd.notnull(df), None)

# Prepare insert SQL
insert_sql = """
    INSERT INTO mining_data VALUES ({})
""".format(', '.join(['%s'] * len(df.columns)))  # 24 %s

# Insert rows
for i, row in df.iterrows():
    try:
        cur.execute(insert_sql, tuple(row))
    except Exception as e:
        print(f"Error inserting row {i}: {e}")

conn.commit()
cur.close()
conn.close()