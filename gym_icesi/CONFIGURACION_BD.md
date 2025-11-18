# 📊 Guía Completa de Configuración de Bases de Datos

Esta guía te ayudará a configurar las bases de datos para el proyecto Gym Icesi paso a paso.

## 🎯 Resumen de Bases de Datos

El proyecto utiliza **3 bases de datos**:

1. **PostgreSQL (Neon)**: Base de datos relacional
   - Esquema institucional (users, students, employees, etc.)
   - Esquema de la aplicación (exercises, routines, progress_log, etc.)

2. **MongoDB (Atlas)**: Base de datos NoSQL
   - Progreso detallado
   - Metadata de ejercicios
   - Logs de actividad
   - Plantillas de rutinas

3. **SQLite (Local - Desarrollo)**: Opcional para desarrollo sin Neon

---

## 📋 PARTE 1: Configurar Neon (PostgreSQL)

### Paso 1.1: Crear Proyecto en Neon

1. Ve a [https://neon.tech](https://neon.tech) y regístrate
2. Crea un nuevo proyecto (ej: `gym-icesi`)
3. Neon creará automáticamente:
   - Un cluster de PostgreSQL
   - Una base de datos por defecto
   - Un usuario con contraseña

### Paso 1.2: Obtener Credenciales de Conexión

En el dashboard de Neon, encontrarás:

- **Host**: Algo como `ep-xxxxx.us-east-2.aws.neon.tech`
- **Database**: Nombre de la base de datos (por defecto `neondb`)
- **User**: Tu usuario
- **Password**: Tu contraseña
- **Port**: `5432`
- **Connection String**: Una cadena completa tipo `postgresql://user:password@host/dbname`

**⚠️ IMPORTANTE**: Anota estas credenciales, las necesitarás para el archivo `.env`

### Paso 1.3: Configurar Acceso (IP Allowlist)

1. En Neon, ve a **Settings** → **IP Allowlist**
2. Para desarrollo, tienes dos opciones:
   - **Opción 1 (Más fácil)**: Permitir `0.0.0.0/0` (cualquier IP) - ⚠️ Menos seguro
   - **Opción 2 (Más seguro)**: Agregar tu IP pública específica
3. Cuando despliegues en producción, agrega la IP de tu servidor (Render, Railway, etc.)

### Paso 1.4: Cargar Esquema Institucional

1. En Neon, abre la **consola SQL** (SQL Editor)
2. Selecciona tu base de datos
3. Abre el archivo `university_schema_postgresql.sql` en tu editor
4. **Copia TODO el contenido** y pégalo en la consola SQL de Neon
5. Ejecuta el script (botón "Run" o F5)
6. Verifica que no haya errores

### Paso 1.5: Cargar Datos Institucionales

1. En la misma consola SQL de Neon
2. Abre el archivo `university_full_data_postgresql.sql`
3. **Copia TODO el contenido** y pégalo en la consola
4. Ejecuta el script
5. Verifica que se insertaron los datos

### Paso 1.6: Verificar Usuarios de Prueba

Los usuarios de prueba ya vienen incluidos en `university_full_data_postgresql.sql`.

Para verificar que se cargaron correctamente:

1. En la consola SQL de Neon, ejecuta:
   ```sql
   SELECT username, role, student_id, employee_id FROM USERS ORDER BY username;
   ```

2. Debes ver usuarios como:
   - `laura.h` (STUDENT) - Contraseña: `lh123`
   - `paula.r` (EMPLOYEE - Instructor) - Contraseña: `pr123`
   - `maria.g` (EMPLOYEE - Administrativo) - Contraseña: `mg123`

**Nota**: El formato de contraseña es: si el `password_hash` es `hash_lh123`, la contraseña real es `lh123`

### Paso 1.7: Configurar Variables de Entorno

1. En el directorio `gym_icesi`, crea o edita el archivo `.env`
2. Agrega las siguientes variables:

```env
# Configuración de Neon PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=neondb
DB_USER=tu_usuario_neon
DB_PASSWORD=tu_contraseña_neon
DB_HOST=ep-xxxxx.us-east-2.aws.neon.tech
DB_PORT=5432
```

**⚠️ IMPORTANTE**: Reemplaza los valores con tus credenciales reales de Neon.

### Paso 1.8: Aplicar Migraciones de Django

1. Activa tu entorno virtual:
   ```bash
   cd gym_icesi
   .\venv\Scripts\Activate.ps1  # Windows
   # o
   source venv/bin/activate  # Linux/Mac
   ```

2. Aplica las migraciones para crear las tablas de la aplicación:
   ```bash
   python manage.py migrate
   ```

3. Esto creará las tablas:
   - `fit_exercise`
   - `fit_routine`
   - `fit_routineitem`
   - `fit_progresslog`
   - `fit_trainerassignment`
   - `fit_trainerrecommendation`
   - `fit_usermonthlystats`
   - `fit_trainermonthlystats`
   - Y las tablas internas de Django

### Paso 1.9: Verificar Conexión

Ejecuta el comando de verificación:

```bash
python manage.py verify_database_connection
```

Este comando verificará:
- ✅ Conexión a Neon
- ✅ Tablas institucionales existentes
- ✅ Tablas de la aplicación creadas
- ✅ Usuarios de prueba disponibles

---

## 📋 PARTE 2: Configurar MongoDB Atlas

### Paso 2.1: Crear Proyecto en MongoDB Atlas

1. Ve a [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Regístrate o inicia sesión
3. Crea un nuevo proyecto (ej: `GymIcesi`)

### Paso 2.2: Crear Cluster

1. En el proyecto, haz clic en **"Build a Database"**
2. Selecciona el plan **FREE (M0)**
3. Elige una región cercana (ej: `us-east-1`)
4. Nombra tu cluster (ej: `Cluster0`)
5. Haz clic en **"Create"**

### Paso 2.3: Crear Usuario de Base de Datos

1. Ve a **Database Access** → **Add New Database User**
2. Configura:
   - **Authentication Method**: Password
   - **Username**: `gymuser` (o el que prefieras)
   - **Password**: Genera una contraseña segura y **guárdala**
   - **Database User Privileges**: Read and write to any database
3. Haz clic en **"Add User"**

### Paso 2.4: Configurar Acceso por IP

1. Ve a **Network Access** → **Add IP Address**
2. Para desarrollo:
   - **Opción 1**: Agrega `0.0.0.0/0` (cualquier IP) - ⚠️ Menos seguro
   - **Opción 2**: Agrega tu IP pública específica
3. Haz clic en **"Confirm"**

### Paso 2.5: Obtener Connection String

1. Ve a **Database** → Haz clic en **"Connect"**
2. Selecciona **"Connect your application"**
3. Copia la connection string que aparece, será algo como:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Reemplaza `<username>` y `<password>` con tus credenciales reales
5. Agrega el nombre de la base de datos al final:
   ```
   mongodb+srv://gymuser:TU_PASSWORD@cluster0.xxxxx.mongodb.net/gym_icesi?retryWrites=true&w=majority
   ```

### Paso 2.6: Configurar Variables de Entorno

En tu archivo `.env`, agrega:

```env
# Configuración de MongoDB Atlas
MONGODB_ENABLED=True
MONGODB_CONNECTION_STRING=mongodb+srv://gymuser:TU_PASSWORD@cluster0.xxxxx.mongodb.net/gym_icesi?retryWrites=true&w=majority

# O configuración manual (alternativa)
MONGODB_HOST=cluster0.xxxxx.mongodb.net
MONGODB_PORT=27017
MONGODB_DB_NAME=gym_icesi
MONGODB_USERNAME=gymuser
MONGODB_PASSWORD=TU_PASSWORD
MONGODB_AUTH_SOURCE=admin
```

**⚠️ IMPORTANTE**: Reemplaza `TU_PASSWORD` con tu contraseña real.

### Paso 2.7: Verificar Conexión a MongoDB

Ejecuta:

```bash
python manage.py verify_mongodb_connection
```

O prueba manualmente:

```bash
python manage.py insert_mongodb_data
```

---

## 📋 PARTE 3: Verificación Completa

### Verificar Todo Está Funcionando

1. **Verificar Neon**:
   ```bash
   python manage.py verify_database_connection
   ```

2. **Verificar MongoDB**:
   ```bash
   python manage.py verify_mongodb_connection
   ```

3. **Crear usuarios de prueba en Django** (si es necesario):
   ```bash
   python manage.py create_test_users
   ```

4. **Iniciar el servidor**:
   ```bash
   python manage.py runserver
   ```

5. **Probar login**:
   - Ve a http://127.0.0.1:8000/
   - Haz clic en cualquier rol
   - Intenta iniciar sesión con:
     - Usuario: `estudiante1` / Contraseña: `estudiante1`
     - Usuario: `entrenador1` / Contraseña: `entrenador1`
     - Usuario: `admin1` / Contraseña: `admin1`

---

## 🔍 Solución de Problemas

### Error: "Connection refused" (Neon)

- Verifica que la IP allowlist incluya tu IP
- Verifica que las credenciales en `.env` sean correctas
- Verifica que el host no tenga espacios extra

### Error: "Authentication failed" (MongoDB)

- Verifica que el usuario y contraseña sean correctos
- Verifica que la IP esté en la allowlist
- Verifica que el connection string esté bien formado

### Error: "Table does not exist" (Neon)

- Verifica que ejecutaste `university_schema_postgresql.sql`
- Verifica que ejecutaste `python manage.py migrate`
- Verifica que estás usando la base de datos correcta

### Error: "No module named 'psycopg2'"

- Instala psycopg2: `pip install psycopg2-binary`

---

## 📝 Checklist Final

Antes de considerar que todo está listo:

- [ ] Proyecto creado en Neon
- [ ] Esquema institucional cargado en Neon
- [ ] Datos institucionales cargados en Neon
- [ ] Usuarios de prueba creados en Neon
- [ ] Variables de entorno configuradas para Neon
- [ ] Migraciones de Django aplicadas
- [ ] Cluster creado en MongoDB Atlas
- [ ] Usuario de MongoDB creado
- [ ] IP allowlist configurada en MongoDB
- [ ] Variables de entorno configuradas para MongoDB
- [ ] Conexión a Neon verificada
- [ ] Conexión a MongoDB verificada
- [ ] Login funciona con usuarios de prueba
- [ ] Dashboard se muestra correctamente según el rol

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu aplicación estará completamente configurada y lista para usar con datos reales en Neon y MongoDB.

