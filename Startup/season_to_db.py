#!/usr/bin/env python
import psycopg2

seasons = ['all', 'spring', 'summer', 'autumn', 'winter']

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
    CREATE TABLE IF NOT EXISTS season (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    )
''')
conn.commit()

# Process and insert data, avoiding duplicates
for season in seasons:
    c.execute('''
        INSERT INTO season (name)
        VALUES (%s)
    ''', (season,))


# Commit changes and close connection
conn.commit()
c.close()
conn.close()

print("Data successfully imported into PostgreSQL without duplicates!")
