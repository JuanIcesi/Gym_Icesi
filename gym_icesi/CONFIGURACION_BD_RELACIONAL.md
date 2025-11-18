# 📊 Configuración de Base de Datos Relacional - Gym Icesi

Esta guía te ayudará a configurar completamente la base de datos relacional PostgreSQL para el proyecto Gym Icesi.

## 🎯 Objetivo

Configurar una base de datos PostgreSQL con:
- ✅ Esquema institucional (users, students, employees, etc.)
- ✅ Esquema de la aplicación (exercises, routines, progress_log, etc.)
- ✅ Tablas de estadísticas mensuales
- ✅ Usuario de conexión dedicado
- ✅ Datos de prueba para desarrollo

---

## 📋 Paso 1: Crear Base de Datos en Neon

### 1.1 Crear Proyecto en Neon

1. Ve a [https://neon.tech](https://neon.tech) y regístrate/inicia sesión
2. Crea un nuevo proyecto (ej: `gym-icesi`)
3. Neon creará automáticamente:
   - Un cluster de PostgreSQL
   - Una base de datos por defecto (ej: `neondb`)
   - Un usuario con contraseña

### 1.2 Obtener Credenciales

En el dashboard de Neon, encontrarás:
- **Host**: `ep-xxxxx.us-east-2.aws.neon.tech`
- **Database**: `neondb` (o el nombre que hayas elegido)
- **User**: Tu usuario de Neon
- **Password**: Tu contraseña de Neon
- **Port**: `5432`

**⚠️ IMPORTANTE**: Guarda estas credenciales, las necesitarás.

---

## 📋 Paso 2: Configurar Usuario de Conexión

### Opción A: Usar el Usuario Principal de Neon (Recomendado para desarrollo)

El usuario principal de Neon ya tiene todos los permisos necesarios. Puedes usarlo directamente.

### Opción B: Crear Usuario Dedicado (Recomendado para producción)

Si prefieres crear un usuario específico para la aplicación:

1. En Neon, ve a la **consola SQL**
2. Ejecuta:

```sql
-- Crear usuario para la aplicación
CREATE USER gym_app_user WITH PASSWORD 'tu_contraseña_segura';

-- Otorgar permisos en la base de datos
GRANT ALL PRIVILEGES ON DATABASE neondb TO gym_app_user;

-- Conectarse a la base de datos
\c neondb

-- Otorgar permisos en el esquema público
GRANT ALL PRIVILEGES ON SCHEMA public TO gym_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gym_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gym_app_user;

-- Para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gym_app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gym_app_user;
```

---

## 📋 Paso 3: Cargar Esquema Institucional

### 3.1 Cargar Esquema (CREATE TABLE)

1. En Neon, abre la **consola SQL** (SQL Editor)
2. Selecciona tu base de datos
3. Abre el archivo `university_schema_postgresql.sql`
4. **Copia TODO el contenido** y pégalo en la consola SQL
5. Ejecuta el script (botón "Run" o F5)
6. Verifica que no haya errores

Este script crea las tablas:
- `users` - Usuarios institucionales
- `students` - Estudiantes
- `employees` - Empleados
- `faculties` - Facultades
- `campuses` - Campus
- `cities`, `departments`, `countries` - Ubicaciones

### 3.2 Cargar Datos Institucionales (INSERT)

1. En la misma consola SQL de Neon
2. Abre el archivo `university_full_data_postgresql.sql`
3. **Copia TODO el contenido** y pégalo en la consola
4. Ejecuta el script
5. Verifica que se insertaron los datos

Este script inserta:
- Usuarios de prueba (estudiantes, empleados, administradores)
- Datos de facultades, campus, etc.

**Usuarios de prueba incluidos:**
- `laura.h` (STUDENT) - Contraseña: `lh123`
- `paula.r` (EMPLOYEE - Instructor) - Contraseña: `pr123`
- `maria.g` (EMPLOYEE - Administrativo) - Contraseña: `mg123`

---

## 📋 Paso 4: Configurar Variables de Entorno

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

# O si creaste un usuario dedicado:
# DB_USER=gym_app_user
# DB_PASSWORD=tu_contraseña_segura
```

**⚠️ IMPORTANTE**: Reemplaza los valores con tus credenciales reales.

---

## 📋 Paso 5: Crear Esquema de la Aplicación

El esquema de la aplicación se crea automáticamente mediante las migraciones de Django.

### 5.1 Aplicar Migraciones

1. Activa tu entorno virtual:
   ```bash
   cd gym_icesi
   .\venv\Scripts\Activate.ps1  # Windows
   # o
   source venv/bin/activate  # Linux/Mac
   ```

2. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```

Esto creará las siguientes tablas:

**Tablas Principales:**
- `fit_exercise` - Ejercicios disponibles
- `fit_routine` - Rutinas de ejercicio
- `fit_routineitem` - Ejercicios dentro de rutinas
- `fit_progresslog` - Registros de progreso de entrenamiento
- `fit_trainerassignment` - Asignaciones de entrenadores a usuarios
- `fit_trainerrecommendation` - Recomendaciones de entrenadores

**Tablas de Estadísticas:**
- `fit_usermonthlystats` - Estadísticas mensuales por usuario
  - `rutinas_iniciadas` - Cantidad de rutinas iniciadas en el mes
  - `seguimientos_registrados` - Cantidad de registros de progreso en el mes
  
- `fit_trainermonthlystats` - Estadísticas mensuales por entrenador
  - `asignaciones_nuevas` - Cantidad de asignaciones nuevas en el mes
  - `seguimientos_realizados` - Cantidad de recomendaciones/seguimientos realizados en el mes

**Tablas del Sistema:**
- `auth_user` - Usuarios de Django (sincronizados con users institucional)
- `django_migrations` - Control de migraciones
- Otras tablas del sistema Django

### 5.2 Verificar Tablas Creadas

```bash
python manage.py verify_database_connection
```

Este comando verificará:
- ✅ Conexión a PostgreSQL
- ✅ Tablas institucionales
- ✅ Tablas de la aplicación
- ✅ Usuarios de prueba

---

## 📋 Paso 6: Cargar Datos de Prueba

### Opción A: Usar el Comando Automático (Recomendado)

Ejecuta el comando que configura todo automáticamente:

```bash
python manage.py setup_database
```

Este comando:
1. ✅ Verifica la conexión
2. ✅ Aplica migraciones (si es necesario)
3. ✅ Verifica que todas las tablas existan
4. ✅ Crea datos de prueba:
   - Ejercicios de ejemplo
   - Rutinas para usuarios existentes
   - Registros de progreso
   - Asignaciones de entrenadores
   - Estadísticas mensuales (se actualizan automáticamente)

### Opción B: Crear Datos Manualmente

Si prefieres crear datos manualmente:

1. **Crear ejercicios:**
   ```bash
   python manage.py populate_exercises
   ```

2. **Crear rutinas y progreso:**
   - Inicia sesión en la aplicación
   - Crea rutinas desde la interfaz
   - Registra progreso

---

## 📋 Paso 7: Verificar Configuración Completa

### 7.1 Verificar Conexión y Tablas

```bash
python manage.py verify_database_connection
```

Deberías ver:
```
[OK] Conexion exitosa
[OK] Tablas institucionales: users, students, employees...
[OK] Tablas de aplicacion: fit_exercise, fit_routine...
[OK] Usuarios de prueba encontrados
```

### 7.2 Verificar Datos

```bash
python manage.py setup_database --skip-migrations
```

Esto mostrará un resumen de todos los registros en cada tabla.

---

## 📊 Estructura de la Base de Datos

### Esquema Institucional

```
users (username, password_hash, role, student_id, employee_id)
  ├── students (id, first_name, last_name, email, campus_code)
  └── employees (id, first_name, last_name, email, faculty_code, employee_type)
      ├── faculties (code, name)
      └── campuses (code, name)
```

### Esquema de la Aplicación

```
auth_user (sincronizado con users)
  ├── fit_exercise (nombre, tipo, descripcion, dificultad, video_url)
  ├── fit_routine (user, nombre, descripcion, es_predisenada)
  │   └── fit_routineitem (routine, exercise, orden, series, reps, tiempo_seg)
  ├── fit_progresslog (user, routine, fecha, repeticiones, tiempo_seg, esfuerzo)
  ├── fit_trainerassignment (user, trainer, fecha_asignacion, activo)
  ├── fit_trainerrecommendation (trainer, user, mensaje, fecha)
  ├── fit_usermonthlystats (user, anio, mes, rutinas_iniciadas, seguimientos_registrados)
  └── fit_trainermonthlystats (trainer, anio, mes, asignaciones_nuevas, seguimientos_realizados)
```

---

## 🔄 Actualización Automática de Estadísticas

Las estadísticas mensuales se actualizan automáticamente mediante señales Django:

- **Al crear una rutina** → Se actualiza `rutinas_iniciadas` del usuario
- **Al registrar progreso** → Se actualiza `seguimientos_registrados` del usuario
- **Al asignar entrenador** → Se actualiza `asignaciones_nuevas` del entrenador
- **Al crear recomendación** → Se actualiza `seguimientos_realizados` del entrenador

No necesitas actualizar las estadísticas manualmente.

---

## 🧪 Datos de Prueba

### Usuarios Institucionales

Los usuarios de prueba vienen en `university_full_data_postgresql.sql`:

| Usuario | Rol | Contraseña | Descripción |
|---------|-----|------------|-------------|
| `laura.h` | STUDENT | `lh123` | Estudiante |
| `paula.r` | EMPLOYEE | `pr123` | Instructor (Entrenador) |
| `maria.g` | EMPLOYEE | `mg123` | Administrativo |

### Datos de la Aplicación

El comando `setup_database` crea:
- 5 ejercicios de ejemplo
- Rutinas para cada usuario
- 3-5 registros de progreso por usuario
- Asignaciones de entrenadores

---

## 🛠️ Comandos Útiles

### Verificar Estado de la BD
```bash
python manage.py verify_database_connection
```

### Configurar Todo Automáticamente
```bash
python manage.py setup_database
```

### Solo Aplicar Migraciones
```bash
python manage.py migrate
```

### Crear Ejercicios
```bash
python manage.py populate_exercises
```

### Acceder a la Consola SQL
En Neon: Dashboard → SQL Editor

---

## ⚠️ Solución de Problemas

### Error: "relation does not exist"
**Solución**: Ejecuta `python manage.py migrate`

### Error: "permission denied"
**Solución**: Verifica que el usuario tenga permisos en la BD

### Error: "connection refused"
**Solución**: 
- Verifica las credenciales en `.env`
- Verifica que la IP esté en el allowlist de Neon
- Verifica que `sslmode=require` esté configurado

### Las estadísticas no se actualizan
**Solución**: Las señales Django se activan automáticamente. Si no funcionan, verifica que `fit/apps.py` esté configurado correctamente.

---

## ✅ Checklist de Configuración

- [ ] Proyecto creado en Neon
- [ ] Credenciales guardadas
- [ ] Esquema institucional cargado (`university_schema_postgresql.sql`)
- [ ] Datos institucionales cargados (`university_full_data_postgresql.sql`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Datos de prueba creados (`python manage.py setup_database`)
- [ ] Verificación exitosa (`python manage.py verify_database_connection`)

---

## 📝 Notas Importantes

1. **Esquema Separado**: El esquema institucional y el de la aplicación coexisten en la misma base de datos pero son independientes.

2. **Usuario de Conexión**: Puedes usar el usuario principal de Neon o crear uno dedicado. Ambos funcionan.

3. **Estadísticas Automáticas**: Las estadísticas se actualizan automáticamente. No necesitas hacer nada manual.

4. **Datos de Prueba**: Los datos de prueba se pueden recrear en cualquier momento ejecutando `setup_database`.

5. **Producción**: Para producción, considera crear un usuario dedicado con permisos específicos.

---

*Última actualización: $(date)*
*Para más detalles sobre Neon, ver `GUIA_NEON_PASO_A_PASO.md`*

