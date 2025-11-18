# Justificación de Arquitectura NoSQL - Gym Icesi

## 📐 Arquitectura Híbrida: PostgreSQL + MongoDB

El proyecto **Gym Icesi** utiliza una arquitectura híbrida que combina:
- **PostgreSQL (Neon)**: Base de datos relacional para datos estructurados
- **MongoDB (Atlas)**: Base de datos NoSQL documental para datos flexibles

---

## 🎯 ¿Por qué PostgreSQL (Neon)?

### Ventajas para este proyecto:

1. **Integridad Referencial**
   - Relaciones claras entre entidades (Usuario → Rutina → Ejercicio)
   - Foreign keys garantizan consistencia
   - Transacciones ACID para operaciones críticas

2. **Datos Estructurados**
   - Esquema fijo y bien definido
   - Perfecto para: usuarios, rutinas, ejercicios, asignaciones
   - Consultas complejas con JOINs eficientes

3. **Integración con BD Institucional**
   - Mismo motor (PostgreSQL) facilita consultas cruzadas
   - Acceso directo a tablas `users`, `students`, `employees`
   - Sin necesidad de sincronización compleja

4. **Estadísticas Agregadas**
   - Tablas `UserMonthlyStats` y `TrainerMonthlyStats`
   - Consultas de agregación eficientes
   - Índices optimizados para reportes

### Casos de Uso en el Proyecto:
- ✅ Autenticación y roles de usuario
- ✅ Estructura de rutinas y ejercicios
- ✅ Relaciones entre entidades
- ✅ Estadísticas mensuales estructuradas
- ✅ Asignaciones entrenador-usuario

---

## 🎯 ¿Por qué MongoDB (Atlas)?

### Ventajas para este proyecto:

1. **Flexibilidad de Esquema**
   - El progreso de entrenamiento es variable:
     - Algunos usuarios registran peso, otros no
     - Algunos incluyen fotos, otros solo notas
     - Métricas adicionales pueden agregarse sin migraciones
   
2. **Documentos Complejos**
   - Un solo documento puede contener toda la información de una sesión:
     ```json
     {
       "user_id": "jp123",
       "routine_id": 5,
       "fecha": "2024-01-15",
       "series_completadas": 3,
       "reps_completadas": 12,
       "tiempo_segundos": 1800,
       "esfuerzo_percibido": 7,
       "peso_usado": 20,
       "notas": "Me sentí fuerte hoy",
       "fotos": ["url1", "url2"],
       "metricas_adicionales": {
         "frecuencia_cardiaca_promedio": 145,
         "calorias_quemadas": 250,
         "sensacion": "energizado"
       }
     }
     ```

3. **Evolución sin Migraciones**
   - Agregar nuevos campos no requiere ALTER TABLE
   - Diferentes usuarios pueden tener diferentes estructuras
   - Ideal para datos que cambian frecuentemente

4. **Logs y Metadata**
   - Logs de actividad con estructura variable
   - Metadata de ejercicios (tags, variaciones, consejos)
   - Plantillas de rutinas con estructura flexible

5. **Escalabilidad Horizontal**
   - MongoDB Atlas permite escalar fácilmente
   - Sharding automático para grandes volúmenes
   - Replicación para alta disponibilidad

### Casos de Uso en el Proyecto:

#### 1. Progreso Detallado (`progress_logs`)
**Problema**: El modelo `ProgressLog` en PostgreSQL tiene campos fijos, pero cada usuario puede querer registrar información diferente.

**Solución MongoDB**:
- Documento flexible con campos opcionales
- Métricas adicionales como objeto anidado
- Fotos, sensaciones, notas extensas
- Sin necesidad de múltiples tablas relacionadas

**Ejemplo Real**:
```javascript
// Usuario A: Registra progreso básico
{
  "user_id": "estudiante1",
  "routine_id": 10,
  "fecha": ISODate("2024-01-15"),
  "tiempo_segundos": 1800,
  "esfuerzo_percibido": 7,
  "notas": "Buen entrenamiento"
}

// Usuario B: Registra progreso detallado
{
  "user_id": "estudiante2",
  "routine_id": 10,
  "fecha": ISODate("2024-01-15"),
  "series_completadas": 4,
  "reps_completadas": 12,
  "peso_usado": 25,
  "tiempo_segundos": 2400,
  "esfuerzo_percibido": 8,
  "metricas_adicionales": {
    "frecuencia_cardiaca_max": 165,
    "calorias": 320,
    "sensacion": "agotado pero satisfecho",
    "equipamiento_usado": ["mancuernas", "banco"]
  },
  "fotos": ["https://storage.../foto1.jpg"]
}
```

#### 2. Logs de Actividad (`user_activity_logs`)
**Problema**: Los logs tienen estructura variable según la acción.

**Solución MongoDB**:
- Un solo documento por acción
- Metadata específica según el tipo de acción
- Fácil agregación por tipo de acción o usuario

**Ejemplo**:
```javascript
// Log de creación de rutina
{
  "user_id": "estudiante1",
  "action": "create_routine",
  "entity_type": "routine",
  "entity_id": 15,
  "metadata": {
    "routine_name": "Rutina Cardio",
    "descripcion": "Rutina de 30 min"
  },
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "ip_address": "192.168.1.1"
}

// Log de registro de progreso
{
  "user_id": "estudiante1",
  "action": "log_progress",
  "entity_type": "progress",
  "entity_id": 42,
  "metadata": {
    "routine_name": "Rutina Cardio",
    "fecha": "2024-01-15",
    "esfuerzo": 7
  },
  "timestamp": ISODate("2024-01-15T18:00:00Z")
}
```

#### 3. Metadata de Ejercicios (`exercise_details`)
**Problema**: Los ejercicios pueden tener información adicional variable.

**Solución MongoDB**:
- Tags, variaciones, consejos como arrays
- Estadísticas de uso como objeto
- Sin necesidad de tablas de relación many-to-many

**Ejemplo**:
```javascript
{
  "exercise_id": 5,
  "tags": ["cardio", "principiante", "sin-equipo"],
  "variaciones": [
    "Correr en el lugar",
    "Burpees modificados",
    "Jumping jacks"
  ],
  "consejos": [
    "Mantén el ritmo constante",
    "Hidrátate bien"
  ],
  "equipamiento_necesario": [],
  "musculos_trabajados": ["piernas", "core", "cardiovascular"],
  "nivel_recomendado": "principiante",
  "estadisticas_uso": {
    "veces_usado": 150,
    "promedio_esfuerzo": 6.5,
    "usuarios_que_lo_usaron": 45
  }
}
```

#### 4. Plantillas de Rutinas (`routine_templates`)
**Problema**: Las rutinas prediseñadas pueden tener estructuras complejas.

**Solución MongoDB**:
- Estructura flexible para diferentes tipos de rutinas
- Objetivos, tags, variaciones
- Contador de veces adoptada

---

## 📊 Comparación: PostgreSQL vs MongoDB

| Aspecto | PostgreSQL | MongoDB |
|---------|------------|---------|
| **Esquema** | Fijo, requiere migraciones | Flexible, sin migraciones |
| **Relaciones** | JOINs eficientes | Referencias o documentos embebidos |
| **Consultas** | SQL estándar | Query language específico |
| **Transacciones** | ACID completo | ACID en documentos únicos |
| **Escalabilidad** | Vertical (más hardware) | Horizontal (más servidores) |
| **Casos de Uso** | Datos estructurados | Datos flexibles/variables |

---

## 🔄 Integración Dual: ¿Cómo Funciona?

### Flujo de Datos:

1. **Creación de Rutina**:
   - PostgreSQL: Guarda estructura básica (`Routine`, `RoutineItem`)
   - MongoDB: Guarda metadata y detalles extendidos (`user_routines`)

2. **Registro de Progreso**:
   - PostgreSQL: Guarda datos esenciales (`ProgressLog`)
   - MongoDB: Guarda información detallada y flexible (`progress_logs`)
   - Ambos se actualizan en la misma transacción (o casi)

3. **Consultas**:
   - Datos básicos: Desde PostgreSQL (rápido, estructurado)
   - Datos detallados: Desde MongoDB (flexible, completo)
   - Reportes: Combinan ambos según necesidad

### Ventajas de esta Arquitectura:

✅ **Mejor de ambos mundos**:
- Estructura y consistencia de PostgreSQL
- Flexibilidad y escalabilidad de MongoDB

✅ **Resiliencia**:
- Si MongoDB falla, la app sigue funcionando (datos básicos en PostgreSQL)
- Si PostgreSQL falla, los datos detallados están en MongoDB

✅ **Performance**:
- Consultas rápidas en PostgreSQL para datos estructurados
- Consultas flexibles en MongoDB para datos variables

---

## 📈 Ejemplos de Documentos MongoDB en el Proyecto

### 1. Progreso Detallado
```javascript
// Colección: progress_logs
{
  "_id": ObjectId("..."),
  "user_id": "jp123",
  "routine_id": 5,
  "exercise_id": 12,
  "fecha": ISODate("2024-01-15"),
  "series_completadas": 3,
  "reps_completadas": 12,
  "tiempo_segundos": 1800,
  "esfuerzo_percibido": 7,
  "peso_usado": 20,
  "notas": "Me sentí fuerte, podría aumentar peso",
  "fotos": [],
  "metricas_adicionales": {
    "frecuencia_cardiaca_promedio": 145,
    "calorias_quemadas": 250
  },
  "created_at": ISODate("2024-01-15T18:30:00Z"),
  "updated_at": ISODate("2024-01-15T18:30:00Z")
}
```

### 2. Log de Actividad
```javascript
// Colección: user_activity_logs
{
  "_id": ObjectId("..."),
  "user_id": "jp123",
  "action": "create_routine",
  "entity_type": "routine",
  "entity_id": 15,
  "metadata": {
    "routine_name": "Rutina Cardio Intensa",
    "descripcion": "30 minutos de cardio"
  },
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### 3. Detalles de Ejercicio
```javascript
// Colección: exercise_details
{
  "_id": ObjectId("..."),
  "exercise_id": 5,
  "tags": ["cardio", "principiante", "sin-equipo"],
  "variaciones": [
    "Correr en el lugar",
    "Burpees modificados"
  ],
  "consejos": [
    "Mantén el ritmo constante",
    "Hidrátate bien"
  ],
  "equipamiento_necesario": [],
  "musculos_trabajados": ["piernas", "core"],
  "nivel_recomendado": "principiante",
  "estadisticas_uso": {
    "veces_usado": 150,
    "promedio_esfuerzo": 6.5
  },
  "created_at": ISODate("2024-01-10T08:00:00Z"),
  "updated_at": ISODate("2024-01-15T12:00:00Z")
}
```

---

## ✅ Conclusión

La arquitectura híbrida **PostgreSQL + MongoDB** es la elección correcta para este proyecto porque:

1. **PostgreSQL** maneja perfectamente:
   - Datos estructurados y relaciones
   - Integridad referencial
   - Integración con BD institucional
   - Estadísticas agregadas

2. **MongoDB** maneja perfectamente:
   - Datos flexibles y variables
   - Logs de actividad
   - Metadata extensa
   - Evolución sin migraciones

3. **Juntos** proporcionan:
   - Mejor rendimiento
   - Mayor flexibilidad
   - Escalabilidad
   - Resiliencia

Esta arquitectura es **escalable, mantenible y adecuada** para las necesidades del proyecto Gym Icesi.

