import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'sprout.db')
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')


def initialize_database():
    connection = sqlite3.connect(db_path)

    with open(schema_path, 'r') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    # Create the demo student only if it does not already exist
    cur.execute(
        "INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)",
        ('MB-1024', 'Uday Jirwankar')
    )

    connection.commit()
    connection.close()

    print(f"Database successfully generated at: {db_path}")


if __name__ == '__main__':
    initialize_database()
