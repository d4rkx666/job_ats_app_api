# migration_script.py (Run once)
from firebase_admin import firestore
from app.services.firebase_service import db  # Import the Firestore client

def migrate_user(user_ref):
    try: 
        db = firestore.client()
        user = user_ref.get().to_dict()
        
        updates = {
            # Add new fields
            'name': user.get("name", ""),
            'email': user.get("email", ""),
            'country': user.get("country", ""),
            'linkedin': user.get('linkedin', ''),
            'website': user.get('website', ''),
            
            # Transform subscription
            'subscription.current_period_start': user.get('subscription', {}).get('startDate', ''),
            'subscription.current_period_end': user.get('subscription', {}).get('endDate', ''),
            'subscription.payment_method': '',
            'subscription.stripe_id': '',
            'subscription.history': [],
            'subscription.plan': user.get('subscription', {}).get('plan', ''),
            'subscription.status': user.get('subscription', {}).get('status', ''),

            # Add usage
            'usage.actions.keyword_optimizations': 0,
            'usage.actions.resume_creations': 0,
            'usage.actions.resume_optimizations': user.get("settings.",{}).get("resumeImprovements",0),
            'usage.total_credits': 6,
            'usage.current_credits': user.get("settings.",{}).get("maximumImprovements",0) - (user.get("settings.",{}).get("resumeImprovements",0)*2),
            'usage.used_credits': (user.get("settings.",{}).get("resumeImprovements",0)*2),
            'usage.last_reset': firestore.SERVER_TIMESTAMP,
            'usage.next_reset': firestore.SERVER_TIMESTAMP,
        }

        # Field deletions must be separate for update()
        delete_updates = {
            'subscription.startDate': firestore.DELETE_FIELD,
            'subscription.endDate': firestore.DELETE_FIELD,
            'settings': firestore.DELETE_FIELD
        }
        
        user_ref.update(updates)
        user_ref.update(delete_updates)
        
        return True
    except Exception as e:
        print(f"Error migrating user {user_ref.id}: {str(e)}")
        return False

# TESTING WITH SINGLE USER
"""test_user_id = "aHF8pwgboKNGJxcxfIKHRVh467F2"
users_ref = db.collection('users').document(test_user_id)

if migrate_user(users_ref):
    print("\nVerify migration:")
    migrated_user = users_ref.get().to_dict()
    print(migrated_user)
else:
    print("Migration failed")"""


    
# Run for all users
users_ref = db.collection('users')
for user in users_ref.stream():
    user_ref = users_ref.document(user.id)
    if migrate_user(user_ref):
        print("\nVerify migration:")
        migrated_user = user_ref.get().to_dict()
        print(migrated_user)
    else:
        print("Migration failed")