"""
Servicio para interactuar con MongoDB (NoSQL)
Maneja la conexión y operaciones CRUD para datos NoSQL
"""
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    ConnectionFailure = Exception
    ServerSelectionTimeoutError = Exception
    ObjectId = None

from django.conf import settings
from datetime import datetime, date
import logging
import os

logger = logging.getLogger(__name__)

class MongoDBService:
    """Servicio singleton para MongoDB"""
    _client = None
    _db = None
    
    @classmethod
    def get_client(cls):
        """Obtiene o crea el cliente de MongoDB"""
        if not PYMONGO_AVAILABLE:
            return None
        if cls._client is None and settings.MONGODB_ENABLED:
            try:
                config = settings.MONGODB_SETTINGS
                
                # PRIORIDAD: Verificar si hay connection string completa (para Atlas)
                connection_string = os.getenv("MONGODB_CONNECTION_STRING", "").strip()
                if connection_string:
                    # Usar la connection string directamente (ya viene completa con credenciales)
                    uri = connection_string
                    logger.info("Usando MONGODB_CONNECTION_STRING completa")
                else:
                    # Construir URI de conexión manualmente
                    if config.get("username") and config.get("password"):
                        host = config.get("host", "")
                        # Para Atlas con SRV
                        if "mongodb.net" in host or ".mongodb.net" in host:
                            uri = f"mongodb+srv://{config['username']}:{config['password']}@{host}/{config['db']}?retryWrites=true&w=majority"
                        else:
                            uri = f"mongodb://{config['username']}:{config['password']}@{host}:{config['port']}/{config['db']}?authSource={config.get('authentication_source', 'admin')}"
                    else:
                        uri = f"mongodb://{config['host']}:{config['port']}/{config['db']}"
                
                cls._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                # Verificar conexión
                cls._client.admin.command('ping')
                logger.info("Conexión a MongoDB establecida correctamente")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"No se pudo conectar a MongoDB: {e}")
                cls._client = None
            except Exception as e:
                logger.warning(f"Error configurando MongoDB: {e}")
                cls._client = None
        return cls._client
    
    @classmethod
    def get_db(cls):
        """Obtiene la base de datos de MongoDB"""
        if cls._db is None:
            client = cls.get_client()
            if client:
                config = settings.MONGODB_SETTINGS
                cls._db = client[config['db']]
        return cls._db
    
    @classmethod
    def is_available(cls):
        """Verifica si MongoDB está disponible"""
        try:
            client = cls.get_client()
            if client:
                client.admin.command('ping')
                return True
        except:
            pass
        return False


class ProgressLogService:
    """Servicio para gestionar registros de progreso en MongoDB"""
    
    @staticmethod
    def save_detailed_progress(user_id, routine_id, exercise_id, fecha, **kwargs):
        """
        Guarda un registro detallado de progreso en MongoDB
        
        Args:
            user_id: ID del usuario (username)
            routine_id: ID de la rutina en PostgreSQL
            exercise_id: ID del ejercicio en PostgreSQL
            fecha: Fecha del progreso
            **kwargs: Datos adicionales (series, reps, tiempo_seg, esfuerzo, notas, etc.)
        """
        if not MongoDBService.is_available():
            logger.warning("MongoDB no disponible, no se guardó progreso detallado")
            return None
        
        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.progress_logs
        
        document = {
            "user_id": str(user_id),
            "routine_id": int(routine_id),
            "exercise_id": int(exercise_id) if exercise_id else None,
            "fecha": datetime.combine(fecha, datetime.min.time()) if isinstance(fecha, date) else fecha,
            "series_completadas": kwargs.get("series"),
            "reps_completadas": kwargs.get("reps"),
            "tiempo_segundos": kwargs.get("tiempo_seg"),
            "esfuerzo_percibido": kwargs.get("esfuerzo"),
            "peso_usado": kwargs.get("peso_usado"),
            "notas": kwargs.get("notas", ""),
            "fotos": kwargs.get("fotos", []),
            "metricas_adicionales": kwargs.get("metricas_adicionales", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Crear índices si no existen
        collection.create_index([("user_id", 1), ("fecha", -1)])
        collection.create_index([("routine_id", 1), ("fecha", -1)])
        
        result = collection.insert_one(document)
        logger.info(f"Progreso detallado guardado en MongoDB: {result.inserted_id}")
        return result.inserted_id
    
    @staticmethod
    def get_user_progress(user_id, start_date=None, end_date=None, limit=100):
        """
        Obtiene el historial de progreso de un usuario
        
        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            limit: Límite de resultados
        """
        if not MongoDBService.is_available():
            return []
        
        db = MongoDBService.get_db()
        if db is None:
            return []

        collection = db.progress_logs
        query = {"user_id": str(user_id)}
        
        if start_date or end_date:
            query["fecha"] = {}
            if start_date:
                query["fecha"]["$gte"] = datetime.combine(start_date, datetime.min.time()) if isinstance(start_date, date) else start_date
            if end_date:
                query["fecha"]["$lte"] = datetime.combine(end_date, datetime.min.time()) if isinstance(end_date, date) else end_date
        
        cursor = collection.find(query).sort("fecha", -1).limit(limit)
        return list(cursor)


class ActivityLogService:
    """Servicio para registrar logs de actividad"""
    
    @staticmethod
    def log_activity(user_id, action, entity_type=None, entity_id=None, metadata=None, request=None):
        """
        Registra una actividad del usuario en MongoDB
        
        Args:
            user_id: ID del usuario
            action: Tipo de acción (create_routine, add_exercise, log_progress, etc.)
            entity_type: Tipo de entidad (routine, exercise, progress, etc.)
            entity_id: ID de la entidad
            metadata: Diccionario con información adicional
            request: Objeto request de Django (opcional)
        """
        if not MongoDBService.is_available():
            return None
        
        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.user_activity_logs
        
        document = {
            "user_id": str(user_id),
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }
        
        if request:
            document["ip_address"] = request.META.get("REMOTE_ADDR", "")
            document["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
        
        # Crear índices si no existen
        collection.create_index([("user_id", 1), ("timestamp", -1)])
        collection.create_index([("action", 1), ("timestamp", -1)])
        
        result = collection.insert_one(document)
        return result.inserted_id


class ExerciseDetailsService:
    """Servicio para gestionar detalles extendidos de ejercicios"""

    @staticmethod
    def save_exercise_details(exercise_id, **kwargs):
        """
        Guarda detalles extendidos de un ejercicio

        Args:
            exercise_id: ID del ejercicio en PostgreSQL
            **kwargs: Datos adicionales (variaciones, consejos, equipamiento, etc.)
        """
        if not MongoDBService.is_available():
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.exercise_details

        document = {
            "exercise_id": int(exercise_id),
            "variaciones": kwargs.get("variaciones", []),
            "consejos": kwargs.get("consejos", []),
            "equipamiento_necesario": kwargs.get("equipamiento_necesario", []),
            "musculos_trabajados": kwargs.get("musculos_trabajados", []),
            "nivel_recomendado": kwargs.get("nivel_recomendado", ""),
            "tags": kwargs.get("tags", []),
            "estadisticas_uso": kwargs.get("estadisticas_uso", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Usar upsert para actualizar si existe o crear si no
        collection.create_index([("exercise_id", 1)], unique=True)
        collection.create_index([("tags", 1)])

        result = collection.update_one(
            {"exercise_id": int(exercise_id)},
            {"$set": document},
            upsert=True
        )
        return result.upserted_id or exercise_id

    @staticmethod
    def get_exercise_details(exercise_id):
        """Obtiene los detalles extendidos de un ejercicio"""
        if not MongoDBService.is_available():
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.exercise_details
        return collection.find_one({"exercise_id": int(exercise_id)})


class ExerciseService:
    """Servicio para gestionar ejercicios en MongoDB (complemento a BD relacional)"""

    @staticmethod
    def save_exercise(exercise_id, user_id, **kwargs):
        """
        Guarda información del ejercicio en MongoDB

        Args:
            exercise_id: ID del ejercicio en PostgreSQL
            user_id: ID del usuario creador (username)
            **kwargs: Datos adicionales del ejercicio
        """
        if not MongoDBService.is_available():
            logger.warning("MongoDB no disponible, no se guardó ejercicio")
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.exercises

        document = {
            "exercise_id": int(exercise_id),
            "user_id": str(user_id) if user_id else None,
            "nombre": kwargs.get("nombre", ""),
            "tipo": kwargs.get("tipo", ""),
            "descripcion": kwargs.get("descripcion", ""),
            "duracion_min": kwargs.get("duracion_min", 0),
            "dificultad": kwargs.get("dificultad", 1),
            "video_url": kwargs.get("video_url", ""),
            "es_personalizado": kwargs.get("es_personalizado", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Crear índices
        collection.create_index([("exercise_id", 1)], unique=True)
        collection.create_index([("user_id", 1), ("created_at", -1)])
        collection.create_index([("tipo", 1)])

        result = collection.update_one(
            {"exercise_id": int(exercise_id)},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Ejercicio guardado en MongoDB: {exercise_id}")
        return result.upserted_id or exercise_id


class RoutineService:
    """Servicio para gestionar rutinas en MongoDB (complemento a BD relacional)"""

    @staticmethod
    def save_user_routine(routine_id, user_id, **kwargs):
        """
        Guarda información de rutina de usuario en MongoDB

        Args:
            routine_id: ID de la rutina en PostgreSQL
            user_id: ID del usuario (username)
            **kwargs: Datos adicionales
        """
        if not MongoDBService.is_available():
            logger.warning("MongoDB no disponible, no se guardó rutina")
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.user_routines

        document = {
            "routine_id": int(routine_id),
            "user_id": str(user_id),
            "nombre": kwargs.get("nombre", ""),
            "descripcion": kwargs.get("descripcion", ""),
            "es_predisenada": kwargs.get("es_predisenada", False),
            "trainer_id": str(kwargs.get("trainer_id")) if kwargs.get("trainer_id") else None,
            "exercises": kwargs.get("exercises", []),  # Lista de exercise_ids
            "items_detalle": kwargs.get("items_detalle", []),  # Detalle de items
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Crear índices
        collection.create_index([("routine_id", 1)], unique=True)
        collection.create_index([("user_id", 1), ("created_at", -1)])
        collection.create_index([("trainer_id", 1)])

        result = collection.update_one(
            {"routine_id": int(routine_id)},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Rutina de usuario guardada en MongoDB: {routine_id}")
        return result.upserted_id or routine_id

    @staticmethod
    def save_routine_template(routine_id, trainer_id, **kwargs):
        """
        Guarda plantilla de rutina prediseñada en MongoDB

        Args:
            routine_id: ID de la rutina en PostgreSQL
            trainer_id: ID del entrenador creador (username)
            **kwargs: Datos adicionales
        """
        if not MongoDBService.is_available():
            logger.warning("MongoDB no disponible, no se guardó plantilla")
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.routine_templates

        document = {
            "routine_id": int(routine_id),
            "trainer_id": str(trainer_id),
            "nombre": kwargs.get("nombre", ""),
            "descripcion": kwargs.get("descripcion", ""),
            "nivel_recomendado": kwargs.get("nivel_recomendado", ""),
            "objetivo": kwargs.get("objetivo", ""),
            "duracion_estimada_min": kwargs.get("duracion_estimada_min", 0),
            "exercises": kwargs.get("exercises", []),
            "items_detalle": kwargs.get("items_detalle", []),
            "veces_adoptada": kwargs.get("veces_adoptada", 0),
            "tags": kwargs.get("tags", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Crear índices
        collection.create_index([("routine_id", 1)], unique=True)
        collection.create_index([("trainer_id", 1), ("created_at", -1)])
        collection.create_index([("tags", 1)])

        result = collection.update_one(
            {"routine_id": int(routine_id)},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Plantilla de rutina guardada en MongoDB: {routine_id}")
        return result.upserted_id or routine_id

    @staticmethod
    def get_user_routines(user_id, limit=50):
        """Obtiene las rutinas de un usuario desde MongoDB"""
        if not MongoDBService.is_available():
            return []

        db = MongoDBService.get_db()
        if db is None:
            return []

        collection = db.user_routines
        cursor = collection.find({"user_id": str(user_id)}).sort("created_at", -1).limit(limit)
        return list(cursor)


class TrainerAssignmentService:
    """Servicio para gestionar asignaciones de entrenadores en MongoDB"""

    @staticmethod
    def save_assignment(assignment_id, user_id, trainer_id, **kwargs):
        """
        Guarda asignación de entrenador en MongoDB

        Args:
            assignment_id: ID de la asignación en PostgreSQL
            user_id: ID del usuario (username)
            trainer_id: ID del entrenador (username)
            **kwargs: Datos adicionales
        """
        if not MongoDBService.is_available():
            logger.warning("MongoDB no disponible, no se guardó asignación")
            return None

        db = MongoDBService.get_db()
        if db is None:
            return None

        collection = db.trainer_assignments

        document = {
            "assignment_id": int(assignment_id),
            "user_id": str(user_id),
            "trainer_id": str(trainer_id),
            "fecha_asignacion": kwargs.get("fecha_asignacion", datetime.utcnow()),
            "activo": kwargs.get("activo", True),
            "notas": kwargs.get("notas", ""),
            "objetivos": kwargs.get("objetivos", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Crear índices
        collection.create_index([("assignment_id", 1)], unique=True)
        collection.create_index([("user_id", 1), ("activo", 1)])
        collection.create_index([("trainer_id", 1), ("activo", 1)])

        result = collection.update_one(
            {"assignment_id": int(assignment_id)},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Asignación de entrenador guardada en MongoDB: {assignment_id}")
        return result.upserted_id or assignment_id

    @staticmethod
    def get_trainer_assignees(trainer_id, active_only=True):
        """Obtiene los usuarios asignados a un entrenador"""
        if not MongoDBService.is_available():
            return []

        db = MongoDBService.get_db()
        if db is None:
            return []

        collection = db.trainer_assignments
        query = {"trainer_id": str(trainer_id)}
        if active_only:
            query["activo"] = True

        cursor = collection.find(query).sort("fecha_asignacion", -1)
        return list(cursor)

