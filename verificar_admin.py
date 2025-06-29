#!/usr/bin/env python
"""
Script para verificar el login y crear un usuario admin si no existe
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User

def verificar_admin():
    print("🔐 VERIFICACIÓN DE USUARIO ADMINISTRADOR")
    print("=" * 50)
    
    # Verificar si existe un admin
    admins = User.objects.filter(is_superuser=True)
    
    if admins.exists():
        print("✅ Se encontraron usuarios administradores:")
        for admin in admins:
            print(f"   - Usuario: {admin.username}")
            print(f"   - Email: {admin.email}")
            print(f"   - Activo: {'Sí' if admin.is_active else 'No'}")
            print()
    else:
        print("❌ No se encontraron usuarios administradores")
        
        # Crear usuario admin
        respuesta = input("¿Quieres crear un usuario admin? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            username = input("Nombre de usuario (admin): ") or "admin"
            password = input("Contraseña (admin): ") or "admin"
            email = input("Email (admin@test.com): ") or "admin@test.com"
            
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            print(f"✅ Usuario administrador creado: {admin.username}")
            print(f"   Usa estas credenciales para hacer login:")
            print(f"   Usuario: {username}")
            print(f"   Contraseña: {password}")
    
    print("\n🌐 INSTRUCCIONES DE LOGIN:")
    print("1. Ve a: http://127.0.0.1:8000/login/")
    print("2. Ingresa las credenciales del administrador")
    print("3. Una vez logueado, ve a: http://127.0.0.1:8000/calendario/")
    print("4. Ya podrás crear eventos y usar todas las funcionalidades")
    
    print("\n🔧 SI TIENES PROBLEMAS:")
    print("- Verifica que el servidor esté ejecutándose: python manage.py runserver")
    print("- Abre las herramientas de desarrollador (F12) para ver errores")
    print("- Asegúrate de estar logueado antes de ir al calendario")

if __name__ == '__main__':
    verificar_admin()
