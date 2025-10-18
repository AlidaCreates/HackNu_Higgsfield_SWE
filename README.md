# Higgsfield AI SWE


Минимальный проект (FastAPI backend + Next.js frontend) с mock mode для хакатона Higgsfield.


## Что внутри
- backend/: FastAPI API, `POST /api/generate` и `GET /api/status/{id}`
- frontend/: Next.js приложение с формой промпта и предпросмотром результата


## Как запустить локально


### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate # на Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# отредактируйте .env (USE_MOCK=true для экономии кредитов)
uvicorn main:app --reload --port 8000