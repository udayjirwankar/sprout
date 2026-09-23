import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'sprout.db')
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

def initialize_database():
    connection = sqlite3.connect(db_path)
    
    with open(schema_path, 'r') as f:
        connection.executescript(f.read())
        
    cur = connection.cursor()
    # Insert a dummy student for our testing
    cur.execute(
        "INSERT INTO students (student_id, name) VALUES (?, ?)",
        ('MB-1024', 'Uday Jirwankar')
    )
    
    connection.commit()
    connection.close()
    print(f"Database successfully generated at: {db_path}")

if __name__ == '__main__':
    initialize_database()