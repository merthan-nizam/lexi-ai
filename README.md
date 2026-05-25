# Lexi AI 🤖

**Türkiye'nin İlk %100 Offline CPU AI Asistanı**

Modern, gerçek zamanlı ve tamamen yerel çalışan AI chatbot uygulaması.

![Proje Yapısı](Proje%20Yapısı.jpg)

## ✨ Features

- **Fully Offline** - No internet required
- **CPU Only** - Works without GPU (Normal computers are enough)
- Real-time chat with WebSocket
- User authentication (Register / Login)
- Conversation history
- Live system monitoring (CPU, RAM, Model status)
- Fully Turkish-speaking, friendly and smart assistant

## 🎯 AI Model Usage

- Default model: **`llama3.2:3b-instruct-q4_K_M`**
- You can use **any Ollama model** you want
- Model selection depends on your computer's power:
  - Low-end PCs → 3B models
  - Mid-range → 7B models  
  - High-end → 13B+ models

> The stronger your computer, the better and larger models you can run.

---

## 🚀 Quick Start

### 1. Clone the Project
```bash
git clone https://github.com/merthan-nizam/lexi-ai
cd lexi-ai
2. Install Requirements
Bashpip install -r requirements.txt
3. Install Ollama
Download and install Ollama from ollama.com
Then pull a model:
Bashollama pull llama3.2:3b-instruct-q4_K_M
4. Run the Application
Bashpython main.py
Open your browser and go to: http://localhost:8001

🛠 Technologies

Backend: FastAPI
Real-time: WebSocket
AI Engine: Ollama (Local LLMs)
Frontend: HTML, CSS, JavaScript
Database: SQLite


📁 Project Structure
Bashlexi-ai/
├── main.py                 # Main file
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── templates/
├── static/
│   ├── css/
│   └── js/
├── config/
├── auth/
├── database/
├── websocket/
└── chatbot/

📝 Türkçe Açıklama (Turkish)
Lexi AI, tamamen bilgisayarınızda çalışan, internet gerektirmeyen, sadece CPU ile çalışan bir yapay zeka asistanıdır. FastAPI ve Ollama teknolojileri kullanılarak geliştirilmiştir.
Özellikle düşük ve orta seviye bilgisayarlar için optimize edilmiştir.

🔧 Configuration

Copy .env.example to .env
Edit the SECRET_KEY with a strong random string


📄 License
This project is licensed under the MIT License.

Developed by Merthan Nizam
2026