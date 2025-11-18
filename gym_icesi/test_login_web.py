#!/usr/bin/env python
"""
Script para probar el login exactamente como lo hace el formulario web
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymsid.settings')
django.setup()

from django.contrib.auth import authenticate
from django.test import RequestFactory
from fit.auth_backend import InstitutionalBackend

def test_login(username, password):
    print(f"\n{'='*60}")
    print(f"Probando login: {username} / {password}")
    print('='*60)
    
    # Simular request
    factory = RequestFactory()
    request = factory.post('/login/', {
        'username': username,
        'password': password
    })
    
    # Probar autenticación directamente
    print("\n1. Probando authenticate() directamente...")
    user = authenticate(request=request, username=username, password=password)
    
    if user:
        print(f"   [OK] Usuario autenticado: {user.username}")
        print(f"   - is_staff: {user.is_staff}")
        print(f"   - is_superuser: {user.is_superuser}")
        print(f"   - is_active: {user.is_active}")
    else:
        print(f"   [ERROR] Autenticación fallida")
    
    # Probar backend directamente
    print("\n2. Probando InstitutionalBackend directamente...")
    backend = InstitutionalBackend()
    user2 = backend.authenticate(request=request, username=username, password=password)
    
    if user2:
        print(f"   [OK] Usuario autenticado por backend: {user2.username}")
    else:
        print(f"   [ERROR] Backend retornó None")
    
    return user is not None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBA DE LOGIN (Simulando formulario web)")
    print("="*60)
    
    # Probar usuarios
    usuarios = [
        ('laura.h', 'lh123'),
        ('paula.r', 'pr123'),
        ('admin', 'admin123'),
    ]
    
    resultados = []
    for username, password in usuarios:
        resultado = test_login(username, password)
        resultados.append((username, resultado))
    
    # Resumen
    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    for username, resultado in resultados:
        if resultado:
            print(f"[OK] {username}: Login exitoso")
        else:
            print(f"[ERROR] {username}: Login fallido")
    print("="*60 + "\n")

