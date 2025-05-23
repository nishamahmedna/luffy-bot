# LuffyBot – AI-Powered Chit-Chat & Perception Bot

LuffyBot is an intelligent AI companion that combines real-time vision with voice-based interaction. It answers open-ended chit-chat using LLMs and simultaneously monitors the environment through object detection and OCR. In future upgrades, it can be extended to provide safety alerts and autonomous threat awareness.

## 🧠 Core Capabilities

- 💬 Real-time voice interaction using speech recognition
- 🤖 Chit-chat responses using LLMs (ChatGPT, Gemini, OpenRouter)
- 👁️ Object detection using YOLOv8 or CV
- 📷 Visual awareness: environment analysis and narration
- 🧠 Designed for risk/threat analysis in future iterations

## 💻 Tech Stack

- Python, SpeechRecognition, pyttsx3
- OpenAI API / OpenRouter / Gemini for LLM interaction
- YOLOv8, OpenCV, Tesseract OCR for real-time vision
- Raspberry Pi / Robelf / Kinect / LEGO Mindstorms hardware support

## 🤖 System Use Case

- Acts as a semi-autonomous robot assistant
- Designed to observe and interpret real-world surroundings
- Speaks about what it “sees” and answers open-ended questions

## 🚀 Getting Started

```bash
pip install -r requirements.txt
python main.py
