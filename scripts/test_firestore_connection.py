#!/usr/bin/env python3
"""
Simple script to test Firestore database connection.
Queries all documents in the 'conversations' collection and prints them.
"""

import os
import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# Get the path to the credentials file
project_root = Path(__file__).parent.parent
creds_path = project_root / "app" / "creds" / "ai-task-master-7dc79-firebase-adminsdk-fbsvc-9d2fe1e4e1.json"

def test_firestore_connection():
    """Test Firestore connection and query conversations collection."""
    
    # Check if credentials file exists
    if not creds_path.exists():
        print(f"Error: Credentials file not found at {creds_path}")
        sys.exit(1)
    
    print(f"Using credentials file: {creds_path}")
    
    # Initialize Firebase Admin SDK
    try:
        cred = credentials.Certificate(str(creds_path))
        firebase_admin.initialize_app(cred)
        print("✓ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        sys.exit(1)
    
    # Get Firestore client
    try:
        db = firestore.client()
        print("✓ Firestore client created successfully")
    except Exception as e:
        print(f"Error creating Firestore client: {e}")
        sys.exit(1)
    
    # Query all documents in 'conversations' collection
    try:
        print("\nQuerying 'conversations' collection...")
        conversations_ref = db.collection('conversations')
        docs = conversations_ref.stream()
        
        doc_count = 0
        for doc in docs:
            doc_count += 1
            print(f"\n--- Document {doc_count} ---")
            print(f"Document ID: {doc.id}")
            print(f"Document Data:")
            doc_data = doc.to_dict()
            if doc_data:
                # Pretty print the document data
                import json
                print(json.dumps(doc_data, indent=2, default=str))
            else:
                print("  (empty document)")
        
        if doc_count == 0:
            print("No documents found in 'conversations' collection")
        else:
            print(f"\n✓ Total documents retrieved: {doc_count}")
            
    except Exception as e:
        print(f"Error querying Firestore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✓ Firestore connection test completed successfully!")

if __name__ == "__main__":
    test_firestore_connection()

