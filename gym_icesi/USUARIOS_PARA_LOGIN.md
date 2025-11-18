# 👥 Usuarios para Login - Gym Icesi

## 📋 Resumen de Usuarios Disponibles

### 🎓 Usuarios Estándar (Estudiantes)
Estos usuarios pueden:
- Ver su panel personal
- Buscar y consultar ejercicios
- Crear rutinas personalizadas
- Adoptar rutinas prediseñadas
- Registrar progreso
- Ver informes personales

| Usuario | Contraseña | Nombre | ID Estudiante |
|---------|------------|--------|---------------|
| `laura.h` | `lh123` | Laura Hernández | 2001 |
| `pedro.m` | `pm123` | Pedro Martínez | 2002 |
| `ana.s` | `as123` | Ana Sánchez | 2003 |
| `luis.r` | `lr123` | Luis Ramírez | 2004 |
| `sofia.g` | `sg123` | Sofía González | 2005 |

---

### 🏋️ Entrenadores (Instructores)
Estos usuarios pueden:
- Crear rutinas prediseñadas
- Crear ejercicios
- Ver usuarios asignados
- Revisar progreso de usuarios
- Hacer comentarios/recomendaciones

| Usuario | Contraseña | Nombre | ID Empleado | Tipo |
|---------|------------|--------|-------------|------|
| `paula.r` | `pr123` | Paula Rodríguez | 1007 | Instructor |
| `andres.c` | `ac123` | Andrés Castro | 1008 | Instructor |

**⚠️ IMPORTANTE**: Solo los empleados con `employee_type = 'Instructor'` pueden acceder como entrenadores.

---

### ⚙️ Administradores
Estos usuarios pueden:
- Ver lista de entrenadores
- Asignar entrenadores a usuarios
- Consultar estadísticas globales
- Gestionar el sistema

| Usuario | Contraseña | Nombre | ID Empleado | Tipo |
|---------|------------|--------|-------------|------|
| `admin` | `admin123` | Admin | 1001 | Docente (ADMIN) |

**⚠️ NOTA**: Para que un usuario sea administrador, debe tener `role = 'ADMIN'` en la tabla `users`.

Si quieres convertir a `maria.g` en administrador, ejecuta en la consola SQL de Neon:

```sql
UPDATE users 
SET role = 'ADMIN' 
WHERE username = 'maria.g';
```

---

### 👨‍💼 Empleados NO-Instructores (Usuarios Estándar)
Estos empleados NO son entrenadores, acceden como usuarios estándar:

| Usuario | Contraseña | Nombre | Tipo Empleado |
|---------|------------|--------|---------------|
| `maria.g` | `mg123` | María González | Administrativo |
| `juan.p` | `jp123` | Juan Pérez | Docente |
| `carlos.l` | `cl123` | Carlos López | Docente |
| `carlos.m` | `cm123` | Carlos Martínez | Docente |
| `sandra.o` | `so123` | Sandra Ortiz | Docente |

---

## 🔐 Cómo Iniciar Sesión

1. Ve a: http://127.0.0.1:8000/
2. Haz clic en cualquier tarjeta de rol o ve a: http://127.0.0.1:8000/login/
3. Ingresa:
   - **Usuario**: (ej: `laura.h`)
   - **Contraseña**: (ej: `lh123`)
4. El sistema te redirigirá automáticamente al dashboard correspondiente según tu rol.

---

## ✅ Verificación de Roles

Después de iniciar sesión, el sistema te mostrará:
- **Usuario Estándar**: Dashboard personal con rutinas y progreso
- **Entrenador**: Dashboard con usuarios asignados y rutinas prediseñadas
- **Administrador**: Dashboard con estadísticas globales y gestión

---

## 🐛 Si el Login No Funciona

1. **Verifica que el servidor esté corriendo**:
   ```bash
   python manage.py runserver
   ```

2. **Verifica la conexión a Neon**:
   ```bash
   python manage.py verify_database_connection
   ```

3. **Prueba la autenticación directamente**:
   ```bash
   python manage.py test_login
   ```

4. **Verifica que el usuario exista en la BD**:
   - Ve a la consola SQL de Neon
   - Ejecuta: `SELECT username, role, is_active FROM users WHERE username = 'laura.h';`

5. **Limpia la sesión del navegador**:
   - Cierra sesión si estás logueado
   - Limpia las cookies del sitio
   - Intenta iniciar sesión nuevamente

