# 🌱 Sprout

### Private words. Minimal signal. Human support.

Sprout is a privacy-first student wellbeing platform that gives students a private space to reflect while allowing authorized support staff to receive limited wellbeing signals when configured thresholds are met.

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

The counselor API does not return the student's raw journal text.

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

The counselor dashboard is available at:

```text
http://127.0.0.1:5001/counselor
```

## Important Security Note

The encryption key used by the local application is intentionally excluded from this repository.

Do **not** commit:

```text
security/secret.key
```

The local SQLite database is also excluded from Git.

This repository contains the application source and model artifacts, rather than private local data or encryption secrets.

## Prototype Limitations

Sprout is a student-built prototype.

The current NLP classifier and risk thresholds are intended for demonstrating the privacy-first architecture and support workflow. They should not be treated as a clinical assessment system or used as a substitute for qualified professional judgement.

A production system would require additional work including:

- More extensive model validation
- Bias and fairness evaluation
- Stronger authentication and authorization
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
