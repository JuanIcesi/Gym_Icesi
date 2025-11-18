# 🚀 Guía Paso a Paso: Configurar Neon PostgreSQL

Esta guía te llevará paso a paso para configurar Neon y cargar los datos institucionales usando **SOLO** los 2 archivos SQL que ya tienes.

---

## 📋 Archivos que usarás

1. `university_schema_postgresql.sql` - Esquema (CREATE TABLE)
2. `university_full_data_postgresql.sql` - Datos (INSERT)

---

## 🎯 PASO 1: Crear Proyecto en Neon

1. Ve a [https://neon.tech](https://neon.tech)
2. Haz clic en **"Sign Up"** o **"Log In"** si ya tienes cuenta
3. Una vez dentro, haz clic en **"New Project"**
4. Completa:
   - **Project name**: `gym-icesi` (o el nombre que prefieras)
   - **Region**: Elige la más cercana (ej: `US East`)
   - **PostgreSQL version**: Deja la versión por defecto (15 o superior)
5. Haz clic en **"Create Project"**

**⏱️ Tiempo estimado**: 2-3 minutos

---

## 🎯 PASO 2: Obtener Credenciales de Conexión

Una vez creado el proyecto, Neon te mostrará un modal que dice **"Connect to your database"**. Este es el modal que necesitas.

### 2.1: Abrir el Modal de Conexión

Si el modal no está visible:
1. En el dashboard, haz clic en **"Connect"** (botón en la parte superior derecha)
2. O ve a **"SQL Editor"** en el menú lateral y haz clic en **"Connect"**

### 2.2: Extraer las Credenciales del Connection String

En el modal verás un **connection string** que se ve así:

```
postgresql://neondb_owner:npg_jlAtm408KGys@ep-green-waterfall-aeqry6p5-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Desglosa este string para obtener cada parte**:

El formato es: `postgresql://USUARIO:CONTRASEÑA@HOST/DATABASE?opciones`

Del ejemplo anterior:
- **Usuario**: `neondb_owner`
- **Contraseña**: `npg_jlAtm408KGys` (después de los dos puntos `:`)
- **Host**: `ep-green-waterfall-aeqry6p5-pooler.c-2.us-east-2.aws.neon.tech` (después de `@`)
- **Database**: `neondb` (después de la última `/` y antes del `?`)
- **Port**: `5432` (por defecto, no aparece en el string)

### 2.3: Obtener la Contraseña Completa

**⚠️ IMPORTANTE**: La contraseña en el connection string puede estar truncada o oculta.

1. En el modal, busca el campo **"Role"** (debe mostrar algo como `neondb_owner`)
2. A la derecha del campo Role, verás un enlace **"Reset password"**
3. Si necesitas ver la contraseña completa, haz clic en **"Reset password"** para generar una nueva
4. O usa el botón **"Show password"** / **"Hide password"** si está disponible

### 2.4: Anotar las Credenciales

Anota estos datos en un archivo temporal o directamente en tu `.env`:

```
DB_HOST=ep-green-waterfall-aeqry6p5-pooler.c-2.us-east-2.aws.neon.tech
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_jlAtm408KGys
DB_PORT=5432
```

**💡 TIPS**:
- Si el connection string tiene `-pooler` en el host, puedes usarlo así o quitar `-pooler` para conexión directa
- **GUARDA ESTAS CREDENCIALES** - las necesitarás en el PASO 10
- Puedes hacer clic en **"Copy snippet"** para copiar el connection string completo

**⏱️ Tiempo estimado**: 2-3 minutos

---

## 🎯 PASO 3: Configurar Acceso por IP

### 3.1: Verificar Configuración de Networking

1. En la página de **"Project settings"**, en el menú derecho, haz clic en **"Networking"**
2. Verás la sección de **"Networking"** con dos opciones:
   - **"Allow traffic via the public internet"**: Debe estar en **ON** (verde) ✅
   - **"Allow traffic via Virtual Private Network (VPC)"**: Puede estar en OFF (gris)

### 3.2: ¿Qué Significa Esto?

**✅ BUENAS NOTICIAS**: 
- Si **"Allow traffic via the public internet"** está en **ON** (verde), significa que tu base de datos **YA ESTÁ CONFIGURADA** para aceptar conexiones desde cualquier IP
- **NO necesitas hacer nada más** en este paso
- El plan gratuito de Neon permite tráfico público por defecto

**⚠️ NOTA SOBRE IP ALLOWLIST**:
- En el plan **gratuito** de Neon, la opción de **"IP Allowlist"** (limitar IPs específicas) **NO está disponible**
- El mensaje que ves dice: *"Upgrade your plan to limit database access to trusted IP addresses"*
- Esto significa que necesitarías un plan de pago para restringir IPs
- **Para desarrollo, esto está bien** - tu base de datos aceptará conexiones desde tu computadora

### 3.3: Verificar que Todo Está Listo

Asegúrate de que:
- ✅ **"Allow traffic via the public internet"** está en **ON** (verde)
- ✅ No hay errores o advertencias en rojo

**Si todo está en verde, puedes continuar al PASO 4** 🎉

**⏱️ Tiempo estimado**: 1 minuto

---

## 🎯 PASO 4: Abrir la Consola SQL de Neon

1. En el dashboard de Neon, busca el botón **"SQL Editor"** o **"Query"**
2. Haz clic para abrir la consola SQL
3. Verás un editor de texto donde puedes escribir SQL

**⏱️ Tiempo estimado**: 30 segundos

---

## 🎯 PASO 5: Cargar el Esquema (CREATE TABLE)

1. En tu computadora, abre el archivo `university_schema_postgresql.sql`
2. **Selecciona TODO el contenido** (Ctrl+A / Cmd+A)
3. **Copia** el contenido (Ctrl+C / Cmd+C)
4. Vuelve a la consola SQL de Neon
5. **Pega** el contenido en el editor (Ctrl+V / Cmd+V)
6. Verifica que todo el código SQL esté pegado correctamente
7. Haz clic en el botón **"Run"** o presiona **F5**

**✅ Qué debe pasar**:
- Verás mensajes de éxito como "CREATE TABLE" o "ALTER TABLE"
- No debe haber errores en rojo
- Si hay algún error, léelo y verifica que copiaste todo el contenido

**⏱️ Tiempo estimado**: 2-3 minutos

---

## 🎯 PASO 6: Verificar que las Tablas se Crearon

1. En la misma consola SQL de Neon, escribe:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   ```
2. Haz clic en **"Run"**
3. Debes ver una lista de tablas que incluye:
   - `users`
   - `students`
   - `employees`
   - `faculties`
   - `campuses`
   - `cities`
   - `departments`
   - `countries`
   - Y otras más...

**✅ Si ves las tablas**: ¡Perfecto! Continúa al siguiente paso.

**❌ Si NO ves las tablas**: Vuelve al PASO 5 y verifica que ejecutaste el script completo.

**⏱️ Tiempo estimado**: 1 minuto

---

## 🎯 PASO 7: Cargar los Datos (INSERT)

1. En tu computadora, abre el archivo `university_full_data_postgresql.sql`
2. **Selecciona TODO el contenido** (Ctrl+A / Cmd+A)
3. **Copia** el contenido (Ctrl+C / Cmd+C)
4. Vuelve a la consola SQL de Neon
5. **Limpia el editor** (o abre una nueva pestaña/consulta)
6. **Pega** el contenido completo (Ctrl+V / Cmd+V)
7. Verifica que todo el código SQL esté pegado
8. Haz clic en **"Run"** o presiona **F5**

**✅ Qué debe pasar**:
- Verás mensajes como "INSERT 0 1" o "INSERT 0 5" (esto indica cuántos registros se insertaron)
- No debe haber errores en rojo
- El proceso puede tardar unos segundos

**⏱️ Tiempo estimado**: 2-3 minutos

---

## 🎯 PASO 8: Verificar que los Datos se Cargaron

1. En la consola SQL de Neon, ejecuta estas consultas para verificar:

   **Verificar usuarios**:
   ```sql
   SELECT username, role, student_id, employee_id 
   FROM users 
   ORDER BY username;
   ```
   Debes ver varios usuarios como: `laura.h`, `pedro.m`, `juan.p`, `paula.r`, etc.

   **Verificar estudiantes**:
   ```sql
   SELECT id, first_name, last_name, email 
   FROM students;
   ```
   Debes ver 5 estudiantes.

   **Verificar empleados (especialmente instructores)**:
   ```sql
   SELECT id, first_name, last_name, email, employee_type 
   FROM employees 
   WHERE UPPER(employee_type) = 'INSTRUCTOR';
   ```
   Debes ver al menos 2 instructores (paula.r y andres.c).

**✅ Si ves los datos**: ¡Excelente! Los datos están cargados correctamente.

**❌ Si NO ves los datos**: Vuelve al PASO 7 y verifica que ejecutaste el script completo.

**⏱️ Tiempo estimado**: 2 minutos

---

## 🎯 PASO 9: Identificar Usuarios de Prueba

De los usuarios que se cargaron, estos son los que puedes usar para probar:

### 👤 Usuario Estándar (Estudiante):
- **Usuario**: `laura.h`
- **Contraseña**: `lh123` (el password_hash es `hash_lh123`)
- **Rol**: STUDENT
- **ID Estudiante**: 2001

También puedes usar: `pedro.m` / `pm123`, `ana.s` / `as123`, etc.

### 🏋️ Entrenador (Instructor):
- **Usuario**: `paula.r`
- **Contraseña**: `pr123` (el password_hash es `hash_pr123`)
- **Rol**: EMPLOYEE
- **ID Empleado**: 1007 (tipo: Instructor)

También puedes usar: `andres.c` / `ac123`

### ⚙️ Administrador:
Puedes usar cualquier empleado administrativo, por ejemplo:
- **Usuario**: `maria.g`
- **Contraseña**: `mg123` (el password_hash es `hash_mg123`)
- **Rol**: EMPLOYEE
- **ID Empleado**: 1002 (tipo: Administrativo)

**💡 Nota**: El sistema identifica el rol ADMIN si el `role` en la tabla `users` es `'ADMIN'`. Si quieres que un usuario sea admin, puedes actualizarlo:

```sql
UPDATE users 
SET role = 'ADMIN' 
WHERE username = 'maria.g';
```

**⏱️ Tiempo estimado**: 2 minutos

---

## 🎯 PASO 10: Configurar Variables de Entorno

1. En el directorio `gym_icesi`, crea o edita el archivo `.env`
2. Agrega las siguientes líneas (reemplaza con tus credenciales reales de Neon):

```env
# Configuración de Neon PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=neondb
DB_USER=tu_usuario_neon
DB_PASSWORD=tu_contraseña_neon
DB_HOST=ep-xxxxx.us-east-2.aws.neon.tech
DB_PORT=5432

# Configuración de Django
SECRET_KEY=django-insecure-default-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Configuración de MongoDB (si ya lo tienes configurado)
MONGODB_ENABLED=True
MONGODB_CONNECTION_STRING=mongodb+srv://...
```

**⚠️ IMPORTANTE**: 
- Reemplaza `tu_usuario_neon` con tu usuario real
- Reemplaza `tu_contraseña_neon` con tu contraseña real
- Reemplaza `ep-xxxxx.us-east-2.aws.neon.tech` con tu host real

**⏱️ Tiempo estimado**: 2 minutos

---

## 🎯 PASO 11: Aplicar Migraciones de Django

### 11.1: Verificar Contraseña de Neon (IMPORTANTE)

Antes de ejecutar las migraciones, **verifica que la contraseña en tu `.env` sea correcta**:

1. Ve al modal de conexión de Neon (PASO 2)
2. Si la contraseña está oculta o truncada:
   - Haz clic en **"Reset password"** junto al campo "Role"
   - Copia la nueva contraseña completa
   - Actualiza `DB_PASSWORD` en tu archivo `.env`
3. O usa el botón **"Show password"** / **"Hide password"** para ver la contraseña actual

### 11.2: Activar Entorno Virtual

1. Abre una terminal en el directorio `gym_icesi`
2. Activa tu entorno virtual:
   ```bash
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # o
   venv\Scripts\activate.bat     # Windows CMD
   # o
   source venv/bin/activate      # Linux/Mac
   ```

### 11.3: Verificar Conexión Primero

Antes de aplicar migraciones, verifica que la conexión funcione:

```bash
python manage.py verify_database_connection
```

**✅ Si la conexión es exitosa**: Continúa con el siguiente paso.

**❌ Si hay error de autenticación**: 
- Verifica la contraseña en el `.env`
- Asegúrate de que no tenga espacios extra
- Considera resetear la contraseña en Neon

### 11.4: Aplicar Migraciones

Una vez que la conexión funcione, ejecuta:

```bash
python manage.py migrate
```

**✅ Qué debe pasar**:
- Verás mensajes como "Applying fit.0001_initial... OK"
- Se crearán las tablas de la aplicación en Neon:
  - `fit_exercise`
  - `fit_routine`
  - `fit_routineitem`
  - `fit_progresslog`
  - `fit_trainerassignment`
  - `fit_trainerrecommendation`
  - `fit_usermonthlystats`
  - `fit_trainermonthlystats`
  - Y las tablas internas de Django
- No debe haber errores

**⏱️ Tiempo estimado**: 2-3 minutos

---

## 🎯 PASO 12: Verificar que Todo Funciona

1. Ejecuta el comando de verificación:
   ```bash
   python manage.py verify_database_connection
   ```

**✅ Qué debe mostrar**:
- `[OK] Motor: PostgreSQL`
- `[OK] Conexion exitosa`
- `[OK] users: X registros`
- `[OK] students: 5 registros`
- `[OK] employees: X registros`
- `[OK] fit_exercise: 0 registros` (o más si ya creaste ejercicios)
- Y los usuarios de prueba que identificaste

**⏱️ Tiempo estimado**: 1 minuto

---

## 🎯 PASO 13: Probar el Login

1. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```

2. Abre tu navegador en: http://127.0.0.1:8000/

3. Haz clic en cualquier rol y luego en "Iniciar Sesión"

4. Prueba con los usuarios que identificaste:
   - **Estudiante**: `laura.h` / `lh123`
   - **Entrenador**: `paula.r` / `pr123`
   - **Admin**: `maria.g` / `mg123` (después de actualizar el rol a ADMIN)

**✅ Si el login funciona**: ¡Perfecto! Todo está configurado correctamente.

**❌ Si hay errores**: 
- Verifica las credenciales en `.env`
- Verifica que la IP allowlist esté configurada
- Ejecuta `python manage.py verify_database_connection` para ver qué falta

**⏱️ Tiempo estimado**: 2 minutos

---

## ✅ Checklist Final

Antes de considerar que todo está listo:

- [ ] Proyecto creado en Neon
- [ ] Credenciales de conexión anotadas
- [ ] IP allowlist configurada
- [ ] Esquema ejecutado (`university_schema_postgresql.sql`)
- [ ] Tablas verificadas (SELECT en information_schema.tables)
- [ ] Datos ejecutados (`university_full_data_postgresql.sql`)
- [ ] Datos verificados (SELECT en users, students, employees)
- [ ] Usuarios de prueba identificados
- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Migraciones de Django aplicadas (`python manage.py migrate`)
- [ ] Verificación exitosa (`python manage.py verify_database_connection`)
- [ ] Login funciona con usuarios de prueba

---

## 🆘 Solución de Problemas Comunes

### Error: "Connection refused" o "Connection timeout"
- **Causa**: IP no está en la allowlist
- **Solución**: Ve al PASO 3 y agrega tu IP o `0.0.0.0/0`

### Error: "Authentication failed"
- **Causa**: Usuario o contraseña incorrectos en `.env`
- **Solución**: Verifica las credenciales en el PASO 2 y actualiza `.env`

### Error: "Table does not exist"
- **Causa**: No ejecutaste el esquema completo
- **Solución**: Vuelve al PASO 5 y ejecuta `university_schema_postgresql.sql` completo

### Error: "No data" o "0 registros"
- **Causa**: No ejecutaste los INSERTs
- **Solución**: Vuelve al PASO 7 y ejecuta `university_full_data_postgresql.sql` completo

### Error: "Password incorrect" en login
- **Causa**: El formato de password_hash es `hash_<password>`
- **Solución**: Si el password_hash es `hash_lh123`, la contraseña es `lh123` (sin el `hash_`)

---

## 🎉 ¡Listo!

Una vez completados todos los pasos, tu base de datos Neon estará completamente configurada con:
- ✅ Esquema institucional cargado
- ✅ Datos de ejemplo cargados
- ✅ Usuarios de prueba disponibles
- ✅ Tablas de la aplicación creadas
- ✅ Login funcionando

**Tiempo total estimado**: 15-20 minutos

