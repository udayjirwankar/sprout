"""Checks use temporary demo databases and an ephemeral encryption key."""
from contextlib import closing
import importlib
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from cryptography.fernet import Fernet

_TEST_DIRECTORY = tempfile.TemporaryDirectory(prefix='sprout-tests-')
os.environ['SPROUT_DEMO_DB_PATH'] = str(Path(_TEST_DIRECTORY.name) / 'demo.db')
os.environ['SPROUT_ENCRYPTION_KEY'] = Fernet.generate_key().decode()
os.environ['SPROUT_SESSION_SECRET'] = 'test-only-session-secret'
application = importlib.import_module('app')
from database.init_db import initialize_database
from security.encryption import encrypt_text, decrypt_text


class SproutTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='sprout-case-')
        self.database = str(Path(self.directory.name) / 'demo.db')
        application.DB_PATH = self.database
        initialize_database(self.database)
        application.app.config['TESTING'] = True
        self.client = application.app.test_client()
        self.client.get('/')

    def tearDown(self):
        self.directory.cleanup()

    def token(self, client=None):
        with (client or self.client).session_transaction() as current:
            return current['csrf_token']

    def workspace_id(self, client=None):
        with (client or self.client).session_transaction() as current:
            return current['demo_student_id']

    def query(self, sql, parameters=()):
        with closing(sqlite3.connect(self.database)) as connection:
            return connection.execute(sql, parameters).fetchall()

    def save(self, extra=None, analysis=None):
        payload = {'content': 'A synthetic test reflection.', 'mood': 'good'}
        payload.update(extra or {})
        analysis = analysis or {'prediction': 'Normal', 'confidence': 0.9}
        with patch.object(application, 'analyze_text', return_value=analysis):
            return self.client.post('/api/journal', json=payload,
                headers={'X-CSRF-Token': self.token()})

    def test_home_opens_without_login_or_signup(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Guest workspace', response.data)
        self.assertNotIn(b'/logout', response.data)
        self.assertEqual(self.client.get('/counselor').status_code, 200)
        self.assertEqual(self.client.get('/login').status_code, 302)
        self.assertEqual(self.client.get('/register').status_code, 404)
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE name='accounts'"), [])
        with self.client.session_transaction() as current:
            self.assertNotIn('user_id', current)

    def test_restart_preserves_journals_and_alerts(self):
        self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.8})
        for _ in range(3):
            initialize_database(self.database)
        self.assertEqual(len(self.query('SELECT * FROM journal_entries')), 1)
        self.assertEqual(len(self.query('SELECT * FROM escalation_alerts')), 1)

    def test_legacy_schema_migration_preserves_content(self):
        legacy = str(Path(self.directory.name) / 'legacy.db')
        with closing(sqlite3.connect(legacy)) as connection:
            connection.executescript('''
                CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, created_at TEXT);
                CREATE TABLE journal_entries (entry_id INTEGER PRIMARY KEY, student_id TEXT,
                    encrypted_content TEXT, created_at TEXT);
                CREATE TABLE escalation_alerts (alert_id INTEGER PRIMARY KEY, student_id TEXT,
                    risk_level TEXT, signal_summary TEXT, created_at TEXT);
                INSERT INTO students VALUES ('OLD', 'Synthetic', '2026-01-01');
                INSERT INTO journal_entries VALUES (1, 'OLD', 'keep-this-ciphertext', '2026-01-01');
            ''')
        initialize_database(legacy)
        initialize_database(legacy)
        with closing(sqlite3.connect(legacy)) as connection:
            self.assertEqual(connection.execute('SELECT encrypted_content FROM journal_entries').fetchone()[0], 'keep-this-ciphertext')
            self.assertIn('day_factors', [row[1] for row in connection.execute('PRAGMA table_info(journal_entries)')])
            self.assertIn('reviewed_at', [row[1] for row in connection.execute('PRAGMA table_info(escalation_alerts)')])

    def test_csrf_is_checked(self):
        self.assertEqual(self.client.post('/api/journal', json={'content': 'Test', 'mood': 'good'}).status_code, 400)
        self.assertEqual(self.client.post('/api/journal', json={}, headers={'X-CSRF-Token': 'é'}).status_code, 400)
        self.assertEqual(self.client.post('/demo/reset').status_code, 400)

    def test_journals_are_encrypted_and_context_round_trips(self):
        factors = ['📚 College', '👥 Friends']
        needs = ['🌿 Some quiet']
        response = self.save({'day_factors': factors, 'helpful_needs': needs})
        self.assertEqual(response.status_code, 200)
        ciphertext = self.query('SELECT encrypted_content FROM journal_entries ORDER BY entry_id DESC LIMIT 1')[0][0]
        self.assertNotIn('synthetic test reflection', ciphertext)
        self.assertEqual(decrypt_text(ciphertext), 'A synthetic test reflection.')
        history = self.client.get('/api/student/history').get_json()
        self.assertEqual(history[0]['day_factors'], factors)
        self.assertEqual(history[0]['helpful_needs'], needs)
        self.assertTrue(history[0]['created_at'].endswith('Z'))

    def test_real_local_model_can_save_a_synthetic_reflection(self):
        response = self.client.post('/api/journal',
            json={'content': 'I enjoyed finishing my class project and spending time with friends.', 'mood': 'good'},
            headers={'X-CSRF-Token': self.token()})
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn(result['prediction'], {'Normal', 'Anxiety', 'Depression', 'Suicidal'})
        self.assertTrue(0 <= result['confidence'] <= 1)

    def test_workspaces_cannot_spoof_ownership(self):
        other = application.app.test_client()
        other.get('/')
        own_id, other_id = self.workspace_id(), self.workspace_id(other)
        self.save({'student_id': other_id})
        self.assertEqual(self.query('SELECT student_id FROM journal_entries ORDER BY entry_id DESC LIMIT 1')[0][0], own_id)
        self.assertEqual(len(self.client.get('/api/student/history?student_id=' + other_id).get_json()), 1)
        self.assertEqual(len(other.get('/api/student/history?student_id=' + own_id).get_json()), 0)

    def test_invalid_input_never_saves_an_entry(self):
        for extra in [{'content': 123}, {'content': ''}, {'mood': '<script>'},
                      {'day_factors': 'not-a-list'}, {'helpful_needs': [123]}, {'content': 'x' * 20001}]:
            self.assertEqual(self.save(extra).status_code, 400)
        for payload in [[], None, 'text']:
            self.assertEqual(self.client.post('/api/journal', json=payload,
                headers={'X-CSRF-Token': self.token()}).status_code, 400)
        self.assertEqual(len(self.query('SELECT * FROM journal_entries')), 0)

    def test_model_failure_leaves_no_partial_record(self):
        with patch.object(application, 'analyze_text', side_effect=RuntimeError('synthetic failure')):
            response = self.client.post('/api/journal', json={'content': 'Synthetic', 'mood': 'okay'},
                headers={'X-CSRF-Token': self.token()})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(self.query('SELECT * FROM journal_entries')), 0)

    def test_alert_insert_failure_rolls_back_journal(self):
        with closing(sqlite3.connect(self.database)) as connection:
            connection.executescript("CREATE TRIGGER fail_alert BEFORE INSERT ON escalation_alerts BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END;")
        response = self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.8})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(self.query('SELECT * FROM journal_entries')), 0)

    def test_counselor_can_review_and_resolve_without_raw_text(self):
        self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.8})
        alerts = self.client.get('/api/counselor/alerts').get_json()
        self.assertNotIn('content', alerts[0])
        self.assertNotIn('encrypted_content', alerts[0])
        alert_id = alerts[0]['alert_id']
        for status in ['REVIEWED', 'RESOLVED']:
            response = self.client.patch(f'/api/counselor/alerts/{alert_id}', json={'status': status},
                headers={'X-CSRF-Token': self.token()})
            self.assertEqual(response.status_code, 200)
        resolved = self.client.get('/api/counselor/alerts').get_json()[0]
        self.assertEqual(resolved['status'], 'RESOLVED')
        self.assertTrue(resolved['reviewed_at'].endswith('Z'))
        self.assertTrue(resolved['resolved_at'].endswith('Z'))
        self.assertEqual(self.client.patch(f'/api/counselor/alerts/{alert_id}', json={'status': 'BAD'},
            headers={'X-CSRF-Token': self.token()}).status_code, 400)
        self.assertEqual(self.client.patch('/api/counselor/alerts/999', json={'status': 'REVIEWED'},
            headers={'X-CSRF-Token': self.token()}).status_code, 404)

    def test_counselor_views_cannot_see_other_workspaces(self):
        self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.8})
        other = application.app.test_client()
        other.get('/counselor')
        own_alerts = self.client.get('/api/counselor/alerts').get_json()
        other_alerts = other.get('/api/counselor/alerts').get_json()
        self.assertEqual(other_alerts, [])
        self.assertEqual(other.patch(f"/api/counselor/alerts/{own_alerts[0]['alert_id']}", json={'status': 'RESOLVED'},
            headers={'X-CSRF-Token': self.token(other)}).status_code, 404)
        self.assertTrue(all(alert['student_id'] == self.workspace_id(other) for alert in other_alerts))

    def test_expired_workspace_requires_refresh_before_saving(self):
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("UPDATE students SET created_at = datetime('now', '-2 days') WHERE student_id = ?", (self.workspace_id(),))
            connection.commit()
        self.assertEqual(self.client.get('/api/student/history').status_code, 409)
        self.assertEqual(self.save().status_code, 409)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(len(self.client.get('/api/student/history').get_json()), 0)

    def test_new_demo_creates_a_fresh_workspace(self):
        original_id = self.workspace_id()
        self.save()
        response = self.client.post('/demo/reset', data={'csrf_token': self.token()}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.workspace_id(), original_id)
        self.assertEqual(len(self.client.get('/api/student/history').get_json()), 0)

    def test_existing_non_demo_records_are_never_exposed(self):
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("INSERT INTO escalation_alerts (student_id, risk_level, signal_summary) VALUES ('MB-1024', 'HIGH', 'legacy-private-metadata')")
            connection.commit()
        self.assertTrue(all(alert['signal_summary'] != 'legacy-private-metadata' for alert in self.client.get('/api/counselor/alerts').get_json()))
        self.assertEqual(len(self.client.get('/api/student/history?student_id=MB-1024').get_json()), 0)


    def test_workspaces_start_empty_and_normal_reflections_create_no_alert(self):
        self.assertEqual(self.client.get('/api/student/history').get_json(), [])
        self.assertEqual(self.client.get('/api/counselor/alerts').get_json(), [])
        self.assertEqual(self.save().status_code, 200)
        self.assertEqual(self.client.get('/api/counselor/alerts').get_json(), [])
        self.assertEqual(self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.2}).status_code, 200)
        self.assertEqual(self.client.get('/api/counselor/alerts').get_json(), [])

    def test_legacy_sample_cleanup_preserves_submitted_data(self):
        self.save(analysis={'prediction': 'Anxiety', 'confidence': 0.8})
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                'INSERT INTO journal_entries (student_id, encrypted_content, mood) VALUES (?, ?, ?)',
                (self.workspace_id(), encrypt_text('Sample reflection: I made time to check in with myself today.'), 'good')
            )
            connection.execute(
                'INSERT INTO escalation_alerts (student_id, risk_level, signal_summary) VALUES (?, ?, ?)',
                (self.workspace_id(), 'HIGH', 'Sample alert for demonstrating the counselor review workflow.')
            )
            connection.commit()
        application.remove_legacy_samples()
        application.remove_legacy_samples()
        history = self.client.get('/api/student/history').get_json()
        alerts = self.client.get('/api/counselor/alerts').get_json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['content'], 'A synthetic test reflection.')
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['signal_summary'], 'Potential distress signal detected')


if __name__ == '__main__':
    unittest.main()
