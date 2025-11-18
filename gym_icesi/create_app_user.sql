-- ============================================================
-- Script para crear usuario dedicado de la aplicación
-- Gym Icesi - Base de Datos Relacional
-- ============================================================
-- 
-- Este script crea un usuario específico para la aplicación
-- con los permisos necesarios para operar la base de datos.
--
-- USO:
-- 1. Ejecuta este script en la consola SQL de Neon
-- 2. Reemplaza 'tu_contraseña_segura' con una contraseña fuerte
-- 3. Actualiza las variables DB_USER y DB_PASSWORD en .env
-- ============================================================

-- Crear usuario para la aplicación
CREATE USER gym_app_user WITH PASSWORD 'tu_contraseña_segura';

-- Otorgar permisos en la base de datos actual
-- (Asegúrate de estar conectado a la base de datos correcta)
GRANT ALL PRIVILEGES ON DATABASE neondb TO gym_app_user;

-- Conectarse a la base de datos (esto se ejecuta automáticamente en Neon)
-- \c neondb

-- Otorgar permisos en el esquema público
GRANT ALL PRIVILEGES ON SCHEMA public TO gym_app_user;

-- Otorgar permisos en todas las tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gym_app_user;

-- Otorgar permisos en todas las secuencias (para auto-increment)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gym_app_user;

-- Configurar permisos por defecto para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gym_app_user;

-- Configurar permisos por defecto para secuencias futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gym_app_user;

-- Verificar que el usuario fue creado
SELECT 
    usename as username,
    usecreatedb as can_create_db,
    usesuper as is_superuser
FROM pg_user
WHERE usename = 'gym_app_user';

-- ============================================================
-- NOTAS:
-- 
-- 1. Reemplaza 'tu_contraseña_segura' con una contraseña fuerte
--    Ejemplo: 'GymIcesi2025!SecurePass'
--
-- 2. Si tu base de datos tiene otro nombre, reemplaza 'neondb'
--
-- 3. Después de ejecutar este script, actualiza tu .env:
--    DB_USER=gym_app_user
--    DB_PASSWORD=tu_contraseña_segura
--
-- 4. Para desarrollo, puedes usar el usuario principal de Neon
--    sin necesidad de crear un usuario dedicado
-- ============================================================

