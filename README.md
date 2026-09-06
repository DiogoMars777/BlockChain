# Sistema de Trazabilidad Multi-Tenant

Backend (FastAPI), frontend (Angular) y app móvil (Flutter) para el sistema de trazabilidad.

## Backend

```powershell
cd trazabilidad/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # completar DATABASE_URL, JWT_SECRET, SMTP_USER/PASSWORD
python -m alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000 — Docs: http://127.0.0.1:8000/docs

`alembic upgrade head` crea las 41 tablas completas del esquema (las 20 que ya
usa el código de Sprint 0/1, más las 21 de sprints futuros que todavía no
tienen modelos/controllers pero ya existen en el diseño de base de datos).
Cada compañero migra su propia base local — no comparten la misma DB.

## Frontend

```powershell
cd trazabilidad/frontend
npm install
ng serve
```

http://localhost:4200

## Mobile

```bash
cd trazabilidad/mobile
flutter pub get
flutter run
```

Requiere Flutter SDK y un emulador/dispositivo Android o iOS conectado.
