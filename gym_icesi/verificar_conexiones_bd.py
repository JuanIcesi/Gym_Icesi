"""
Script para verificar las conexiones a MongoDB y Neon (PostgreSQL)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.db import connection
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import psycopg2
from psycopg2 import OperationalError

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def verificar_postgresql_neon():
    """Verifica la conexión a PostgreSQL (Neon)"""
    print_header("VERIFICACION DE POSTGRESQL (NEON)")
    
    resultados = {
        'configuracion': False,
        'conexion': False,
        'tablas_institucionales': False,
        'tablas_aplicacion': False,
    }
    
    # 1. Verificar configuración
    print_info("1. Verificando configuración...")
    try:
        db_config = settings.DATABASES['default']
        print_info(f"   Engine: {db_config.get('ENGINE', 'N/A')}")
        print_info(f"   Name: {db_config.get('NAME', 'N/A')}")
        print_info(f"   Host: {db_config.get('HOST', 'N/A')}")
        print_info(f"   Port: {db_config.get('PORT', 'N/A')}")
        print_info(f"   User: {db_config.get('USER', 'N/A')}")
        
        if db_config.get('ENGINE') == 'django.db.backends.postgresql':
            resultados['configuracion'] = True
            print_success("   Configuración de PostgreSQL encontrada")
        else:
            print_error("   No se encontró configuración de PostgreSQL")
            return resultados
    except Exception as e:
        print_error(f"   Error al verificar configuración: {e}")
        return resultados
    
    # 2. Verificar conexión
    print_info("\n2. Verificando conexión...")
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print_success(f"   Conexión exitosa a PostgreSQL")
            print_info(f"   Versión: {version[:50]}...")
            resultados['conexion'] = True
    except OperationalError as e:
        print_error(f"   Error de conexión: {e}")
        return resultados
    except Exception as e:
        print_error(f"   Error inesperado: {e}")
        return resultados
    
    # 3. Verificar tablas institucionales
    print_info("\n3. Verificando tablas institucionales...")
    tablas_institucionales = [
        'users', 'students', 'employees', 'faculties', 
        'campuses', 'programs', 'subjects'
    ]
    tablas_encontradas = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tablas_existentes = [row[0] for row in cur.fetchall()]
            
            for tabla in tablas_institucionales:
                if tabla in tablas_existentes:
                    tablas_encontradas.append(tabla)
                    print_success(f"   Tabla '{tabla}' encontrada")
                else:
                    print_warning(f"   Tabla '{tabla}' NO encontrada")
            
            if len(tablas_encontradas) == len(tablas_institucionales):
                resultados['tablas_institucionales'] = True
                print_success(f"   Todas las tablas institucionales están presentes")
            else:
                print_warning(f"   Solo {len(tablas_encontradas)}/{len(tablas_institucionales)} tablas institucionales encontradas")
    except Exception as e:
        print_error(f"   Error al verificar tablas: {e}")
    
    # 4. Verificar datos en tablas institucionales
    print_info("\n4. Verificando datos en tablas institucionales...")
    try:
        with connection.cursor() as cur:
            # Verificar usuarios
            cur.execute("SELECT COUNT(*) FROM users;")
            count_users = cur.fetchone()[0]
            print_info(f"   Usuarios en BD: {count_users}")
            
            # Verificar estudiantes
            cur.execute("SELECT COUNT(*) FROM students;")
            count_students = cur.fetchone()[0]
            print_info(f"   Estudiantes en BD: {count_students}")
            
            # Verificar empleados
            cur.execute("SELECT COUNT(*) FROM employees;")
            count_employees = cur.fetchone()[0]
            print_info(f"   Empleados en BD: {count_employees}")
            
            if count_users > 0 and (count_students > 0 or count_employees > 0):
                print_success("   Hay datos en las tablas institucionales")
            else:
                print_warning("   Las tablas institucionales están vacías")
    except Exception as e:
        print_error(f"   Error al verificar datos: {e}")
    
    # 5. Verificar tablas de la aplicación
    print_info("\n5. Verificando tablas de la aplicación...")
    tablas_aplicacion = [
        'fit_exercise', 'fit_routine', 'fit_routineitem', 
        'fit_progresslog', 'fit_trainerassignment',
        'fit_usermonthlystats', 'fit_trainermonthlystats'
    ]
    tablas_app_encontradas = []
    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name LIKE 'fit_%'
                ORDER BY table_name;
            """)
            tablas_app_existentes = [row[0] for row in cur.fetchall()]
            
            for tabla in tablas_aplicacion:
                if tabla in tablas_app_existentes:
                    tablas_app_encontradas.append(tabla)
                    print_success(f"   Tabla '{tabla}' encontrada")
                else:
                    print_warning(f"   Tabla '{tabla}' NO encontrada")
            
            if len(tablas_app_encontradas) > 0:
                resultados['tablas_aplicacion'] = True
                print_success(f"   {len(tablas_app_encontradas)} tablas de la aplicación encontradas")
            else:
                print_warning("   No se encontraron tablas de la aplicación (ejecuta migraciones)")
    except Exception as e:
        print_error(f"   Error al verificar tablas de aplicación: {e}")
    
    return resultados

def verificar_mongodb():
    """Verifica la conexión a MongoDB"""
    print_header("VERIFICACION DE MONGODB")
    
    resultados = {
        'configuracion': False,
        'conexion': False,
        'base_datos': False,
        'colecciones': False,
    }
    
    # 1. Verificar configuración
    print_info("1. Verificando configuración...")
    try:
        # Usar la misma lógica que MongoDBService
        connection_string = os.getenv("MONGODB_CONNECTION_STRING", "").strip()
        mongo_config = settings.MONGODB_SETTINGS
        
        if connection_string:
            mongo_uri = connection_string
            uri_safe = connection_string.split('@')[0].split(':')[0] + ':***@' + '@'.join(connection_string.split('@')[1:])
            print_info(f"   Usando MONGODB_CONNECTION_STRING: {uri_safe}")
            resultados['configuracion'] = True
        elif mongo_config.get("username") and mongo_config.get("password"):
            host = mongo_config.get("host", "")
            if "mongodb.net" in host or ".mongodb.net" in host:
                mongo_uri = f"mongodb+srv://{mongo_config['username']}:{mongo_config['password']}@{host}/{mongo_config['db']}?retryWrites=true&w=majority"
            else:
                mongo_uri = f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{host}:{mongo_config.get('port', 27017)}/{mongo_config['db']}"
            uri_safe = mongo_uri.split('@')[0].split(':')[0] + ':***@' + '@'.join(mongo_uri.split('@')[1:])
            print_info(f"   URI construida desde configuración: {uri_safe}")
            print_info(f"   Host: {host}")
            print_info(f"   Database: {mongo_config.get('db', 'N/A')}")
            resultados['configuracion'] = True
        else:
            print_error("   No se encontró configuración de MongoDB (ni MONGODB_CONNECTION_STRING ni MONGODB_SETTINGS completo)")
            return resultados
    except Exception as e:
        print_error(f"   Error al verificar configuración: {e}")
        return resultados
    
    # 2. Verificar conexión
    print_info("\n2. Verificando conexión...")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Intentar obtener información del servidor
        server_info = client.server_info()
        print_success("   Conexión exitosa a MongoDB")
        print_info(f"   Versión del servidor: {server_info.get('version', 'N/A')}")
        resultados['conexion'] = True
    except ConnectionFailure as e:
        print_error(f"   Error de conexión: {e}")
        return resultados
    except ServerSelectionTimeoutError as e:
        print_error(f"   Timeout al conectar: {e}")
        return resultados
    except Exception as e:
        print_error(f"   Error inesperado: {e}")
        return resultados
    
    # 3. Verificar base de datos
    print_info("\n3. Verificando base de datos...")
    try:
        # Obtener nombre de BD desde configuración o URI
        if connection_string:
            db_name = connection_string.split('/')[-1].split('?')[0]
        else:
            db_name = mongo_config.get('db', 'sid_gym_icesi')
        db = client[db_name]
        print_info(f"   Base de datos: {db_name}")
        
        # Listar colecciones
        colecciones = db.list_collection_names()
        print_info(f"   Colecciones encontradas: {len(colecciones)}")
        
        if len(colecciones) > 0:
            print_success("   Base de datos accesible y con colecciones")
            resultados['base_datos'] = True
            resultados['colecciones'] = True
            
            # Mostrar colecciones
            for coleccion in colecciones:
                count = db[coleccion].count_documents({})
                print_info(f"   - {coleccion}: {count} documentos")
        else:
            print_warning("   Base de datos accesible pero sin colecciones (esto es normal si no hay datos aún)")
            resultados['base_datos'] = True
    except Exception as e:
        print_error(f"   Error al verificar base de datos: {e}")
    
    # Cerrar conexión
    try:
        client.close()
    except:
        pass
    
    return resultados

def main():
    print_header("VERIFICACION DE CONEXIONES A BASES DE DATOS")
    
    # Verificar PostgreSQL/Neon
    resultados_pg = verificar_postgresql_neon()
    
    # Verificar MongoDB
    resultados_mongo = verificar_mongodb()
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    print("\nPostgreSQL (Neon):")
    print(f"  Configuración: {'OK' if resultados_pg['configuracion'] else 'ERROR'}")
    print(f"  Conexión: {'OK' if resultados_pg['conexion'] else 'ERROR'}")
    print(f"  Tablas institucionales: {'OK' if resultados_pg['tablas_institucionales'] else 'WARNING'}")
    print(f"  Tablas aplicación: {'OK' if resultados_pg['tablas_aplicacion'] else 'WARNING'}")
    
    print("\nMongoDB:")
    print(f"  Configuración: {'OK' if resultados_mongo['configuracion'] else 'ERROR'}")
    print(f"  Conexión: {'OK' if resultados_mongo['conexion'] else 'ERROR'}")
    print(f"  Base de datos: {'OK' if resultados_mongo['base_datos'] else 'ERROR'}")
    print(f"  Colecciones: {'OK' if resultados_mongo['colecciones'] else 'WARNING'}")
    
    # Estado general
    pg_ok = resultados_pg['configuracion'] and resultados_pg['conexion']
    mongo_ok = resultados_mongo['configuracion'] and resultados_mongo['conexion']
    
    print("\n" + "="*70)
    if pg_ok and mongo_ok:
        print_success("TODAS LAS CONEXIONES ESTAN FUNCIONANDO CORRECTAMENTE")
        return True
    else:
        if not pg_ok:
            print_error("PostgreSQL (Neon) tiene problemas")
        if not mongo_ok:
            print_error("MongoDB tiene problemas")
        return False

if __name__ == '__main__':
    try:
        exit_code = 0 if main() else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

