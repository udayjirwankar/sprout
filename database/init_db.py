import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'sprout.db')
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')


def initialize_database(database_path=None):
    """Create missing tables and add columns without deleting saved data."""
    database_path = database_path or db_path
    os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        with open(schema_path, 'r', encoding='utf-8') as schema_file:
            # Serialize startup migrations and commit them together.
            connection.executescript('BEGIN IMMEDIATE;\n' + schema_file.read())

        # These small, additive migrations also support older local databases.
        migrations = {
            'journal_entries': {
                'mood': 'TEXT',
                'day_factors': 'TEXT',
                'helpful_needs': 'TEXT',
            },
            'escalation_alerts': {
                'status': "TEXT DEFAULT 'PENDING'",
                'reviewed_at': 'TIMESTAMP',
                'resolved_at': 'TIMESTAMP',
            },
        }
        for table, columns in migrations.items():
            existing = {
                row[1] for row in connection.execute(f'PRAGMA table_info({table})')
            }
            for column, definition in columns.items():
                if column not in existing:
                    connection.execute(
                        f'ALTER TABLE {table} ADD COLUMN {column} {definition}'
                    )

        connection.execute(
            'CREATE INDEX IF NOT EXISTS idx_journal_student_date '
            'ON journal_entries (student_id, created_at)'
        )
        connection.execute(
            "INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)",
            ('MB-1024', 'Uday Jirwankar')
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == '__main__':
    initialize_database()
