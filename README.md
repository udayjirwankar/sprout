# 🌱 Sprout

### Private words. Minimal signal. Human support.

Sprout is a student wellbeing prototype that demonstrates encrypted journaling, local text classification, and a counselor view of limited wellbeing signals. It opens directly into an empty guest workspace without accounts or passwords.

> **Support students without turning personal reflection into surveillance.**

## Why Sprout?

College students can experience academic pressure, isolation, uncertainty, relationship difficulties, financial stress, and other forms of emotional distress.

Sprout explores a different approach:

- Students can write privately.
- Journal content is encrypted before storage.
- Local NLP analyzes the reflection.
- The system produces a configured wellbeing signal.
- Counselor-facing alerts contain limited metadata rather than raw journal text.
- Human review remains part of the support process.

Sprout is a prototype for **early support assistance**, not a medical or diagnostic system.

## How It Works

```text
Student
   │
   ▼
Private Journal
   │
   ▼
Encrypted Storage
   │
   ▼
Local NLP Analysis
   │
   ▼
Risk / Signal Engine
   │
   ├── LOW
   ├── ELEVATED
   └── HIGH
   │
   ▼
Privacy Firewall
   │
   ▼
Counselor Dashboard
```

The student's raw journal text is kept separate from counselor-facing escalation alerts.

## Student Experience

Sprout provides a calm digital space where students can:

- Write private journal reflections
- Record their current mood
- Add optional context about what affected their day
- Select what kind of support or space feels helpful
- Review recent reflection history
- View personal wellbeing insights
- Grow a visual Mood Tree through check-ins
- Maintain a reflection streak through the Star Jar
- Use the Night Radio experience
- Explore their personal space and privacy information

## Local NLP & Wellbeing Signals

The current prototype uses a locally stored text-classification model rather than sending journal text to an external AI API.

The classifier uses:

- Word TF-IDF features
- Character TF-IDF features
- Logistic Regression classification

The classifier produces one of four text categories:

```text
Normal
Anxiety
Depression
Suicidal
```

A separate configurable risk engine converts model output into prototype wellbeing signals:

```text
LOW
ELEVATED
HIGH
```

These thresholds are prototype configuration and are **not clinical thresholds**.

Sprout does not claim to diagnose a student's mental health.

## Privacy Architecture

Privacy is a core design principle of Sprout.

### Journal storage

Journal content is encrypted before being stored using Fernet symmetric encryption.

### Counselor view

The counselor dashboard receives limited escalation information such as:

- Student identifier
- Risk level
- Signal summary
- Alert status
- Timestamp

The counselor API does not return raw journal text. Both demo views are scoped to the current browser workspace. A submitted student ID cannot change which workspace's records are returned. This prototype does not authenticate students or counselors.

### Local processing

The current prototype performs NLP analysis locally using the stored model artifacts rather than sending journal content to an external generative AI service.

## Counselor Dashboard

The counselor-facing interface provides:

- Total alert count
- High-risk signal count
- Pending review count
- Alerts requiring attention
- Signal overview
- Alert details
- Mark alerts pending, reviewed, or resolved
- Record review and resolution timestamps
- Privacy firewall explanation

The dashboard is intentionally limited to the information needed for support triage.

## Technology Stack

### Backend
- Python
- Flask
- SQLite

### Machine Learning
- scikit-learn
- TF-IDF
- Logistic Regression

### Frontend
- HTML5
- CSS3
- JavaScript

### Security
- Fernet symmetric encryption
- Local encrypted journal storage
- Privacy-focused counselor API

## Project Structure

```text
sprout/
├── app.py
├── nlp_model.py
├── risk_engine.py
├── database/
│   ├── init_db.py
│   └── schema.sql
├── models/
│   ├── char_vectorizer.pkl
│   ├── sprout_classifier.pkl
│   └── word_vectorizer.pkl
├── security/
│   └── encryption.py
├── templates/
│   ├── index.html
│   └── counselor.html
├── data/
│   └── CSV datasets are kept outside the repository
├── .gitignore
└── README.md
```

## Running Sprout Locally

### 1. Clone the repository

```bash
git clone https://github.com/udayjirwankar/sprout.git
cd sprout
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Flask application

```bash
python3 app.py
```

The application runs locally on:

```text
http://127.0.0.1:5001/
```

The home page opens the student view directly. Use **Counselor view** to see
alerts generated from submitted reflections and their review workflow. Both views
use the same browser workspace. Choose **New workspace** to start fresh.

The counselor view is available at:

```text
http://127.0.0.1:5001/counselor
```

Each visitor starts with an empty workspace. Reflections you submit are encrypted
and stored in that visitor's workspace. No sample journals or alerts are added.
Alerts are created only when the local model and signal engine flag a submitted reflection.
No journal text is stored in the browser cookie. There is no login or signup.

Demo records are kept in `database/demo.db`, separate from the existing
`database/sprout.db`. Existing records and any earlier account data are preserved;
this demo version does not open them. Browser sessions expire after eight hours
of inactivity. Old demo records are cleaned up after 24 hours when a new workspace
is created. This is a demonstration, rather than a permanent personal journal.

## Important Security Note

The encryption key used by the local application is intentionally excluded from this repository.

Do **not** commit:

```text
security/secret.key
security/session.key
```

The local SQLite database is also excluded from Git. Starting the app creates
missing tables and adds missing columns; it does not erase saved records.
Existing records are preserved; new workspaces start empty.

A signed Flask cookie identifies the demo workspace and carries a CSRF token.
It contains no journal text, account details, or passwords. The signing secret is
generated once for local use.

Optional configuration:

- `SPROUT_DEMO_DB_PATH`: alternative SQLite path for demo records.
- `SPROUT_ENCRYPTION_KEY`: an existing Fernet key; keep it stable to read saved journals.
- `SPROUT_SESSION_SECRET`: a stable secret for signing browser workspace cookies.
- `SPROUT_COOKIE_SECURE=1`: use secure cookies when serving over HTTPS.
- `SPROUT_DEBUG=1`: explicitly enable local development debugging.

Keep the database and its encryption key together when making a private backup.
Changing the encryption key does not re-encrypt existing journal entries.

This repository contains the application source and model artifacts, rather than private local data or encryption secrets.

## Prototype Limitations

Sprout is a student-built prototype.

The current NLP classifier and risk thresholds are intended for demonstrating the privacy-first architecture and support workflow. They should not be treated as a clinical assessment system or used as a substitute for qualified professional judgement.

A production system would require additional work including:

- More extensive model validation
- Bias and fairness evaluation
- Authentication and authorization for real student/counselor use
- Secure key management
- Production database infrastructure
- Audit logging
- Human-review workflows
- Privacy and security review
- Institutional policies and consent mechanisms

## Design Principles

### 🔒 Privacy by Default
Personal reflections should remain private unless a configured support signal requires escalation.

### 🤖 Signal, Not Diagnosis
AI assists with identifying potential wellbeing signals; it does not make clinical decisions.

### 👤 Human in the Loop
Escalation is designed to support human review rather than replace it.

### 🌱 A Kinder Digital Space
The student experience should feel like a safe place to reflect, not a system that watches them.

## Project

**Sprout — Privacy-First Student Wellbeing Platform**

Built by:

**Uday Jirwankar**

> Private words. Minimal signal. Human support.


## Verification

These checks use temporary databases and a temporary encryption key. They do not
read or modify your real journal database.

```bash
python3 -m unittest discover -s tests -v
node tests/test_journal_utils.js
```

The checks cover data preservation on restart, legacy schema upgrades, workspace
isolation, scoped counselor alerts, CSRF protection, atomic journal saving, saved
context, alert status changes, timezone handling, and streak logic.
