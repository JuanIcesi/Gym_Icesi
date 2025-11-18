# 🧪 Guía de Pruebas Completa - Gym Icesi

Esta guía te ayudará a probar todas las funcionalidades del sistema según los requerimientos.

---

## 📋 Pre-requisitos

1. ✅ Servidor Django corriendo: `http://127.0.0.1:8000/`
2. ✅ Base de datos Neon conectada
3. ✅ MongoDB Atlas conectado (opcional, no crítico)
4. ✅ Usuarios de prueba cargados en la BD

---

## 🔐 FASE 1: Autenticación y Roles

### 1.1 Página de Inicio (Selección de Login)
- [ ] **URL**: `http://127.0.0.1:8000/`
- [ ] Verificar que se muestren 3 tarjetas: Usuario Estándar, Entrenador, Administrador
- [ ] Cada tarjeta debe tener un botón/link que lleve a `/login/`

### 1.2 Login de Usuario Estándar
- [ ] **Usuario**: `laura.h` | **Contraseña**: `lh123`
- [ ] Verificar que después del login se redirija al dashboard de usuario
- [ ] Verificar que el menú muestre: Inicio, Mis Rutinas, Ejercicios, Progreso, Informes
- [ ] Verificar que NO aparezcan opciones de entrenador o admin

### 1.3 Login de Entrenador
- [ ] **Usuario**: `paula.r` | **Contraseña**: `pr123`
- [ ] Verificar que después del login se redirija al dashboard de entrenador
- [ ] Verificar que el menú muestre: Inicio, Mis Usuarios, Mis Rutinas Prediseñadas, Mis Ejercicios
- [ ] Verificar que NO aparezcan opciones de usuario estándar o admin

### 1.4 Login de Administrador
- [ ] **Usuario**: `admin` | **Contraseña**: `admin123`
- [ ] Verificar que después del login se redirija al panel de administración
- [ ] Verificar que el menú muestre: Inicio, Asignaciones, Informes Globales
- [ ] Verificar que NO aparezcan opciones de usuario estándar o entrenador

### 1.5 Validación de Errores
- [ ] Intentar login con usuario incorrecto → Debe mostrar mensaje de error claro
- [ ] Intentar login con contraseña incorrecta → Debe mostrar mensaje de error claro
- [ ] Verificar que el enlace "Problemas con tu cuenta?" esté visible

---

## 👤 FASE 2: Usuario Estándar

### 2.1 Dashboard de Usuario (`/home/`)
- [ ] Verificar que se muestre el nombre del usuario
- [ ] Verificar que se muestre programa/dependencia (si está en BD institucional)
- [ ] Verificar tarjetas de resumen:
  - [ ] Rutinas activas (número)
  - [ ] Sesiones este mes (número)
  - [ ] Tiempo total entrenado este mes
  - [ ] Entrenador asignado (si tiene uno)
- [ ] Verificar sección "Últimas actividades" con lista de progresos recientes
- [ ] Verificar botones de acción rápida:
  - [ ] "Crear nueva rutina"
  - [ ] "Registrar progreso"
  - [ ] "Ver informes"

### 2.2 Módulo de Ejercicios (`/ejercicios/`)
- [ ] Verificar que se muestre lista/grid de ejercicios
- [ ] Verificar que cada ejercicio muestre: nombre, tipo, dificultad
- [ ] Probar filtros:
  - [ ] Buscar por nombre
  - [ ] Filtrar por tipo (cardio, fuerza, movilidad)
  - [ ] Filtrar por dificultad
- [ ] Hacer clic en un ejercicio → Debe ir a `/ejercicios/<id>/`
- [ ] En el detalle del ejercicio:
  - [ ] Ver descripción completa
  - [ ] Ver paso a paso (si existe)
  - [ ] Ver video (si existe)
  - [ ] Ver botón "Agregar a una de mis rutinas"
  - [ ] Probar el modal para agregar a rutina

### 2.3 Módulo de Rutinas (`/rutinas/`)
- [ ] Verificar lista de rutinas del usuario
- [ ] Cada rutina debe mostrar: nombre, tipo, estado, última vez entrenada
- [ ] Verificar botones:
  - [ ] "Crear rutina nueva"
  - [ ] "Ver rutinas prediseñadas"
- [ ] Hacer clic en una rutina → Debe ir a `/rutinas/<id>/`
- [ ] En el detalle de rutina:
  - [ ] Ver nombre y descripción
  - [ ] Ver lista de ejercicios en orden
  - [ ] Ver series, repeticiones, tiempo de cada ejercicio
  - [ ] Ver botones: "Editar rutina", "Añadir ejercicio", "Registrar progreso"

### 2.4 Crear Rutina Nueva (`/rutinas/nueva/`)
- [ ] Verificar formulario con campos:
  - [ ] Nombre de la rutina
  - [ ] Objetivo
  - [ ] Días de la semana sugeridos (checkboxes)
  - [ ] Notas generales
- [ ] Guardar rutina → Debe redirigir a agregar ejercicios
- [ ] Agregar ejercicios a la rutina:
  - [ ] Seleccionar ejercicio del catálogo
  - [ ] Definir series/reps/tiempo
  - [ ] Añadir a la lista
- [ ] Guardar rutina completa

### 2.5 Rutinas Prediseñadas (`/rutinas/templates/` o desde lista)
- [ ] Verificar lista de rutinas creadas por entrenadores
- [ ] Cada rutina debe mostrar: nombre, objetivo, duración, nivel, creador
- [ ] Probar botón "Adoptar rutina"
- [ ] Verificar que al adoptar se cree una copia editable asociada al usuario

### 2.6 Módulo de Progreso (`/progreso/`)
- [ ] Verificar historial de progreso con filtros:
  - [ ] Filtrar por mes
  - [ ] Filtrar por año
  - [ ] Filtrar por rutina
- [ ] Verificar estadísticas del mes actual:
  - [ ] Sesiones este mes
  - [ ] Horas entrenadas
- [ ] Hacer clic en "Nueva Sesión" → Debe ir a `/progreso/nuevo/`
- [ ] En el formulario de progreso:
  - [ ] Seleccionar rutina
  - [ ] Ingresar fecha
  - [ ] Ingresar tiempo total
  - [ ] Ingresar nivel de esfuerzo (1-10)
  - [ ] Agregar notas opcionales
  - [ ] Guardar → Debe redirigir al historial

### 2.7 Informes de Usuario

#### 2.7.1 Informe de Progreso Mensual (`/reportes/progreso/`)
- [ ] Verificar selector de mes/año
- [ ] Verificar indicadores:
  - [ ] Número de sesiones
  - [ ] Tiempo total entrenado
  - [ ] Rutinas diferentes usadas
- [ ] Verificar gráficas:
  - [ ] Barras: sesiones por semana del mes
  - [ ] Pastel: distribución por tipo de ejercicio
- [ ] Verificar lista de "hitos" del mes

#### 2.7.2 Informe de Adherencia (`/reportes/adherencia/`)
- [ ] Verificar selector de mes/año
- [ ] Verificar indicadores:
  - [ ] Días activos
  - [ ] Porcentaje de adherencia
  - [ ] Racha actual (días consecutivos)
  - [ ] Porcentaje de cumplimiento
- [ ] Verificar comparación: días planificados vs días realmente entrenados
- [ ] Verificar distribución por tipo de ejercicio
- [ ] Verificar sugerencias basadas en actividad

---

## 🏋️ FASE 3: Entrenador

### 3.1 Dashboard de Entrenador (`/home/` como entrenador)
- [ ] Verificar tarjetas de resumen:
  - [ ] Usuarios asignados
  - [ ] Sesiones registradas por usuarios este mes
  - [ ] Rutinas prediseñadas creadas
  - [ ] Recomendaciones enviadas este mes
- [ ] Verificar sección "Usuarios que necesitan atención" (sin actividad en 7+ días)
- [ ] Verificar lista de últimos usuarios asignados con nivel de actividad
- [ ] Verificar botones de acción rápida:
  - [ ] "Ver mis usuarios"
  - [ ] "Crear rutina prediseñada"
  - [ ] "Crear ejercicio"

### 3.2 Lista de Usuarios Asignados (`/trainer/asignados/`)
- [ ] Verificar lista de usuarios asignados
- [ ] Cada usuario debe mostrar:
  - [ ] Nombre y programa
  - [ ] Última sesión registrada
  - [ ] Nivel de actividad (Alto/Medio/Bajo)
  - [ ] Rutinas activas
  - [ ] Sesiones este mes
- [ ] Probar filtros:
  - [ ] Buscar por nombre
  - [ ] Filtrar por nivel de actividad
- [ ] Hacer clic en un usuario → Debe ir a `/trainer/feedback/<user_id>/`

### 3.3 Detalle de Usuario para Entrenador (`/trainer/feedback/<user_id>/`)
- [ ] Verificar resumen del usuario:
  - [ ] Nombre y datos institucionales
  - [ ] Rutinas activas
  - [ ] Sesiones este mes
  - [ ] Fecha de asignación
- [ ] Verificar tendencia de actividad (últimos 3 meses)
- [ ] Verificar lista de progresos recientes:
  - [ ] Cada progreso debe mostrar: fecha, rutina, esfuerzo, notas
  - [ ] Botón "Enviar Recomendación" en cada progreso
- [ ] Verificar lista de rutinas del usuario:
  - [ ] Ver detalles de cada rutina
  - [ ] Botón "Recomendar" en cada rutina
- [ ] Verificar historial de recomendaciones enviadas
- [ ] Probar botón "Enviar Recomendación" general

### 3.4 Enviar Recomendación (`/trainer/recomendacion/<user_id>/`)
- [ ] Verificar formulario de recomendación
- [ ] Si viene desde una rutina → Debe mostrar la rutina asociada
- [ ] Si viene desde un progreso → Debe mostrar el progreso asociado
- [ ] Ingresar mensaje de recomendación
- [ ] Enviar → Debe guardar y redirigir al detalle del usuario

### 3.5 Gestión de Rutinas Prediseñadas (`/trainer/rutinas/`)
- [ ] Verificar lista de rutinas prediseñadas creadas por el entrenador
- [ ] Probar botón "Crear nueva rutina prediseñada"
- [ ] Crear rutina prediseñada:
  - [ ] Similar a crear rutina normal
  - [ ] Debe marcarse como `es_predisenada=True`
  - [ ] Debe estar disponible para que usuarios la adopten

### 3.6 Gestión de Ejercicios (`/trainer/ejercicios/`)
- [ ] Verificar lista de ejercicios creados por el entrenador
- [ ] Probar botón "Crear ejercicio nuevo"
- [ ] Crear ejercicio:
  - [ ] Nombre, tipo, descripción
  - [ ] Dificultad
  - [ ] Video (opcional)
  - [ ] Guardar → Debe estar disponible en el catálogo

---

## ⚙️ FASE 4: Administrador

### 4.1 Panel de Administración (`/home/` como admin)
- [ ] Verificar resumen global:
  - [ ] Total usuarios
  - [ ] Total entrenadores
  - [ ] Total rutinas
  - [ ] Total sesiones
  - [ ] Usuarios activos este mes
- [ ] Verificar tarjetas:
  - [ ] Usuarios con entrenador asignado
  - [ ] Usuarios sin entrenador
- [ ] Verificar estadísticas del mes actual:
  - [ ] Rutinas creadas
  - [ ] Sesiones registradas
  - [ ] Asignaciones nuevas
- [ ] Verificar listas:
  - [ ] Entrenadores con más carga
  - [ ] Usuarios más activos
  - [ ] Rutinas más usadas

### 4.2 Asignación de Entrenadores (`/admin/asignar-entrenador/`)
- [ ] Verificar formulario de asignación:
  - [ ] Selector de usuario (con búsqueda)
  - [ ] Selector de entrenador (con búsqueda)
- [ ] Verificar lista de usuarios con sus asignaciones actuales:
  - [ ] Usuario con entrenador → Mostrar entrenador y botón "Desactivar"
  - [ ] Usuario sin entrenador → Mostrar "Sin Entrenador"
- [ ] Probar asignar entrenador a usuario:
  - [ ] Seleccionar usuario sin entrenador
  - [ ] Seleccionar entrenador
  - [ ] Guardar → Debe crear asignación
- [ ] Probar desactivar asignación:
  - [ ] Hacer clic en "Desactivar" → Debe marcar como inactiva

### 4.3 Informes Globales (si están implementados)
- [ ] Verificar gráficas generales:
  - [ ] Usuarios activos por mes
  - [ ] Sesiones globales por mes
  - [ ] Ranking de entrenadores
- [ ] Probar filtros:
  - [ ] Por programa académico
  - [ ] Por campus

---

## 🔄 FASE 5: Flujos Integrados

### 5.1 Flujo Completo Usuario
1. [ ] Login como usuario estándar
2. [ ] Ver dashboard
3. [ ] Buscar ejercicios
4. [ ] Crear rutina nueva
5. [ ] Agregar ejercicios a la rutina
6. [ ] Registrar progreso usando esa rutina
7. [ ] Ver historial de progreso
8. [ ] Ver informe de progreso mensual
9. [ ] Ver informe de adherencia

### 5.2 Flujo Completo Entrenador
1. [ ] Login como entrenador
2. [ ] Ver dashboard
3. [ ] Ver usuarios asignados
4. [ ] Ver detalle de un usuario
5. [ ] Enviar recomendación a un usuario
6. [ ] Crear rutina prediseñada
7. [ ] Crear ejercicio nuevo

### 5.3 Flujo Completo Administrador
1. [ ] Login como administrador
2. [ ] Ver panel de administración
3. [ ] Asignar entrenador a usuario
4. [ ] Ver estadísticas globales
5. [ ] Ver entrenadores con más carga

### 5.4 Flujo Inter-Roles
1. [ ] Admin asigna entrenador a usuario
2. [ ] Usuario ve que tiene entrenador asignado
3. [ ] Entrenador ve al usuario en su lista
4. [ ] Entrenador envía recomendación al usuario
5. [ ] Usuario ve la recomendación en su dashboard
6. [ ] Entrenador crea rutina prediseñada
7. [ ] Usuario adopta la rutina prediseñada
8. [ ] Usuario registra progreso con la rutina adoptada
9. [ ] Entrenador ve el progreso del usuario

---

## ✅ Checklist Final

### Funcionalidades Críticas
- [ ] Login institucional funciona para los 3 roles
- [ ] Dashboards se muestran correctamente según rol
- [ ] Navegación muestra menús correctos según rol
- [ ] Usuario puede crear rutinas
- [ ] Usuario puede registrar progreso
- [ ] Entrenador puede ver usuarios asignados
- [ ] Entrenador puede enviar recomendaciones
- [ ] Admin puede asignar entrenadores
- [ ] Informes se generan correctamente

### Validaciones
- [ ] Usuario no puede acceder a páginas de entrenador
- [ ] Entrenador no puede acceder a páginas de admin
- [ ] Admin puede acceder a todo
- [ ] Mensajes de error son claros y amigables
- [ ] Datos institucionales se muestran correctamente

### Integración MongoDB (Opcional)
- [ ] Progresos detallados se guardan en MongoDB
- [ ] Actividades se registran en MongoDB
- [ ] Rutinas prediseñadas se guardan en MongoDB

---

## 🐛 Problemas Comunes y Soluciones

### Error: "Usuario o contraseña incorrectos"
- Verificar que el usuario exista en la BD Neon
- Verificar que la contraseña sea correcta (sin prefijo `hash_`)
- Ejecutar: `python manage.py test_login`

### Error: "No tienes permisos"
- Verificar que el usuario tenga el rol correcto en la BD
- Para entrenador: `employee_type = 'Instructor'`
- Para admin: `role = 'ADMIN'`

### Error: "No se puede conectar a la BD"
- Verificar variables de entorno en `.env`
- Ejecutar: `python manage.py verify_database_connection`

### Páginas en blanco o errores 500
- Revisar logs del servidor Django
- Verificar que todas las migraciones estén aplicadas
- Verificar que los templates existan

---

## 📝 Notas de Prueba

**Fecha de Prueba**: _______________

**Probado por**: _______________

**Resultados**:
- ✅ Funciona correctamente
- ⚠️ Funciona con problemas menores
- ❌ No funciona / Error crítico

**Observaciones**:
_________________________________________________
_________________________________________________
_________________________________________________

---

¡Buena suerte con las pruebas! 🚀

