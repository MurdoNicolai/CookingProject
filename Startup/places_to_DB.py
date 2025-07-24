#!/usr/bin/env python
import pandas as pd
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname='postgres',
    user='murdo',
    password='n9XLSLHx',
    host='localhost',
    port='5432'
)
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS geography (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        sub_region TEXT,
        intermediate_region TEXT)
''')
conn.commit()

# Load Excel file
file_path = "places.xml"
df = pd.read_xml(file_path, xpath=".//country")

# Process and insert data, avoiding duplicates
for _, row in df.iterrows():
    c.execute('''
        INSERT INTO geography (name, region, sub_region, intermediate_region)
        VALUES (%s, %s, %s, %s)
    ''', (row['name'], row['region'], row['sub-region'], row['intermediate-region']))


# Commit changes and close connection
conn.commit()
c.close()
conn.close()

print("Data successfully imported into PostgreSQL without duplicates!")
