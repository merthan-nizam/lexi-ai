# auth/routes.py
from fastapi import APIRouter, Request, Response, HTTPException
from database.memory_db import MemoryDatabase
from config.settings import SESSION_MAX_AGE_SECONDS

db = MemoryDatabase()
router = APIRouter(prefix="/auth")

@router.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    display_name = data.get("display_name")

    if not username or not password:
        raise HTTPException(400, "Kullanıcı adı ve şifre gerekli")

    user_id = db.create_user(username, password, display_name)
    if not user_id:
        raise HTTPException(400, "Bu kullanıcı adı zaten alınmış")

    session_id = db.create_session(user_id)
    response = {"success": True, "message": "Kayıt başarılı!", "username": username}
    resp = Response(content=response, media_type="application/json")
    resp.set_cookie("lexi_session", session_id, max_age=SESSION_MAX_AGE_SECONDS, httponly=True, samesite="lax")
    return resp

@router.post("/login")
async def login(request: Request):
    data = await request.json()
    user_id = db.verify_user(data.get("username"), data.get("password"))
    if not user_id:
        raise HTTPException(401, "Kullanıcı adı veya şifre yanlış")

    session_id = db.create_session(user_id)
    resp = Response(content={"success": True, "message": "Giriş başarılı!"}, media_type="application/json")
    resp.set_cookie("lexi_session", session_id, max_age=SESSION_MAX_AGE_SECONDS, httponly=True, samesite="lax")
    return resp

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("lexi_session")
    return {"success": True}

@router.get("/check")
async def check(lexi_session: str = Cookie(None)):
    if not lexi_session:
        return {"authenticated": False}
    user_id = db.get_user_from_session(lexi_session)
    if not user_id:
        return {"authenticated": False}
    info = db.get_user_info_full(user_id)
    info["authenticated"] = True
    info["message_count"] = db.get_conversation_count(user_id)
    return info