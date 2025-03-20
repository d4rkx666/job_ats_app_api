import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings

def initialize_firebase():
    # Path to your Firebase Admin SDK JSON file
    cred = credentials.Certificate(settings.firebase_credentials_path)
    firebase_admin.initialize_app(cred)

    # Get Firestore client
    db = firestore.client()
    return db

# Initialize Firestore and export the `db` variable
db = initialize_firebase()