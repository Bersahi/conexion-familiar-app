from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import User

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def get_emisor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Solo el emisor puede hacer esto")
    return current_user

def get_receptor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Solo el receptor puede hacer esto")
    return current_user