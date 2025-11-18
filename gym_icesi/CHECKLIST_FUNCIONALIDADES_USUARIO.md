# ✅ Checklist de Verificación - Funcionalidades Usuario Estándar

## 📋 Guía de Verificación Manual

Este documento proporciona un checklist completo para verificar manualmente todas las funcionalidades del usuario estándar.

---

## 🔐 1. AUTENTICACIÓN Y LOGIN

### URLs a Verificar:
- [ ] `/` - Página de selección de login (debe mostrar 3 opciones: Usuario Estándar, Entrenador, Administrador)
- [ ] `/login/?role=user` - Página de login para usuario estándar
- [ ] `/logout/` - Cerrar sesión

### Pruebas:
1. **Selección de Login**:
   - Ir a `http://127.0.0.1:8000/`
   - Verificar que aparecen 3 tarjetas (Usuario Estándar, Entrenador, Administrador)
   - Hacer clic en "Usuario Estándar"
   - Verificar que redirige a `/login/?role=user`

2. **Login Exitoso**:
   - Usuario: `laura.h`
   - Contraseña: `lh123`
   - Verificar que redirige al dashboard (`/home/`)
   - Verificar que el menú muestra opciones de usuario estándar

3. **Login Fallido**:
   - Intentar con credenciales incorrectas
   - Verificar que muestra mensaje de error
   - Verificar que NO redirige

---

## 🏠 2. DASHBOARD DEL USUARIO

### URL: `/home/` o `/`

### Elementos a Verificar:
- [ ] Nombre del usuario se muestra correctamente
- [ ] Programa/dependencia (si está disponible en BD institucional)
- [ ] Tarjeta "Rutinas Activas" con número correcto
- [ ] Tarjeta "Sesiones Este Mes" con número correcto
- [ ] Tarjeta "Tiempo Total Entrenado" (si aplica)
- [ ] Tarjeta "Entrenador Asignado" (si tiene entrenador)
- [ ] Sección "Últimas Actividades" con lista de progresos recientes
- [ ] Botones de acción rápida:
  - [ ] "Crear nueva rutina"
  - [ ] "Registrar progreso"
  - [ ] "Ver informes"

---

## 📋 3. GESTIÓN DE RUTINAS

### URLs a Verificar:
- [ ] `/rutinas/` - Lista de rutinas del usuario
- [ ] `/rutinas/nueva/` - Crear nueva rutina
- [ ] `/rutinas/<id>/` - Detalle de rutina
- [ ] `/rutinas/<id>/agregar-item/` - Agregar ejercicio a rutina
- [ ] `/rutinas/<id>/adoptar/` - Adoptar rutina prediseñada (si aplica)

### Pruebas de Lista de Rutinas:
1. **Cargar Lista**:
   - Ir a `/rutinas/`
   - Verificar que muestra todas las rutinas del usuario
   - Verificar que muestra: nombre, tipo, estado, última vez entrenada

2. **Botones**:
   - [ ] "Crear rutina nueva" funciona
   - [ ] "Ver rutinas prediseñadas" funciona (si hay rutinas prediseñadas)

### Pruebas de Crear Rutina:
1. **Formulario Completo**:
   - Ir a `/rutinas/nueva/`
   - Verificar que el formulario tiene:
     - [ ] Campo "Nombre" (requerido)
     - [ ] Campo "Descripción"
     - [ ] Campo "Objetivo"
     - [ ] Campo "Frecuencia" (diaria/semanal)
     - [ ] Campo "Días de la semana" (checkboxes)
     - [ ] Campo "Meta personal"
   - Llenar el formulario y guardar
   - Verificar que redirige y crea la rutina

2. **Validaciones**:
   - Intentar crear rutina sin nombre
   - Verificar que muestra error de validación

### Pruebas de Detalle de Rutina:
1. **Información Básica**:
   - Ir a `/rutinas/<id>/` (usar ID de rutina existente)
   - Verificar que muestra:
     - [ ] Nombre de la rutina
     - [ ] Descripción
     - [ ] Lista de ejercicios en orden
     - [ ] Series, repeticiones, tiempo para cada ejercicio

2. **Acciones Disponibles**:
   - [ ] Botón "Editar rutina" (si es suya y está activa)
   - [ ] Botón "Añadir ejercicio"
   - [ ] Botón "Duplicar rutina"
   - [ ] Botón "Registrar progreso usando esta rutina"

### Pruebas de Agregar Ejercicio:
1. **Agregar Ejercicio a Rutina**:
   - Ir a `/rutinas/<id>/agregar-item/`
   - Verificar que muestra selector de ejercicios
   - Seleccionar un ejercicio
   - Llenar: orden, series, repeticiones, tiempo, notas
   - Guardar
   - Verificar que el ejercicio aparece en la rutina

### Pruebas de Adoptar Rutina:
1. **Adoptar Rutina Prediseñada**:
   - Ir a `/rutinas/` y hacer clic en "Ver rutinas prediseñadas"
   - Verificar que muestra lista de rutinas creadas por entrenadores
   - Hacer clic en "Adoptar rutina" en una rutina
   - Verificar que se crea una copia para el usuario
   - Verificar que la copia es editable

---

## 💪 4. GESTIÓN DE EJERCICIOS

### URLs a Verificar:
- [ ] `/ejercicios/` - Lista de ejercicios
- [ ] `/ejercicios/<id>/` - Detalle de ejercicio
- [ ] `/ejercicios/nuevo/` - Crear ejercicio personalizado

### Pruebas de Lista de Ejercicios:
1. **Vista de Lista**:
   - Ir a `/ejercicios/`
   - Verificar que muestra ejercicios en grid o tabla
   - Verificar que muestra: nombre, tipo, dificultad, origen

2. **Filtros**:
   - [ ] Filtro por nombre (búsqueda)
   - [ ] Filtro por tipo (cardio, fuerza, movilidad)
   - [ ] Filtro por dificultad (1-5)
   - Verificar que los filtros funcionan correctamente

### Pruebas de Detalle de Ejercicio:
1. **Información Completa**:
   - Hacer clic en un ejercicio
   - Verificar que muestra:
     - [ ] Nombre
     - [ ] Tipo
     - [ ] Descripción completa
     - [ ] Dificultad
     - [ ] Duración aproximada
     - [ ] Video (si hay)
     - [ ] Instrucciones paso a paso (si hay)
     - [ ] Músculos involucrados (si hay)
     - [ ] Equipamiento necesario (si hay)
     - [ ] Precauciones (si hay)
     - [ ] Contraindicaciones (si hay)
     - [ ] Variaciones (si hay)

2. **Acciones**:
   - [ ] Botón "Agregar a una de mis rutinas" (si hay rutinas)
   - Verificar que abre modal para seleccionar rutina

### Pruebas de Crear Ejercicio Personalizado:
1. **Formulario Completo**:
   - Ir a `/ejercicios/nuevo/`
   - Verificar que el formulario tiene todos los campos
   - Llenar y guardar
   - Verificar que se crea el ejercicio
   - Verificar que aparece en la lista

---

## ✅ 5. REGISTRO DE PROGRESO

### URLs a Verificar:
- [ ] `/progreso/nuevo/` - Crear registro de progreso
- [ ] `/progreso/` - Lista de progreso

### Pruebas de Crear Progreso:
1. **Formulario Completo**:
   - Ir a `/progreso/nuevo/`
   - Verificar que el formulario tiene:
     - [ ] Selector de rutina
     - [ ] Campo fecha (por defecto hoy)
     - [ ] Campo tiempo total (minutos o segundos)
     - [ ] Campo nivel de esfuerzo (1-10)
     - [ ] Campo repeticiones
     - [ ] Campo peso usado (si aplica)
     - [ ] Campo notas
   - Llenar y guardar
   - Verificar que redirige y crea el registro

2. **Desde Rutina**:
   - Ir a detalle de rutina
   - Hacer clic en "Registrar progreso usando esta rutina"
   - Verificar que la rutina ya está seleccionada

### Pruebas de Lista de Progreso:
1. **Vista de Lista**:
   - Ir a `/progreso/`
   - Verificar que muestra todos los registros
   - Verificar que muestra: fecha, rutina, tiempo, esfuerzo

2. **Filtros**:
   - [ ] Filtro por mes
   - [ ] Filtro por año
   - [ ] Filtro por rutina
   - Verificar que los filtros funcionan

3. **Conversión de Tiempo**:
   - Verificar que los segundos se convierten correctamente a minutos
   - Verificar que NO hay errores de template (como el `div` que corregimos)

4. **Estadísticas del Mes**:
   - Verificar que muestra:
     - [ ] Total de sesiones del mes
     - [ ] Total de horas entrenadas del mes

---

## 📊 6. INFORMES

### URLs a Verificar:
- [ ] `/reportes/progreso/` - Informe de progreso mensual
- [ ] `/reportes/adherencia/` - Informe de adherencia
- [ ] `/reportes/carga/` - Informe de balance de carga
- [ ] `/reportes/tendencias/` - Informe de tendencias
- [ ] `/reportes/logros/` - Informe de logros

### Pruebas de Informe de Progreso:
1. **Elementos del Informe**:
   - Ir a `/reportes/progreso/`
   - Verificar que muestra:
     - [ ] Selector de mes/año
     - [ ] Número de sesiones
     - [ ] Tiempo total entrenado
     - [ ] Rutinas diferentes usadas
     - [ ] Gráficas (si hay)
     - [ ] Lista de hitos

### Pruebas de Informe de Adherencia:
1. **Elementos del Informe**:
   - Ir a `/reportes/adherencia/`
   - Verificar que muestra:
     - [ ] Días que entrena vs días planificados
     - [ ] Porcentaje de cumplimiento mensual
     - [ ] "Racha actual" (días consecutivos)
     - [ ] Sugerencias

---

## 🏥 7. PERFIL DE SALUD

### URL: `/perfil/salud/`

### Pruebas:
1. **Formulario de Perfil**:
   - Ir a `/perfil/salud/`
   - Verificar que el formulario tiene:
     - [ ] Campo "Peso (kg)"
     - [ ] Campo "Altura (cm)"
     - [ ] Campo "Condiciones médicas"
   - Llenar y guardar
   - Verificar que se guarda el perfil

2. **Actualización**:
   - Modificar valores existentes
   - Guardar
   - Verificar que se actualiza correctamente

---

## 💬 8. MENSAJERÍA

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
   - Verificar que muestra selector de destinatario (solo entrenadores asignados)
   - Llenar asunto y mensaje
   - Enviar
   - Verificar que se crea el mensaje

3. **Detalle de Mensaje**:
   - Hacer clic en un mensaje
   - Verificar que muestra contenido completo
   - Verificar que marca como leído

---

## 📅 9. EVENTOS INSTITUCIONALES

### URLs a Verificar:
- [ ] `/eventos/` - Lista de eventos
- [ ] `/eventos/<id>/` - Detalle de evento
- [ ] `/eventos/<id>/inscribir/` - Inscribirse a evento
- [ ] `/eventos/<id>/desinscribir/` - Desinscribirse de evento

### Pruebas:
1. **Lista de Eventos**:
   - Ir a `/eventos/`
   - Verificar que muestra eventos disponibles
   - Verificar que muestra: título, fecha, lugar, capacidad

2. **Detalle de Evento**:
   - Hacer clic en un evento
   - Verificar que muestra información completa
   - Verificar que muestra botón "Inscribirse" o "Desinscribirse"

3. **Inscripción**:
   - Inscribirse a un evento
   - Verificar que se registra la inscripción
   - Verificar que el botón cambia a "Desinscribirse"

---

## 🏋️ 10. ESPACIOS DEPORTIVOS Y RESERVAS

### URLs a Verificar:
- [ ] `/espacios/` - Lista de espacios
- [ ] `/espacios/<id>/` - Detalle de espacio
- [ ] `/reservas/nueva/` - Crear reserva
- [ ] `/reservas/` - Lista de reservas
- [ ] `/reservas/<id>/cancelar/` - Cancelar reserva

### Pruebas:
1. **Lista de Espacios**:
   - Ir a `/espacios/`
   - Verificar que muestra espacios disponibles
   - Verificar que muestra: nombre, tipo, capacidad, ubicación

2. **Detalle de Espacio**:
   - Hacer clic en un espacio
   - Verificar que muestra información completa
   - Verificar que muestra horarios disponibles
   - Verificar que muestra botón "Reservar"

3. **Crear Reserva**:
   - Ir a `/reservas/nueva/` o desde detalle de espacio
   - Verificar que el formulario tiene:
     - [ ] Selector de espacio
     - [ ] Campo fecha de reserva
     - [ ] Campo hora inicio
     - [ ] Campo hora fin
     - [ ] Campo notas
   - Llenar y guardar
   - Verificar que se crea la reserva

4. **Lista de Reservas**:
   - Ir a `/reservas/`
   - Verificar que muestra todas las reservas del usuario
   - Verificar que muestra estado (pendiente, confirmada, cancelada)

5. **Cancelar Reserva**:
   - Cancelar una reserva
   - Verificar que cambia el estado a "cancelada"

---

## 🔔 11. RECORDATORIOS

### URL: `/recordatorios/`

### Pruebas:
1. **Vista de Recordatorios**:
   - Ir a `/recordatorios/`
   - Verificar que muestra rutinas pendientes
   - Verificar que muestra recordatorios basados en frecuencia

---

## 🔍 12. VALIDACIONES Y SEGURIDAD

### Pruebas de Seguridad:
- [ ] No puede acceder a rutinas de otros usuarios
- [ ] No puede modificar progreso de otros usuarios
- [ ] No puede acceder a páginas de entrenador sin ser entrenador
- [ ] No puede acceder a páginas de administrador sin ser administrador

### Pruebas de Validación:
- [ ] Formularios validan campos requeridos
- [ ] Mensajes de error se muestran correctamente
- [ ] Validaciones de datos (fechas, números, etc.)

---

## 📝 13. NAVEGACIÓN Y MENÚ

### Elementos del Menú a Verificar:
- [ ] "Inicio" - Redirige a dashboard
- [ ] "Mis Rutinas" - Redirige a lista de rutinas
- [ ] "Ejercicios" - Redirige a lista de ejercicios
- [ ] "Progreso" - Redirige a lista de progreso
- [ ] "Informes" - Redirige a informes
- [ ] "Eventos" - Redirige a eventos
- [ ] "Espacios" - Redirige a espacios
- [ ] "Mensajes" - Redirige a mensajes (si tiene entrenador)
- [ ] "Mi Entrenador" - Redirige a información del entrenador (si tiene)
- [ ] "Salir" - Cierra sesión

---

## ✅ RESUMEN DE VERIFICACIÓN

### Funcionalidades Principales:
- [x] Autenticación y login
- [x] Dashboard del usuario
- [x] Gestión de rutinas (crear, listar, detalle, adoptar, agregar ejercicios)
- [x] Gestión de ejercicios (listar, detalle, crear personalizados, filtros)
- [x] Registro de progreso (crear, listar, filtros)
- [x] Informes (progreso, adherencia, balance, tendencias, logros)
- [x] Perfil de salud
- [x] Mensajería
- [x] Eventos institucionales
- [x] Espacios deportivos y reservas
- [x] Recordatorios
- [x] Navegación y menús

### Errores Corregidos:
- [x] Error de template `div` en `progress_list.html` → Corregido usando `widthratio`
- [x] URL `/admin/asignar-entrenador/` no funcionaba → Corregido moviendo Django admin a `/django-admin/`
- [x] Solo aparecían 2 entrenadores → Corregido para obtener todos los empleados de BD institucional
- [x] `test_trainer` aparecía en lista → Corregido filtrando usuarios de prueba

---

## 🚀 CÓMO USAR ESTE CHECKLIST

1. **Inicia sesión** como usuario estándar (`laura.h` / `lh123`)
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
- Verifica que las conversiones de tiempo funcionan correctamente

---

**Última actualización**: Después de corregir error de template `div`

