from firebase_admin import auth
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: Request):
    # Get cookie from session
    session_cookie = token.cookies.get("session")

    if not session_cookie:
        raise HTTPException(status_code=401, detail="No active session")
    
    try:
        decoded_token = auth.verify_session_cookie(session_cookie, check_revoked=True)
        
        if not decoded_token.get("email_verified", False):
            raise HTTPException(status_code=403, detail="Email not verified")
            
        return decoded_token
    except auth.RevokedSessionCookieError:
        raise HTTPException(status_code=401, detail="Revoked session")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")