Manger - a password manager

A secure, cross-platform, Zero-Knowledge password manager built with Python and Kotlin. This project features a desktop client, Android app, and a server sync, all communicating via a strict Zero-Knowledge architecture with end-to-end encryption.

Tech Stack
This project is structured as a monorepo containing three distinct applications:
- **Backend Sync Server:** Python, FastAPI, Uvicorn (REST API)
- **Desktop Client:** Python, PyQt6, Cryptography, Argon2-cffi
- **Mobile Client:** Kotlin, Android Studio, OkHttp, Tink (Android Security)