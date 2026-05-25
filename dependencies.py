# auth/dependencies.py
from fastapi import Cookie, HTTPException
from database.memory_db import MemoryDatabase

db = MemoryDatabase()

def get_current_user(lexi_session: str = Cookie(None)):
    if not lexi_session:
        raise HTTPException(status_code=401, detail="Giriş yapmadın")
    user_id = db.get_user_from_session(lexi_session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Oturum süresi dolmuş")
    return user_id