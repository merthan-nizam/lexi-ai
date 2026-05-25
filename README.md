
# Lexi AI ??

**Turkiye'nin ?lk %100 Offline CPU AI Asistan?**

Modern, gercek zamanl? ve tamamen yerel cal??an AI chatbot uygulamas?.

![Proje Yap?s?](Proje%20Yap?s?.jpg)

## ? Features

- **Fully Offline** — No internet required
- **CPU Only** — Works without GPU
- Real-time chat (WebSocket)
- User authentication (Register / Login)
- Conversation history
- Live system monitoring (CPU, RAM, Model status)
- Fully Turkish-speaking friendly AI assistant

## ?? AI Model Usage

- Default model: **`llama3.2:3b-instruct-q4_K_M`**
- You can use **any Ollama model** you want according to your computer's power.
- Low-end PC → 3B models  
- Mid-range → 7B models  
- High-end → 13B+ models

> The stronger your computer, the better models you can run.

---

## ?? Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/merthan-nizam/lexi-ai.git
cd lexi-ai
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Install Ollama
- [Ollama](https://ollama.com)'y? indir ve kur
- Onerilen model:
```bash
ollama pull llama3.2:3b-instruct-q4_K_M
```

### 4. Run the Application
```bash
python main.py
```

Uygulamay? taray?c?da ac?n: **http://localhost:8001**

---

## ?? Technologies

- **Backend**: FastAPI
- **Real-time**: WebSocket
- **AI Engine**: Ollama (Local LLMs)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

---

## ?? Project Structure

```
lexi-ai/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── templates/
├── static/
├── config/
├── auth/
├── database/
├── websocket/
└── chatbot/
```

---

## ?? Turkce Ac?klama

**Lexi AI**, tamamen bilgisayar?n?zda cal??an, internet gerektirmeyen, sadece CPU ile cal??an Turkce bir yapay zeka asistan?d?r. Ozellikle du?uk ve orta seviye bilgisayarlar icin optimize edilmi?tir.

---

## ?? Configuration

`.env.example` dosyas?n? `.env` olarak kopyalay?n ve `SECRET_KEY` de?erini guclu bir ?ifre ile de?i?tirin.

---

## ?? License

This project is licensed under the [MIT License](LICENSE).

**Developed by Merthan Nizam** — 2025


