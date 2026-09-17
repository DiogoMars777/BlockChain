# Sistema de Trazabilidad Multi-Tenant

Backend (FastAPI), frontend (Angular) y app móvil (Flutter).

---

## 1. Backend (FastAPI + PostgreSQL)

```powershell
# 1. Entrar a la carpeta backend
cd trazabilidad/backend

# 2. Activar el entorno virtual (ya creado en .venv)
.\.venv\Scripts\Activate.ps1

# 3. Instalar librerias (si es primera vez)
pip install -r requirements.txt

# 4. Configurar variables de entorno en .env (DATABASE_URL con tu clave de Postgres)
# DATABASE_URL=postgresql+psycopg://postgres:TU_CLAVE@localhost:5432/BLACKCHAIN

# 5. Ejecutar migraciones de base de datos
python -m alembic upgrade head

# 6. Poblar datos base del sistema (5 empresas y usuarios admin)
python seed.py

# 7. Poblar datos de Sprint 2 (CU-011 compras, CU-016 codigos QR, CU-021 envios y transportes)
python seed_sprint2.py

# 8. Iniciar el servidor local
python -m uvicorn app.main:app --reload
```

* **API Local:** http://127.0.0.1:8000
* **Documentación interactiva (Swagger):** http://127.0.0.1:8000/docs

---

## 2. Frontend Web (Angular)

```powershell
# 1. Entrar a la carpeta frontend
cd trazabilidad/frontend

# 2. Instalar dependencias npm (si es primera vez)
npm install

# 3. Levantar la aplicacion web
npm start
```

* **Aplicación Web:** http://localhost:4200

### Credenciales de acceso de prueba:
* **Contraseña general:** `Admin123!`
* **Empresa 1 (Slug: 1):** `admin@trazabilidad.com`
* **Empresa 2 (Slug: 2):** `admin@techimport.com`
* **Empresa 3 (Slug: 3):** `admin@andinadigital.com`

---

## 3. App Móvil (Flutter)

```powershell
# 1. Entrar a la carpeta mobile
cd trazabilidad/mobile

# 2. Obtener paquetes de Flutter
flutter pub get

# 3. Ejecutar en navegador web Chrome (sin emulador)
flutter run -d chrome

# 4. O ejecutar en dispositivo/emulador conectado
flutter run
```
