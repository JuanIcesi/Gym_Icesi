# ✅ Checklist de Verificación - Funcionalidades Entrenador

## 📋 Guía de Verificación Manual

Este documento proporciona un checklist completo para verificar manualmente todas las funcionalidades del entrenador.

---

## 🔐 1. AUTENTICACIÓN Y LOGIN

### URLs a Verificar:
- [ ] `/` - Página de selección de login (debe mostrar 3 opciones)
- [ ] `/login/?role=trainer` - Página de login para entrenador
- [ ] `/logout/` - Cerrar sesión

### Pruebas:
1. **Selección de Login**:
   - Ir a `http://127.0.0.1:8000/`
   - Verificar que aparecen 3 tarjetas
   - Hacer clic en "Entrenador"
   - Verificar que redirige a `/login/?role=trainer`

2. **Login Exitoso**:
   - Usuario: `sandra.m` (o cualquier entrenador de BD institucional)
   - Contraseña: `sm123`
   - Verificar que redirige al dashboard del entrenador
   - Verificar que el menú muestra opciones de entrenador

3. **Login Fallido**:
   - Intentar con credenciales incorrectas
   - Verificar que muestra mensaje de error
   - Verificar que NO redirige

---

## 🏠 2. DASHBOARD DEL ENTRENADOR

### URL: `/home/` o `/`

### Elementos a Verificar:
- [ ] Nombre del entrenador se muestra correctamente
- [ ] Tarjeta "Usuarios Asignados" con número correcto
- [ ] Tarjeta "Sesiones Este Mes" (de usuarios asignados)
- [ ] Tarjeta "Recomendaciones Enviadas" este mes
- [ ] Lista "Usuarios que necesitan atención":
  - [ ] Usuarios sin progreso reciente
  - [ ] Usuarios con bajo rendimiento
  - [ ] Usuarios inactivos
- [ ] Botones de acción rápida:
  - [ ] "Ver mis usuarios"
  - [ ] "Crear rutina prediseñada"
  - [ ] "Ver mis ejercicios"
  - [ ] "Crear ejercicio nuevo"

---

## 👥 3. GESTIÓN DE USUARIOS ASIGNADOS

### URLs a Verificar:
- [ ] `/trainer/asignados/` - Lista de usuarios asignados
- [ ] `/trainer/feedback/<user_id>/` - Detalle de usuario asignado

### Pruebas de Lista de Usuarios Asignados:
1. **Cargar Lista**:
   - Ir a `/trainer/asignados/`
   - Verificar que muestra todos los usuarios asignados
   - Verificar que muestra: nombre, programa, última sesión, nivel de actividad

2. **Filtros**:
   - [ ] Filtro por programa académico
   - [ ] Filtro por nivel de actividad
   - [ ] Búsqueda por nombre
   - Verificar que los filtros funcionan correctamente

3. **Acciones**:
   - [ ] Clic en un usuario → Va a detalle del usuario
   - [ ] Botón "Enviar recomendación" (si está disponible en la lista)

### Pruebas de Detalle de Usuario:
1. **Información Básica**:
   - Ir a `/trainer/feedback/<user_id>/`
   - Verificar que muestra:
     - [ ] Nombre del usuario
     - [ ] Programa académico/departamento
     - [ ] Información institucional

2. **Resumen de Actividad**:
   - [ ] Rutinas activas del usuario
   - [ ] Sesiones este mes
   - [ ] Tendencia de actividad (mini gráfico)
   - [ ] Nivel de actividad (Alto/Medio/Bajo)

3. **Rutinas del Usuario**:
   - [ ] Lista de rutinas del usuario
   - [ ] Ver detalle de cada rutina
   - [ ] Sugerir cambios a rutinas

4. **Progresos Recientes**:
   - [ ] Lista de progresos recientes
   - [ ] Clic para ver detalles de una sesión
   - [ ] Información detallada de cada progreso

5. **Recomendaciones Enviadas**:
   - [ ] Lista de recomendaciones enviadas a este usuario
   - [ ] Ver detalle de cada recomendación

6. **Acción Clave - Enviar Recomendación**:
   - [ ] Botón "Enviar recomendación"
   - [ ] Formulario con:
     - [ ] Asunto/título
     - [ ] Mensaje
     - [ ] Opción de asociar a rutina específica
     - [ ] Opción de asociar a sesión específica
   - [ ] Enviar y verificar que se crea la recomendación
   - [ ] Verificar que se actualizan estadísticas mensuales

---

## 📊 4. SEGUIMIENTO DE PROGRESO

### URL: `/trainer/analisis/<user_id>/`

### Pruebas:
1. **Análisis Detallado**:
   - Ir a `/trainer/analisis/<user_id>/`
   - Verificar que muestra:
     - [ ] Historial completo de rutinas realizadas
     - [ ] Métricas de desempeño por ejercicio
     - [ ] Gráficos comparativos de progreso
     - [ ] Identificación de tendencias
     - [ ] Identificación de estancamientos

2. **Métricas por Ejercicio**:
   - [ ] Repeticiones promedio
   - [ ] Peso utilizado
   - [ ] Tiempo empleado
   - [ ] Esfuerzo percibido
   - [ ] Evolución temporal

3. **Gráficos Comparativos**:
   - [ ] Comparación mes a mes
   - [ ] Comparación entre ejercicios
   - [ ] Tendencias de mejora/estancamiento

4. **Alertas**:
   - [ ] Alertas de bajo rendimiento
   - [ ] Alertas de inactividad
   - [ ] Alertas de estancamiento

---

## 💬 5. SISTEMA DE RECOMENDACIONES

### URLs a Verificar:
- [ ] `/trainer/recomendacion/<user_id>/` - Crear recomendación simple
- [ ] `/trainer/recomendacion-avanzada/<user_id>/` - Crear recomendación avanzada

### Pruebas de Recomendación Simple:
1. **Formulario Básico**:
   - Ir a `/trainer/recomendacion/<user_id>/`
   - Verificar que el formulario tiene:
     - [ ] Campo "Título/Asunto"
     - [ ] Campo "Mensaje"
     - [ ] Campo "Tipo" (general, rutina, progreso)
     - [ ] Selector de rutina asociada (opcional)
     - [ ] Selector de sesión asociada (opcional)
   - Llenar y enviar
   - Verificar que se crea la recomendación
   - Verificar que se actualizan estadísticas mensuales

### Pruebas de Recomendación Avanzada:
1. **Formulario Avanzado**:
   - Ir a `/trainer/recomendacion-avanzada/<user_id>/`
   - Verificar que el formulario tiene campos adicionales:
     - [ ] Comentarios específicos por ejercicio
     - [ ] Ajustes sugeridos a rutinas
     - [ ] Modificación de intensidad/dificultad
     - [ ] Recomendaciones de nuevos ejercicios
   - Llenar y enviar
   - Verificar que se crea la recomendación avanzada

2. **Asociación con Contenido**:
   - [ ] Asociar recomendación a rutina específica
   - [ ] Asociar recomendación a sesión específica
   - [ ] Verificar que la asociación funciona correctamente

3. **Notificaciones**:
   - [ ] Verificar que el usuario recibe notificación
   - [ ] Verificar que aparece en el dashboard del usuario

---

## 🏋️ 6. CREACIÓN DE CONTENIDO

### URLs a Verificar:
- [ ] `/trainer/rutinas/` - Lista de rutinas prediseñadas
- [ ] `/trainer/rutinas/nueva/` - Crear rutina prediseñada
- [ ] `/trainer/ejercicios/` - Lista de ejercicios del entrenador
- [ ] `/trainer/ejercicios/nuevo/` - Crear ejercicio

### Pruebas de Rutinas Prediseñadas:
1. **Lista de Rutinas**:
   - Ir a `/trainer/rutinas/`
   - Verificar que muestra todas las rutinas prediseñadas creadas por el entrenador
   - Verificar que muestra: nombre, objetivo, nivel, fecha de creación

2. **Crear Rutina Prediseñada**:
   - Ir a `/trainer/rutinas/nueva/`
   - Verificar que el formulario tiene:
     - [ ] Campo "Nombre" (requerido)
     - [ ] Campo "Descripción"
     - [ ] Campo "Objetivo" (pérdida de peso, ganancia muscular, etc.)
     - [ ] Campo "Nivel de dificultad" (principiante, intermedio, avanzado)
     - [ ] Campo "Duración" (semanas)
     - [ ] Selector de ejercicios del sistema
     - [ ] Configuración de series, repeticiones, tiempo por ejercicio
   - Llenar y guardar
   - Verificar que se crea la rutina
   - Verificar que está marcada como `es_predisenada=True`
   - Verificar que `autor_trainer` es el entrenador actual

3. **Agregar Ejercicios a Rutina**:
   - Después de crear rutina, agregar ejercicios
   - Verificar que se pueden agregar ejercicios del catálogo
   - Verificar que se puede configurar orden, series, repeticiones, tiempo

### Pruebas de Ejercicios:
1. **Lista de Ejercicios**:
   - Ir a `/trainer/ejercicios/`
   - Verificar que muestra todos los ejercicios creados por el entrenador
   - Verificar que muestra: nombre, tipo, dificultad, fecha de creación

2. **Crear Ejercicio**:
   - Ir a `/trainer/ejercicios/nuevo/`
   - Verificar que el formulario tiene:
     - [ ] Campo "Nombre" (requerido)
     - [ ] Campo "Tipo" (cardio, fuerza, movilidad)
     - [ ] Campo "Descripción completa"
     - [ ] Campo "Duración estimada" (minutos)
     - [ ] Campo "Nivel de dificultad" (1-5)
     - [ ] Campo "URL de video demostrativo"
     - [ ] Campo "Instrucciones paso a paso"
     - [ ] Campo "Músculos involucrados"
     - [ ] Campo "Equipamiento necesario"
     - [ ] Campo "Precauciones"
     - [ ] Campo "Contraindicaciones"
     - [ ] Campo "Variaciones" (principiante, intermedio, avanzado)
   - Llenar y guardar
   - Verificar que se crea el ejercicio
   - Verificar que `creado_por` es el entrenador actual

3. **Editar Ejercicio**:
   - Editar un ejercicio existente
   - Verificar que se actualiza correctamente
   - Verificar que los cambios se reflejan en el catálogo

4. **Validación de Contenido**:
   - Intentar crear ejercicio sin nombre
   - Verificar que muestra error de validación
   - Verificar que otros campos requeridos se validan

---

## 📈 7. ESTADÍSTICAS Y MÉTRICAS

### Pruebas:
1. **Estadísticas Mensuales**:
   - Verificar que se actualizan automáticamente cuando:
     - [ ] Se crea una nueva asignación
     - [ ] Se envía una recomendación
   - Verificar que se muestran en el dashboard

2. **Métricas de Efectividad**:
   - [ ] Seguimiento de progreso de alumnos
   - [ ] Número de recomendaciones enviadas
   - [ ] Número de usuarios asignados
   - [ ] Tasa de respuesta de usuarios

---

## 🔔 8. ALERTAS Y NOTIFICACIONES

### Pruebas:
1. **Alertas de Bajo Rendimiento**:
   - [ ] Usuarios con bajo rendimiento en ejercicios
   - [ ] Usuarios con estancamiento en progreso
   - [ ] Verificar que aparecen en dashboard

2. **Alertas de Inactividad**:
   - [ ] Usuarios sin progreso reciente (X días)
   - [ ] Usuarios que no han completado rutinas
   - [ ] Verificar que aparecen en "Usuarios que necesitan atención"

3. **Notificaciones Push**:
   - [ ] Verificar que las recomendaciones generan notificaciones
   - [ ] Verificar que los usuarios reciben notificaciones

---

## 💬 9. MENSAJERÍA

### URLs a Verificar:
- [ ] `/mensajes/` - Lista de mensajes
- [ ] `/mensajes/nuevo/` - Crear mensaje
- [ ] `/mensajes/<id>/` - Detalle de mensaje

### Pruebas:
1. **Lista de Mensajes**:
   - Ir a `/mensajes/`
   - Verificar que muestra mensajes recibidos y enviados
   - Verificar que muestra estado (leído/no leído)

2. **Crear Mensaje**:
   - Ir a `/mensajes/nuevo/`
   - Verificar que muestra selector de destinatario (solo usuarios asignados)
   - Llenar asunto y mensaje
   - Enviar
   - Verificar que se crea el mensaje

3. **Detalle de Mensaje**:
   - Hacer clic en un mensaje
   - Verificar que muestra contenido completo
   - Verificar que marca como leído

---

## 🔍 10. VALIDACIONES Y SEGURIDAD

### Pruebas de Seguridad:
- [ ] No puede acceder a usuarios no asignados
- [ ] No puede modificar rutinas de otros entrenadores
- [ ] No puede acceder a páginas de administrador sin ser admin
- [ ] Solo puede ver ejercicios que creó o ejercicios del sistema

### Pruebas de Validación:
- [ ] Formularios validan campos requeridos
- [ ] Mensajes de error se muestran correctamente
- [ ] Validaciones de datos (fechas, números, etc.)
- [ ] Validación de contenido (ejercicios, rutinas)

---

## 📝 11. NAVEGACIÓN Y MENÚ

### Elementos del Menú a Verificar:
- [ ] "Inicio" - Redirige a dashboard del entrenador
- [ ] "Mis Usuarios" - Redirige a lista de usuarios asignados
- [ ] "Mis Rutinas" - Redirige a rutinas prediseñadas
- [ ] "Mis Ejercicios" - Redirige a ejercicios del entrenador
- [ ] "Mensajes" - Redirige a mensajería
- [ ] "Salir" - Cierra sesión

---

## ✅ RESUMEN DE VERIFICACIÓN

### Funcionalidades Principales:
- [x] Autenticación y login
- [x] Dashboard del entrenador
- [x] Gestión de usuarios asignados (lista, detalle)
- [x] Seguimiento de progreso (análisis detallado)
- [x] Sistema de recomendaciones (simple y avanzada)
- [x] Creación de contenido (rutinas prediseñadas, ejercicios)
- [x] Administración de ejercicios (catálogo, edición, validación)
- [x] Estadísticas y métricas
- [x] Alertas y notificaciones
- [x] Mensajería
- [x] Navegación y menús

---

## 🚀 CÓMO USAR ESTE CHECKLIST

1. **Inicia sesión** como entrenador (`sandra.m` / `sm123` o cualquier entrenador de BD institucional)
2. **Navega** por cada sección del checklist
3. **Marca** cada elemento verificado
4. **Anota** cualquier error o problema encontrado
5. **Verifica** que todas las funcionalidades funcionan al 100%

---

## 📌 NOTAS IMPORTANTES

- El servidor debe estar corriendo en `http://127.0.0.1:8000`
- Usa un navegador con herramientas de desarrollador para ver errores en consola
- Verifica que no hay errores 500 en el servidor
- Verifica que los templates no tienen errores de sintaxis
- Verifica que las estadísticas se actualizan automáticamente
- Verifica que las recomendaciones se envían correctamente a los usuarios

---

## 🔑 USUARIOS DE PRUEBA

### Entrenadores (de BD institucional):
- `sandra.m` / `sm123` - Entrenador
- `paula.r` / `pr123` - Entrenador
- `andres.c` / `ac123` - Entrenador

### Usuarios Estándar (para asignar):
- `laura.h` / `lh123` - Estudiante
- `carlos.m` / `cm123` - Estudiante

---

**Última actualización**: Después de crear herramientas de verificación para entrenadores

