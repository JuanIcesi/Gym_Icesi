# Gym Icesi - Sistema de Gestión de Entrenamiento

Sistema web para Bienestar Universitario que integra PostgreSQL (Neon), MongoDB (Atlas) y base de datos institucional para la gestión de rutinas de ejercicio, progreso de usuarios y asignación de entrenadores.

## 🎯 Características Principales

- **3 Roles de Usuario**: Usuario Estándar, Entrenador, Administrador
- **Autenticación Institucional**: Login con cuenta universitaria
- **Gestión de Rutinas**: Crear, adoptar y personalizar rutinas de ejercicio
- **Registro de Progreso**: Seguimiento detallado de entrenamientos
- **Asignación de Entrenadores**: Sistema de acompañamiento personalizado
- **Informes y Estadísticas**: Reportes de progreso, adherencia y tendencias
- **Integración Dual**: PostgreSQL para datos estructurados + MongoDB para datos flexibles

## 🚀 Instrucciones para ejecutar el proyecto

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- (Opcional) PostgreSQL si deseas usar una base de datos PostgreSQL en lugar de SQLite

### Pasos para ejecutar

1. **Navegar al directorio del proyecto:**
   ```bash
   cd gym_icesi
   ```

2. **Crear un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual:**
   - En Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - En Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - En Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Crear archivo .env (opcional pero recomendado):**
   Crea un archivo `.env` en el directorio `gym_icesi` con el siguiente contenido:
   ```
   SECRET_KEY=django-insecure-default-key-change-in-production
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=db.sqlite3
   MONGODB_ENABLED=True
   MONGODB_HOST=clustergym.pxczpdo.mongodb.net
   MONGODB_PORT=27017
   MONGODB_DB_NAME=sid_gym_icesi
   MONGODB_USERNAME=gym_user
   MONGODB_PASSWORD=EKKLsiwKQjNJkBdu
   MONGODB_AUTH_SOURCE=admin
   ```
   
   **Nota:** Si no creas el archivo `.env`, el proyecto usará valores por defecto (SQLite para la base de datos principal).

6. **Aplicar las migraciones de la base de datos:**
   ```bash
   python manage.py migrate
   ```

7. **Crear un superusuario (opcional, para acceder al panel de administración):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Ejecutar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

9. **Abrir en el navegador:**
   El proyecto estará disponible en: http://127.0.0.1:8000/

### Comandos útiles

- **Ver todas las rutas disponibles:**
  ```bash
  python manage.py show_urls
  ```

- **Acceder al panel de administración:**
  http://127.0.0.1:8000/admin/

- **Ejecutar tests:**
  ```bash
  python manage.py test
  ```

### Crear usuarios de prueba

Para crear usuarios de prueba en el sistema:

```bash
python manage.py create_test_users
```

Esto creará 3 usuarios de prueba:
- **Usuario Estándar**: `estudiante1` / `estudiante1`
- **Entrenador**: `entrenador1` / `entrenador1`
- **Administrador**: `admin1` / `admin1`

### Acceder a la aplicación

1. **Página de inicio**: http://127.0.0.1:8000/
   - Aquí puedes ver los 3 tipos de roles disponibles
   - Todos usan el mismo formulario de login

2. **Login**: http://127.0.0.1:8000/login/
   - Usa las credenciales de los usuarios de prueba
   - El sistema identifica automáticamente tu rol

3. **Dashboard**: http://127.0.0.1:8000/home/
   - Se muestra según tu rol (Usuario, Entrenador o Admin)

### Funcionalidades por Rol

#### 👤 Usuario Estándar
- Ver y crear rutinas personalizadas
- Adoptar rutinas prediseñadas
- Registrar progreso de entrenamiento
- Buscar y consultar ejercicios
- Ver informes de progreso y adherencia
- Recibir recomendaciones de entrenadores

#### 🏋️ Entrenador
- Crear rutinas prediseñadas
- Crear ejercicios para el sistema
- Ver usuarios asignados
- Revisar progreso de usuarios
- Dar recomendaciones y feedback

#### ⚙️ Administrador
- Ver lista de entrenadores
- Asignar entrenadores a usuarios
- Consultar estadísticas globales
- Ver usuarios activos
- Ver entrenadores con más carga

### Notas importantes

- El proyecto usa SQLite por defecto (archivo `db.sqlite3`), que es suficiente para desarrollo.
- Si necesitas usar PostgreSQL, configura las variables `DB_*` en el archivo `.env`.
- El proyecto también se conecta a MongoDB para algunos datos. Las credenciales están en el archivo `.env`.
- Si MongoDB no está disponible, el sistema funcionará normalmente pero sin guardar datos NoSQL.

## 📚 Documentación Adicional

- **Configuración de Bases de Datos**: Ver `CONFIGURACION_BD.md` para instrucciones completas paso a paso
- **Estado del Proyecto**: Ver `ESTADO_PROYECTO.md` para un análisis completo de la implementación
- **Justificación NoSQL**: Ver `JUSTIFICACION_NOSQL.md` para entender la arquitectura híbrida

## 🗄️ Configuración Rápida de Bases de Datos

### Para Neon (PostgreSQL):

**Opción Rápida (Recomendada):**
```bash
# 1. Configura las variables DB_* en .env con tus credenciales de Neon
# 2. Ejecuta el comando automático:
python manage.py setup_database
```

Este comando hace todo automáticamente:
- ✅ Verifica la conexión
- ✅ Aplica migraciones (crea esquema de la aplicación)
- ✅ Verifica tablas
- ✅ Crea datos de prueba

**Opción Manual:**
1. Crea un proyecto en [Neon](https://neon.tech)
2. Ejecuta en la consola SQL de Neon (en este orden):
   - `university_schema_postgresql.sql` (esquema institucional)
   - `university_full_data_postgresql.sql` (datos institucionales)
   - `create_app_user.sql` (opcional: usuario dedicado)
3. Configura las variables `DB_*` en `.env` con tus credenciales
4. Ejecuta: `python manage.py migrate` (crea esquema de la aplicación)
5. Ejecuta: `python manage.py setup_database` (crea datos de prueba)
6. Verifica: `python manage.py verify_database_connection`

**📖 Ver `CONFIGURACION_BD_RELACIONAL.md` para guía completa paso a paso.**
**📖 Ver `GUIA_NEON_PASO_A_PASO.md` para instrucciones específicas de Neon.**

### Para MongoDB Atlas:

1. Crea un proyecto en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea un cluster gratuito (M0)
3. Crea usuario y configura IP allowlist
4. Obtén la connection string
5. Configura `MONGODB_CONNECTION_STRING` en `.env`
6. Verifica: `python manage.py verify_mongodb_connection`

**📖 Ver `GUIA_NEON_PASO_A_PASO.md` para instrucciones paso a paso específicas de Neon.**