# conexion-familiar-app


Plataforma web que facilita la gestión de remesas familiares entre un emisor (Carlos, desde Estados Unidos) y un receptor (Don Alex, en Guatemala). Permite registrar envíos en USD, solicitar montos en GTQ, visualizar el historial de transacciones y confirmar recepciones, con conversión de moneda automática e inmutable al momento de cada transacción.

---

## Stack Tecnológico

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic
- **Frontend:** React 18, Vite
- **Base de datos:** PostgreSQL 15
- **Infraestructura:** Docker, Docker Compose

---

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Git

---

## Levantar el Entorno

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/conexion-familiar-app.git
cd conexion-familiar-app
```

2. Crear el archivo de variables de entorno:

```bash
cp backend/.env.example backend/.env
```

3. Levantar todos los servicios con un solo comando:

```bash
docker-compose up --build
```

4. Aplicar las migraciones de base de datos:

```bash
docker-compose exec backend alembic upgrade head
```

5. Insertar los roles iniciales:

```bash
docker-compose exec db psql -U postgres -d conexion_familiar -c "INSERT INTO roles (name) VALUES ('emisor'), ('receptor');"
```

Los servicios quedan disponibles en:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs

---

## Estructura del Proyecto
conexion-familiar-app/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── dependencies.py
│       │   └── security.py
│       ├── db/
│       │   ├── base.py
│       │   └── session.py
│       ├── models/
│       ├── schemas/
│       ├── routers/
│       └── services/
├── frontend/
│   ├── Dockerfile
│   └── src/
└── README.md

---

## Flujo de Uso

### Registro de usuario
POST /auth/register
{
"name": "Carlos",
"email": "carlos@test.com",
"password": "tu_password",
"role_id": 1
}

### Login
POST /auth/login
{
"email": "carlos@test.com",
"password": "tu_password"
}

Devuelve un `access_token` JWT que debe enviarse en el header de cada petición protegida:
Authorization: Bearer <access_token>

### Endpoints principales

| Método | Ruta | Rol requerido | Descripción |
|--------|------|---------------|-------------|
| POST | /auth/register | Público | Registrar usuario |
| POST | /auth/login | Público | Iniciar sesión |
| POST | /transactions/send | Emisor | Registrar envío en USD |
| POST | /transactions/request | Receptor | Solicitar monto en GTQ |
| GET | /transactions/history | Ambos | Historial paginado |
| PATCH | /transactions/{id}/confirm | Receptor | Confirmar recepción |

---

## Preguntas de Reflexión

### 1. API de tipo de cambio y resiliencia

Se utilizó **Frankfurter** como API de tipo de cambio por tres razones principales: es completamente gratuita, no requiere API Key lo que elimina fricción de configuración, y soporta consulta de tasas históricas por fecha, que es un requisito del sistema. Para el manejo de errores, las llamadas a la API están encapsuladas en el servicio `exchange_rate.py` usando `httpx` con manejo de excepciones. Si la API falla, el endpoint devuelve un error controlado al cliente en lugar de propagar una excepción no manejada.

### 2. Decisiones técnicas y librerías

- **SQLAlchemy** como ORM para abstraer las consultas a PostgreSQL y definir los modelos de forma declarativa, lo que facilita las migraciones y el mantenimiento.
- **Alembic** para el versionado de migraciones de base de datos, permitiendo rastrear y revertir cambios en el esquema.
- **Pydantic v2** para validación estricta de datos de entrada y salida en cada endpoint, garantizando integridad desde la capa de la API.
- **python-jose** para la generación y verificación de tokens JWT con expiración.
- **passlib con bcrypt** para el hash seguro de contraseñas.
- **httpx** para el consumo asíncrono de la API externa de tipo de cambio.

### 3. Arquitectura del backend

El backend sigue una arquitectura en capas con separación clara de responsabilidades:

- **Routers:** reciben las peticiones HTTP y delegan la lógica.
- **Services:** contienen la lógica de negocio, como la consulta a la API de cambio.
- **Models:** definen la estructura de la base de datos mediante SQLAlchemy.
- **Schemas:** validan y serializan los datos con Pydantic.
- **Core:** agrupa configuración, seguridad y dependencias reutilizables.

Esta separación permite escalar el sistema de forma ordenada. Si se necesita agregar nuevos módulos, como notificaciones o reportes, se crean capas independientes sin modificar las existentes. También facilita la escritura de pruebas unitarias por capa.

### 4. Inmutabilidad de los montos

Cuando se procesa una transacción, el sistema consulta la tasa de cambio vigente en ese momento a través de Frankfurter y la almacena junto con la transacción en los campos `exchange_rate`, `amount_usd` y `amount_gtq`. Adicionalmente, se guarda un registro en la tabla `exchange_rate_logs` vinculado a la transacción. Una vez que la transacción es creada, estos valores nunca se recalculan ni se modifican, independientemente de cómo cambie la tasa en el futuro. La tasa queda fija en la base de datos como parte del registro histórico.

### 5. Retos

El reto más complejo fue la configuración del entorno con Docker en desarrollo, particularmente la resolución de módulos de Python dentro del contenedor y la compatibilidad entre versiones de `passlib` y `bcrypt`, que generó errores no evidentes hasta tiempo de ejecución. También requirió atención el orden correcto de inicialización de los modelos de SQLAlchemy para evitar errores de mapeo entre relaciones.

### 6. Mejoras con tiempo adicional

Con una semana extra se priorizarían las siguientes mejoras:

- **Refresh tokens:** implementar un mecanismo de renovación de tokens para no forzar al usuario a hacer login frecuentemente.
- **Rate limiting:** agregar límites de peticiones por IP en los endpoints de autenticación para prevenir ataques de fuerza bruta.
- **Variables de entorno en frontend:** manejar la URL del backend desde variables de entorno para facilitar el despliegue en distintos ambientes.
- **Pruebas unitarias:** agregar cobertura de pruebas con pytest en los servicios y endpoints críticos.
- **Accesibilidad:** mejorar la interfaz de Don Alex para que sea más simple y accesible desde dispositivos móviles de gama baja.

---

## Variables de Entorno

Crea un archivo `backend/.env` con las siguientes variables:
DATABASE_URL=postgresql://postgres:postgres@db:5432/conexion_familiar
SECRET_KEY=tu_clave_secreta_generada
ACCESS_TOKEN_EXPIRE_MINUTES=60

---

## Autor Bersahí Rivera Ramírez

Desarrollado como prueba técnica para Vantum Development Team.