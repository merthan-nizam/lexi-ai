# =============================================
# LEXI v2.0 - Türkiye'nin İlk ve Tek %100 Offline CPU AI Asistanı
# =============================================

import os
import sys
import json
import uuid
import logging
import asyncio
import sqlite3
import hashlib
import psutil
import httpx
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# VERİTABANI
# =============================================
class MemoryDatabase:
    def __init__(self, db_path="lexi_memory.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
                     user_id TEXT PRIMARY KEY, username TEXT UNIQUE, 
                     password_hash TEXT, display_name TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (
                     session_id TEXT PRIMARY KEY, user_id TEXT, expires_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS conversations (
                     id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, 
                     role TEXT, content TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS feedback (
                     id INTEGER PRIMARY KEY AUTOINCREMENT, user_message TEXT,
                     bot_message TEXT, feedback TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
        conn.close()
        logger.info("Hafıza veritabanı hazır!")

    def hash_password(self, pwd): 
        return hashlib.sha256(pwd.encode()).hexdigest()

    def create_user(self, username, password, display_name=None):
        try:
            user_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                      (user_id, username, self.hash_password(password), display_name or username))
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None

    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT user_id, display_name FROM users WHERE username=? AND password_hash=?",
                  (username, self.hash_password(password)))
        row = c.fetchone()
        conn.close()
        return {"user_id": row[0], "display_name": row[1]} if row else None

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        expires = (datetime.now() + timedelta(days=365)).isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", 
                  (session_id, user_id, expires))
        conn.commit()
        conn.close()
        return session_id

    def get_user_from_session(self, session_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT user_id, expires_at FROM sessions WHERE session_id=?", (session_id,))
        row = c.fetchone()
        conn.close()
        if row and datetime.fromisoformat(row[1]) > datetime.now():
            return row[0]
        return None

    def save_message(self, user_id, role, content):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
                  (user_id, role, content))
        conn.commit()
        conn.close()

    def get_conversation_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""SELECT role, content FROM conversations 
                     WHERE user_id=? ORDER BY timestamp DESC LIMIT ?""", (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return list(reversed(rows))

    def save_feedback(self, user_msg, bot_msg, feedback):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO feedback (user_message, bot_message, feedback) VALUES (?, ?, ?)",
                  (user_msg, bot_msg, feedback))
        conn.commit()
        conn.close()

db = MemoryDatabase()

# =============================================
# CHATBOT 
# =============================================
class Chatbot:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.db = db
        self.model_ready = True                  
        self.model_name = "llama3.2:3b-instruct-q4_K_M"  
        logger.info("Chatbot başlatıldı - Model: llama3.2:3b-instruct-q4_K_M")

    async def get_available_model(self) -> str:
        """Yüklü modeli bul"""
            

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code != 200:
                    return None
                
                data = response.json()
                models = data.get("models", [])
                
                    # 1. ÖNCELİK: Llama 3.2 serisi (en hızlı + kaliteli)
                for m in models:
                    name = m.get("name", "").lower()
                    if "llama3.2:3b-instruct-q4_K_M" in name:
                        return "llama3.2:3b-instruct-q4_K_M"
                        
               
                        
                # Hiçbir şey yoksa ilk modeli al
                if models:
                    return models[0].get("name")
                    
                return None
        except Exception as e:
            logger.error(f"Model kontrol hatası: {e}")
            return None

    async def check_and_load_model(self) -> bool:
        model = await self.get_available_model()
        if model:
            self.model_name = "llama3.2:3b-instruct-q4_K_M"
            self.model_ready = True
            logger.info("Model zorla yüklendi: llama3.2:3b-instruct-q4_K_M")
            return True
        return False

    def _build_prompt(self, user_id: str, new_message: str) -> str:
        # Konuşma geçmişini al
        history = self.db.get_conversation_history(user_id, limit=4)
        
        history_text = ""
        for role, content in history:
            if role == "user":
                history_text += f"Kullanıcı: {content}\n"
            else:
                history_text += f"LEXI: {content}\n"
        
        return f"""Sen LEXI adında, Türkçe konuşan akıllı ve samimi bir AI asistanısın.

Kuralların:
- Sorulan soruya DOĞRUDAN cevap ver
- Kısa ve öz ol (1-3 cümle)
- Emoji kullanabilirsin
- Eğer adın sorulursa "LEXI" de
- Eğer yaratıcın sorulursa "Merthan Nizam isimli geliştirici tarafından oluşturuldum" de
- HER ZAMAN Türkçe cevap ver

{history_text}Kullanıcı: {new_message}
LEXI:"""

    async def generate_response(self, message: str, user_id: str) -> str:
        if not await self.check_and_load_model():
            return "⚠️ Model yüklü değil. Lütfen 'ollama pull ...model _adı...' komutunu çalıştırın."

        try:
            logger.info(f"Ollama'ya istek gönderiliyor: {message[:30]}...")
            
            full_prompt = self._build_prompt(user_id, message)
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_ctx": 512,
                    "num_predict": 512,
                    "num_thread": max(1, psutil.cpu_count() // 2),  # CPU'nun yarısını kullan
                    "repeat_penalty": 1.1,
                    "stop": ["\n\n", "Kullanıcı:", "User:"]
                }
            }

            response = await self.client.post(
                "http://localhost:11434/api/generate", 
                json=payload, 
                timeout=None
            )

            if response.status_code != 200:
                logger.error(f"Ollama HTTP hatası: {response.status_code}")
                return "Model şu anda yoğun, lütfen tekrar deneyin."

            data = response.json()
            raw_response = data.get("response", "").strip()

            if not raw_response:
                return "Anlayamadım, tekrar sorabilir misin? 🤔"

            # Temizle
            raw_response = raw_response.replace("<pad>", "").replace("[PAD]", "")
            raw_response = raw_response.replace("[BOS]", "").replace("[EOS]", "")
            raw_response = raw_response.strip()
            
            # Mesajları kaydet
            self.db.save_message(user_id, "user", message)
            self.db.save_message(user_id, "assistant", raw_response)
            
            logger.info(f"Başarılı yanıt: {raw_response[:40]}...")
            return raw_response

        except httpx.TimeoutException:
            return "⏳ Yanıt çok uzun sürdü. Lütfen daha kısa bir soru deneyin."
        except httpx.ConnectError:
            return "🔌 Ollama bağlantı hatası! Ollama'nın çalıştığından emin olun."
        except Exception as e:
            logger.error(f"Ollama hatası: {str(e)}")
            return f"Bir hata oluştu. Lütfen tekrar deneyin."

chatbot = Chatbot()
# =============================================
# MONİTÖR – GÜNCEL, EKSİKSİZ, ORJİNALE SADIK + EKSTRA GELİŞTİRMELER
# =============================================
async def monitor_system_resources(websocket: WebSocket):
    try:
        while True:
            try:
                # Model adı yoksa otomatik kontrol et
                if not chatbot.model_name:
                    await chatbot.check_and_load_model()

                # Sistem kaynakları
                cpu_percent = psutil.cpu_percent(interval=0.5) 
                ram = psutil.virtual_memory()
                ram_percent = round(ram.percent, 1)

                # Ollama durumu
                ollama_running = await check_ollama_status()
                model_loaded = bool(chatbot.model_name) and ollama_running

                # Ollama'nın gerçek RAM kullanımı
                ollama_ram = await get_ollama_memory_usage()

                # Frontend'e gönderilecek veri
                await websocket.send_json({
                    "type": "status",
                    "websocket": True,
                    "model": ollama_running,
                    "gemma_loaded": model_loaded,
                    "model_name": chatbot.model_name or "Tespit ediliyor...",  
                    "cpu_percent": round(cpu_percent, 1),
                    "ram_percent": ram_percent,
                    "model_ram_percent": round(ollama_ram, 1),
                    "progress": 100 if model_loaded else 0
                })

                await asyncio.sleep(3)

            except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
                break
            except Exception as e:
                logger.error(f"Monitor iç hata: {e}")
                await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"Monitor task tamamen çöktü: {e}")

async def check_ollama_status():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except:
        return False

async def check_ollama_status():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except:
        return False


async def get_ollama_memory_usage():
    """Ollama'nın gerçek RAM kullanımını bul"""
    try:
        for proc in psutil.process_iter(['name', 'memory_percent']):
            name = proc.info.get('name', '').lower()
            if 'ollama' in name:
                return round(proc.info.get('memory_percent', 0), 1)
    except:
        pass
    return 0


# =============================================
# AUTH ENDPOINTS
# =============================================
@app.post("/auth/register")
async def register(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        display_name = data.get("display_name")
        
        if not username or not password:
            return JSONResponse({"error": "Kullanıcı adı ve şifre gerekli"}, status_code=400)
        
        user_id = db.create_user(username, password, display_name)
        
        if not user_id:
            return JSONResponse({"error": "Bu kullanıcı adı zaten mevcut"}, status_code=400)
        
        session_id = db.create_session(user_id)
        
        response = JSONResponse({"success": True, "message": "Kayıt başarılı!", "username": username, "display_name": display_name or username})
        response.set_cookie(key="lexi_session", value=session_id, max_age=31536000, httponly=True, samesite="lax")
        return response
        
    except Exception as e:
        logger.error(f"Register hatası: {e}")
        return JSONResponse({"error": f"Kayıt başarısız"}, status_code=500)

@app.post("/auth/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        user_data = db.verify_user(username, password)
        
        if not user_data:
            return JSONResponse({"error": "Kullanıcı adı veya şifre yanlış"}, status_code=401)
        
        session_id = db.create_session(user_data["user_id"])
        
        response = JSONResponse({
            "success": True, 
            "message": "Giriş başarılı!", 
            "username": username,
            "display_name": user_data["display_name"]
        })
        response.set_cookie(key="lexi_session", value=session_id, max_age=31536000, httponly=True, samesite="lax")
        return response
        
    except Exception as e:
        logger.error(f"Login hatası: {e}")
        return JSONResponse({"error": "Giriş başarısız"}, status_code=500)

@app.post("/auth/logout")
async def logout():
    response = JSONResponse({"success": True})
    response.delete_cookie("lexi_session")
    return response

@app.get("/auth/check")
async def check_auth(request: Request):
    session_id = request.cookies.get("lexi_session")
    if not session_id:
        return JSONResponse({"authenticated": False})
    user_id = db.get_user_from_session(session_id)
    if not user_id:
        return JSONResponse({"authenticated": False})
    return JSONResponse({"authenticated": True, "username": "kullanıcı"})

# =============================================
# HEALTH & STATUS ENDPOINTS
# =============================================
# =============================================
# HEALTH & STATUS ENDPOINTS
# =============================================
@app.get("/health")
async def health():
    try:
        ollama_ok = await check_ollama_status()

        # Ollama çalışıyorsa ama model adı hâlâ None ise → tekrar dene
        if ollama_ok and not chatbot.model_name:
            await chatbot.check_and_load_model()

        
        model_loaded = ollama_ok and chatbot.model_name is not None

        return {
            "status": "healthy",
            "ollama_running": ollama_ok,
            "model_loaded": model_loaded,        
            "model_name": chatbot.model_name
        }
    except Exception as e:
        return {
            "status": "error",
            "ollama_running": False,
            "model_loaded": False,
            "model_name": None,
            "error": str(e)
        }
    
@app.get("/env-status")
async def env_status():
    # Sanal ortam kontrolü
    is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    return {
        "status": "healthy",
        "is_virtualenv_active": is_venv,
        "python_path": sys.executable,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ollama-status")
async def ollama_status():
    status = await check_ollama_status()
    return {"ollama_running": status, "model_name": chatbot.model_name}

@app.post("/feedback")
async def feedback(request: Request):
    try:
        data = await request.json()
        db.save_feedback(data.get("user_message", ""), data.get("bot_message", ""), data.get("feedback", ""))
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# =============================================
# WEBSOCKET
# =============================================
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    session_id = None
    cookies = websocket.headers.get("cookie", "")
    for part in cookies.split(";"):
        if "lexi_session" in part:
            session_id = part.split("=")[1].strip()
            break

    if not session_id:
        await websocket.close(code=1008)
        return

    user_id = db.get_user_from_session(session_id)
    
    if not user_id:
        await websocket.close(code=1008)
        return

    logger.info(f"WebSocket bağlandı → {user_id}")
    monitor_task = asyncio.create_task(monitor_system_resources(websocket))

    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=300)
            if data.lower() == "ping":
                await websocket.send_text("pong")
                continue
            
            # JSON parse et
            message_id = None
            try:
                msg_data = json.loads(data)
                message = msg_data.get("text", data)
                message_id = msg_data.get("messageId")
            except:
                message = data
            
            response = await chatbot.generate_response(message, user_id)
            
            # messageId ile geri gönder
            if message_id:
                await websocket.send_text(json.dumps({"text": response, "messageId": message_id}))
            else:
                await websocket.send_text(response)
            
    except (WebSocketDisconnect, asyncio.TimeoutError):
        logger.info(f"Bağlantı kapandı → {user_id}")
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}")
    finally:
        monitor_task.cancel()

# =============================================
# ANA SAYFA
# =============================================
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    logger.info("LEXI sunucusu başlatılıyor...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
