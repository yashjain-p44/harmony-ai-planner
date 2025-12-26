# Scripts

This directory contains utility scripts for project setup and maintenance.

## Available Scripts

### `regenerate_token.py`
Regenerates the Google Calendar OAuth token. Use this if you're getting "invalid_scope" or token expiration errors.

**Usage:**
```bash
python scripts/regenerate_token.py
```

### `regenerate_token_with_tasks.py`
Regenerates the Google OAuth token with both Calendar and Tasks scopes. This is needed if you want to use the Google Tasks API.

**Usage:**
```bash
python scripts/regenerate_token_with_tasks.py
```

### `test_firestore_connection.py`
Simple script to test the Firestore database connection. Queries all documents in the 'conversations' collection and prints them.

**Usage:**
```bash
python scripts/test_firestore_connection.py
```

