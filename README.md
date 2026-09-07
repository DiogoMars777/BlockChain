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

Si ya habías corrido `alembic upgrade head` antes y te quedaron solo 4 tablas
(o cualquier número menor a 41), hacé `git pull` para traer las migraciones
nuevas y volvé a correr `python -m alembic upgrade head` — no hace falta
borrar la base, sigue desde donde quedó.

### Datos de prueba

`python seed.py` carga automáticamente 5 empresas de demostración con datos
mínimos (usuario admin, roles, catálogo de productos, actores, ubicaciones y
unidades). Es seguro correrlo varias veces, no duplica nada. Para iniciar
sesión, usá el número de empresa como "Empresa (Slug)":

| # | Empresa | Correo admin | Contraseña |
|---|---|---|---|
| 1 | iStore Bolivia S.A. | admin@trazabilidad.com | Admin123! |
| 2 | TechImport Santa Cruz S.R.L. | admin@techimport.com | Admin123! |
| 3 | Andina Digital Ltda. | admin@andinadigital.com | Admin123! |
| 4 | ElectroSur Trading S.A. | admin@electrosur.com | Admin123! |
| 5 | Cochabamba Wireless S.A. | admin@cochawireless.com | Admin123! |

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
