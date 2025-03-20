import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import os
import base64
import tempfile

def initialize_firebase():
    # Decode the Base64 string from the environment variable
    firebase_credentials_b64 = settings.firebase_credentials
    if not firebase_credentials_b64:
        raise ValueError("FIREBASE_CREDENTIALS environment variable is missing")

    # Decode the Base64 string into bytes
    firebase_credentials_bytes = base64.b64decode(firebase_credentials_b64)

    # Create a temporary file and write the decoded credentials to it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(firebase_credentials_bytes)
        temp_file_path = temp_file.name

    # Path to your Firebase Admin SDK JSON file
    cred = credentials.Certificate(temp_file_path)
    firebase_admin.initialize_app(cred)

    # Clean up the temporary file (optional, but recommended)
    os.unlink(temp_file_path)

    # Get Firestore client
    db = firestore.client()
    return db

# Initialize Firestore and export the `db` variable
db = initialize_firebase()