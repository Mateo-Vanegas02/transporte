# FastAPI MySQL - Arquitectura por Capas (Repository + Service)

API REST modular y desacoplada construida con **FastAPI**, **SQLAlchemy 2.0** y **MySQL**, siguiendo principios de diseño limpio, inyección de dependencias y separación estricta de responsabilidades.

---

## 🏗️ Arquitectura del Sistema

El proyecto implementa un flujo desacoplado por capas:

```
Petición HTTP
     │
     ▼
[Router (app/api/users.py)]
     │ (Traduce DTOs y excepciones de dominio a HTTP 404, 409, etc.)
     ▼
[Service (app/services/user_service.py)]
     │ (Reglas de negocio, validaciones de unicidad y excepciones propias)
     ▼
[Repository (app/repositories/user_repository.py)]
     │ (Acceso directo a datos con SQLAlchemy 2.0, sin lógica de negocio)
     ▼
[Base de Datos (MySQL)]
```

---

## 🛠️ Stack Tecnológico

- **Python**: 3.11+
- **Framework Web**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0 (estilo tipado con `Mapped` y `mapped_column`)
- **Driver de BD**: PyMySQL + Cryptography
- **Validación y Configuración**: Pydantic v2 + Pydantic-Settings
- **Testing y Calidad**: Pytest, HTTPX, Black, Flake8

---

## 📂 Estructura del Proyecto

```
fastapi_mysql/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Instancia de FastAPI y ciclo de vida (lifespan)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Settings (Pydantic-Settings) y database_url
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py              # Engine con pool_pre_ping, SessionLocal y Base ORM
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                 # Modelo SQLAlchemy 2.0 (tabla users)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py                 # DTOs Pydantic (UserCreate, UserUpdate, UserRead)
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py      # Capa de persistencia (SQLAlchemy queries)
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py         # Lógica de negocio y excepciones de dominio
│   └── api/
│       ├── __init__.py
│       ├── deps.py                 # Inyección de dependencias (get_db, get_user_service)
│       └── users.py                # Endpoints HTTP /users
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Configuración de pruebas (SQLite in-memory + TestClient)
│   └── test_users.py               # Casos de prueba exhaustivos del CRUD
├── .env                            # Variables de entorno locales (ignorado por git)
├── .env.example                    # Plantilla de variables de entorno
├── .flake8                         # Configuración de linter Flake8
├── .gitignore                      # Exclusiones de Git (.venv, .env, __pycache__, etc.)
├── docker-compose.yml              # Contenedor de MySQL 8 para entorno local
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de desarrollo y testing
└── README.md                       # Documentación del proyecto
```

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos

- Python 3.11 o superior instalado.
- MySQL Server 8.0+ instalado localmente o Docker Desktop.

### 2. Crear y Activar Entorno Virtual

En Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalación de Dependencias

Para producción:
```bash
pip install -r requirements.txt
```

Para desarrollo y ejecución de pruebas:
```bash
pip install -r requirements-dev.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y ajusta las credenciales de tu base de datos:

```bash
cp .env.example .env
```

Contenido del archivo `.env`:
```ini
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fastapi_db
```

---

## 🗄️ Base de Datos

### Opción A: Levantar MySQL con Docker Compose (Recomendado)

Ejecuta el siguiente comando para iniciar un contenedor de MySQL 8 configurado con charset UTF-8:

```bash
docker compose up -d
```

### Opción B: Crear la BD en un MySQL local existente

Conéctate a tu cliente MySQL y crea la base de datos con soporte completo para UTF-8:

```sql
CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## ▶️ Ejecución del Servidor

Inicia el servidor de desarrollo con recarga automática:

```bash
uvicorn app.main:app --reload
```

- **API Base**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentación Interactiva Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Endpoint de Salud**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Ejecución de Pruebas y Linters

### Correr Pruebas Unitarias y de Integración

Las pruebas utilizan SQLite en memoria (`sqlite:///:memory:`) con aislamiento por prueba, por lo que **no requieren que MySQL esté encendido**:

```bash
pytest -v
```

### Comprobación de Calidad de Código (PEP 8)

Formateo con Black:
```bash
black --check app tests
```

Linter con Flake8:
```bash
flake8 app tests
```

---

## 📡 Endpoints Disponibles

| Método | Endpoint | Código Éxito | Descripción |
|---|---|---|---|
| `GET` | `/health` | `200 OK` | Verificación de estado de la API |
| `GET` | `/users` | `200 OK` | Lista paginada (`?skip=0&limit=100`) de usuarios |
| `GET` | `/users/{id}` | `200 OK` | Consulta usuario por ID (`404` si no existe) |
| `POST` | `/users` | `201 Created` | Registra nuevo usuario (`409` si el email existe) |
| `PUT` | `/users/{id}` | `200 OK` | Actualiza usuario (`404` o `409` si email en conflicto) |
| `DELETE` | `/users/{id}` | `204 No Content` | Elimina usuario (`404` si no existe) |

---

## 🔄 Migración a Alembic (Próximos Pasos)

El proyecto actualmente inicializa el esquema con `Base.metadata.create_all(bind=engine)` durante el arranque (`lifespan`). Para proyectos en producción con evolución de esquema, se recomienda migrar a **Alembic**:

1. Instalar Alembic:
   ```bash
   pip install alembic
   ```
2. Inicializar entorno de migraciones:
   ```bash
   alembic init alembic
   ```
3. Configurar `alembic/env.py`:
   - Importar la configuración y modelos:
     ```python
     from app.core.config import settings
     from app.db.session import Base
     from app.models.user import User  # Registrar modelos

     target_metadata = Base.metadata
     config.set_main_option("sqlalchemy.url", settings.database_url)
     ```
4. Generar la primera migración:
   ```bash
   alembic revision --autogenerate -m "create users table"
   ```
5. Aplicar migraciones:
   ```bash
   alembic upgrade head
   ```
