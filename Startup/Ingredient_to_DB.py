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
    CREATE TABLE IF NOT EXISTS ingredients (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        UNIQUE(name, type)  -- Ensure name and type together are unique
    )
''')
conn.commit()

# Load Excel file
file_path = "All ingredient names.xlsx"
df = pd.read_excel(file_path)

# Process and insert data, avoiding duplicates
for col in df.columns:
    ingredient_type = col
    for ingredient in df[col].dropna():  # Drop empty cells
        # Use ON CONFLICT DO NOTHING to avoid duplicates
        c.execute("""
            INSERT INTO ingredients (name, type)
            VALUES (%s, %s)
            ON CONFLICT (name, type) DO NOTHING
        """, (ingredient, ingredient_type))

# Commit changes and close connection
conn.commit()
c.close()
conn.close()

print("Data successfully imported into PostgreSQL!")
