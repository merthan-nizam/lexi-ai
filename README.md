# Lexi AI 🤖

**Türkiye'nin İlk %100 Offline CPU AI Asistanı**

Modern, gerçek zamanlı ve tamamen yerel çalışan AI chatbot uygulaması.

![Proje Yapısı](Proje%20Yapısı.jpg)

## ✨ Features

- **Fully Offline** — No internet required
- **CPU Only** — Works without GPU
- Real-time chat (WebSocket)
- User authentication (Register / Login)
- Conversation history
- Live system monitoring (CPU, RAM, Model status)
- Fully Turkish-speaking friendly AI assistant

## 🎯 AI Model Usage

- Default model: **`llama3.2:3b-instruct-q4_K_M`**
- You can use **any Ollama model** you want according to your computer's power.
- Low-end PC → 3B models  
- Mid-range → 7B models  
- High-end → 13B+ models

> The stronger your computer, the better models you can run.

---

## 🚀 Quick Start

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
- [Ollama](https://ollama.com)'yı indir ve kur
- Önerilen model:
```bash
ollama pull llama3.2:3b-instruct-q4_K_M
```

### 4. Run the Application
```bash
python main.py
```

Uygulamayı tarayıcıda açın: **http://localhost:8001**

---

## 🛠 Technologies

- **Backend**: FastAPI
- **Real-time**: WebSocket
- **AI Engine**: Ollama (Local LLMs)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

---

## 📁 Project Structure

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

## 📝 Türkçe Açıklama

**Lexi AI**, tamamen bilgisayarınızda çalışan, internet gerektirmeyen, sadece CPU ile çalışan Türkçe bir yapay zeka asistanıdır. Özellikle düşük ve orta seviye bilgisayarlar için optimize edilmiştir.

---

## 🔧 Configuration

`.env.example` dosyasını `.env` olarak kopyalayın ve `SECRET_KEY` değerini güçlü bir şifre ile değiştirin.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

**Developed by Merthan Nizam** — 2025


`lexi-ai.rar` dosyasını şimdilik bırakabiliriz. İleride istersen sileriz.

Şimdi README’yi güncellemek ister misin?
