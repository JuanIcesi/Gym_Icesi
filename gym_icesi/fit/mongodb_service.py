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
from datetime import datetime
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
                
                # Verificar si hay connection string completa (para Atlas)
                connection_string = os.getenv("MONGODB_CONNECTION_STRING", "")
                if connection_string:
                    # Reemplazar <password> si existe
                    if "<password>" in connection_string and config.get("password"):
                        connection_string = connection_string.replace("<password>", config["password"])
                    uri = connection_string
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
        if not db:
            return None
        
        collection = db.progress_logs
        
        document = {
            "user_id": str(user_id),
            "routine_id": int(routine_id),
            "exercise_id": int(exercise_id) if exercise_id else None,
            "fecha": datetime.combine(fecha, datetime.min.time()) if isinstance(fecha, datetime.date) else fecha,
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
        if not db:
            return []
        
        collection = db.progress_logs
        query = {"user_id": str(user_id)}
        
        if start_date or end_date:
            query["fecha"] = {}
            if start_date:
                query["fecha"]["$gte"] = datetime.combine(start_date, datetime.min.time()) if isinstance(start_date, datetime.date) else start_date
            if end_date:
                query["fecha"]["$lte"] = datetime.combine(end_date, datetime.min.time()) if isinstance(end_date, datetime.date) else end_date
        
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
        if not db:
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
        if not db:
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
        if not db:
            return None
        
        collection = db.exercise_details
        return collection.find_one({"exercise_id": int(exercise_id)})

