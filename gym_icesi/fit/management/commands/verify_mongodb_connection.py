"""
Comando para verificar la conexión a MongoDB
Uso: python manage.py verify_mongodb_connection
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from fit.mongodb_service import MongoDBService


class Command(BaseCommand):
    help = 'Verifica la conexión a MongoDB Atlas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Verificando conexion a MongoDB...\n'))
        
        # Verificar configuración
        self._verify_config()
        
        # Verificar conexión
        self._verify_connection()
        
        # Verificar colecciones
        self._verify_collections()
        
        self.stdout.write(self.style.SUCCESS('\nVerificacion completada!'))
    
    def _verify_config(self):
        """Verifica la configuración de MongoDB"""
        self.stdout.write('Verificando configuracion...')
        
        mongodb_enabled = getattr(settings, 'MONGODB_ENABLED', False)
        if not mongodb_enabled:
            self.stdout.write(self.style.WARNING('  [WARNING] MongoDB esta deshabilitado'))
            self.stdout.write(self.style.WARNING('     [TIP] Configura MONGODB_ENABLED=True en .env'))
            return False
        
        self.stdout.write(self.style.SUCCESS('  [OK] MongoDB habilitado'))
        
        mongodb_settings = getattr(settings, 'MONGODB_SETTINGS', {})
        self.stdout.write(f'  Host: {mongodb_settings.get("host", "N/A")}')
        self.stdout.write(f'  Database: {mongodb_settings.get("db", "N/A")}')
        self.stdout.write(f'  User: {mongodb_settings.get("username", "N/A")}')
        
        return True
    
    def _verify_connection(self):
        """Verifica la conexión a MongoDB"""
        self.stdout.write('\nVerificando conexion...')
        
        if not MongoDBService.is_available():
            self.stdout.write(self.style.ERROR('  [ERROR] MongoDB no esta disponible'))
            self.stdout.write(self.style.WARNING('  [TIP] Verifica:'))
            self.stdout.write(self.style.WARNING('     - Credenciales en .env'))
            self.stdout.write(self.style.WARNING('     - IP allowlist en MongoDB Atlas'))
            self.stdout.write(self.style.WARNING('     - Connection string correcta'))
            return False
        
        try:
            db = MongoDBService.get_db()
            if db is None:
                self.stdout.write(self.style.ERROR('  [ERROR] No se pudo obtener la base de datos'))
                return False
            
            # Hacer un ping
            client = MongoDBService.get_client()
            client.admin.command('ping')
            
            self.stdout.write(self.style.SUCCESS('  [OK] Conexion exitosa'))
            
            # Obtener información del servidor
            server_info = client.server_info()
            self.stdout.write(f'  Version: {server_info.get("version", "N/A")}')
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error de conexion: {e}'))
            return False
    
    def _verify_collections(self):
        """Verifica las colecciones principales"""
        self.stdout.write('\nVerificando colecciones...')
        
        if not MongoDBService.is_available():
            return
        
        try:
            db = MongoDBService.get_db()
            if db is None:
                return
            
            # Colecciones esperadas
            expected_collections = [
                'progress_logs',
                'exercise_details',
                'user_routines',
                'routine_templates',
                'trainer_assignments',
                'user_activity_logs'
            ]
            
            existing_collections = db.list_collection_names()
            
            for collection in expected_collections:
                if collection in existing_collections:
                    count = db[collection].count_documents({})
                    self.stdout.write(self.style.SUCCESS(f'  [OK] {collection}: {count} documentos'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [WARNING] {collection}: No existe (se creara automaticamente)'))
            
            if not existing_collections:
                self.stdout.write(self.style.WARNING('  [INFO] No hay colecciones aun. Se crearan cuando uses la aplicacion.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error verificando colecciones: {e}'))

