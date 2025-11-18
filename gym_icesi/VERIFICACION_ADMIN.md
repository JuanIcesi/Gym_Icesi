# Verificación de Funcionalidades del Administrador

## Usuario Administrador
- **Usuario**: `admin`
- **Contraseña**: `admin123` (formato: hash_admin123)
- **Role en BD**: `ADMIN`

## URLs a Verificar Manualmente

### 1. Dashboard de Administrador
- **URL**: `/` (después de login como admin)
- **Verificar**: 
  - ✅ Muestra estadísticas globales
  - ✅ Tarjetas con totales (usuarios, entrenadores, rutinas, sesiones)
  - ✅ Enlaces a todas las funcionalidades

### 2. Gestión de Usuarios
- **URL**: `/admin/usuarios/`
- **Verificar**:
  - ✅ Lista todos los usuarios
  - ✅ Filtros funcionan (rol, campus, actividad)
  - ✅ Búsqueda por nombre de usuario
  - ✅ Muestra estadísticas por usuario

### 3. Asignación Avanzada de Entrenadores
- **URL**: `/admin/asignaciones/avanzado/`
- **Verificar**:
  - ✅ Muestra lista de usuarios y entrenadores
  - ✅ Permite asignar entrenador a usuario
  - ✅ Muestra carga de trabajo por entrenador
  - ✅ Permite desactivar asignaciones
  - ✅ Registra cambios en historial

### 4. Historial de Asignaciones
- **URL**: `/admin/asignaciones/historial/`
- **Verificar**:
  - ✅ Muestra historial completo de cambios
  - ✅ Filtros funcionan (usuario, entrenador, acción)
  - ✅ Muestra quién hizo cada cambio

### 5. Moderación de Contenido
- **URL**: `/admin/moderacion/`
- **Verificar**:
  - ✅ Lista ejercicios pendientes
  - ✅ Lista rutinas pendientes
  - ✅ Muestra moderaciones recientes
  - ✅ Permite aprobar/rechazar contenido

### 6. Analytics y Reportes
- **URL**: `/admin/analytics/`
- **Verificar**:
  - ✅ Métricas generales del sistema
  - ✅ Actividad mensual (últimos 12 meses)
  - ✅ Actividad por facultad/departamento
  - ✅ Efectividad de entrenadores
  - ✅ Popularidad de ejercicios y rutinas

### 7. Configuración del Sistema
- **URL**: `/admin/config/`
- **Verificar**:
  - ✅ Permite crear nuevas configuraciones
  - ✅ Lista configuraciones existentes
  - ✅ Permite editar configuraciones
  - ✅ Permite eliminar configuraciones

## Pasos para Verificación Manual

1. **Iniciar sesión como administrador**:
   - Ir a `/login/?role=admin`
   - Usuario: `admin`
   - Contraseña: `admin123`

2. **Verificar Dashboard**:
   - Debe redirigir a `/` (admin_dashboard)
   - Verificar que todas las tarjetas muestren datos
   - Verificar que los enlaces funcionen

3. **Probar cada funcionalidad**:
   - Navegar a cada URL
   - Verificar que cargue sin errores
   - Probar acciones básicas (filtros, búsquedas, etc.)

4. **Verificar navegación**:
   - El menú superior debe mostrar todas las opciones del admin
   - Cada enlace debe funcionar correctamente

## Checklist de Funcionalidades

- [ ] Dashboard de administrador carga correctamente
- [ ] Gestión de usuarios funciona con filtros
- [ ] Asignación avanzada permite asignar/desasignar entrenadores
- [ ] Historial de asignaciones muestra cambios
- [ ] Moderación de contenido lista pendientes
- [ ] Analytics muestra métricas correctas
- [ ] Configuración del sistema permite crear/editar/eliminar
- [ ] Navegación funciona correctamente
- [ ] No hay errores en la consola del servidor
- [ ] Todas las vistas responden con código 200

## Notas

- Si algún usuario no tiene `role='ADMIN'` en la BD, no podrá acceder como administrador
- Para crear un admin, ejecutar en Neon: `UPDATE users SET role = 'ADMIN' WHERE username = 'admin';`
- El servidor debe estar corriendo en `http://127.0.0.1:8000`

