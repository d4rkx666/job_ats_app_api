# migration_script.py (Run once)
from firebase_admin import firestore
from app.services.firebase_service import db  # Import the Firestore client

def migrate_user(user_ref):
    try: 
        db = firestore.client()
        template = user_ref.document("template")
        global_rules = user_ref.document("global_rules")

        template = template.get().to_dict()
        global_rules = global_rules.get().to_dict()


        user_to_update = db.collection('chatgpt_prompt').document("creations")

        
        updates = {
            # Add new fields
            'templates.ats': template.get("ats", {}),
            'templates.classic': template.get("classic", {}),
            'templates.modern': template.get("modern", {}),
            'templates.executive': template.get('executive', {}),

            'global_rules': global_rules,
        }
        
        user_to_update.update(updates)
        
        return True
    except Exception as e:
        print(f"Error migrating user {user_ref.id}: {str(e)}")
        return False


    
# Run for all users
user_ref = db.collection('templates')
if migrate_user(user_ref):
    print("\nVerify migration:")
else:
    print("Migration failed")