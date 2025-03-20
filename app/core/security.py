import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token.credentials)

        # Check if the user's email is verified
        if not decoded_token.get("email_verified", False):
            print("raising error")
            raise HTTPException(status_code=403, detail="Email not verified")

        
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))