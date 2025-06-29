#!/usr/bin/env python3
"""
Script para verificar usuarios y permisos en el sistema
"""

import os
import sys

# Configurar Django ANTES de importar cualquier cosa
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
sys.path.append('.')

import django
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil

def verificar_usuarios():
    """Verificar usuarios y sus permisos"""
    
    print("=== VERIFICACIÓN DE USUARIOS Y PERMISOS ===\n")
    
    # Listar todos los usuarios
    usuarios = User.objects.all()
    print(f"Total de usuarios en el sistema: {usuarios.count()}\n")
    
    for user in usuarios:
        print(f"--- Usuario: {user.username} ---")
        print(f"Email: {user.email}")
        print(f"Nombre completo: {user.get_full_name()}")
        print(f"Es activo: {user.is_active}")
        print(f"Es staff: {user.is_staff}")
        print(f"Es superuser: {user.is_superuser}")
        
        # Verificar perfil
        try:
            perfil = Perfil.objects.get(user=user)
            print(f"Tipo de usuario: {perfil.tipo_usuario}")
            print(f"Perfil activo: {perfil.activo if hasattr(perfil, 'activo') else 'N/A'}")
        except Perfil.DoesNotExist:
            print("❌ NO TIENE PERFIL ASIGNADO")
        
        print("-" * 40)
    
    # Verificar usuario admin específicamente
    print("\n=== VERIFICACIÓN ESPECÍFICA DEL ADMIN ===")
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✓ Usuario admin encontrado")
        print(f"Password válido: {admin_user.check_password('admin123')}")
        
        try:
            admin_perfil = Perfil.objects.get(user=admin_user)
            print(f"✓ Perfil encontrado: {admin_perfil.tipo_usuario}")
            
            # Verificar si puede acceder a las vistas
            from django.test import Client
            client = Client()
            
            # Test login
            login_result = client.login(username='admin', password='admin123')
            print(f"Login exitoso: {login_result}")
            
            if login_result:
                # Test acceso a páginas
                response = client.get('/notas/ver/', follow=True)
                print(f"Acceso a ver notas: {response.status_code == 200}")
                
                response = client.get('/notas/ingresar/', follow=True)
                print(f"Acceso a ingresar notas: {response.status_code == 200}")
                
        except Perfil.DoesNotExist:
            print("❌ Admin no tiene perfil - CREANDO PERFIL...")
            perfil = Perfil.objects.create(
                user=admin_user,
                tipo_usuario='administrador'
            )
            print(f"✓ Perfil creado: {perfil.tipo_usuario}")
            
    except User.DoesNotExist:
        print("❌ Usuario admin no existe - CREANDO USUARIO...")
        admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@sma.cl',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        # Crear perfil
        perfil = Perfil.objects.create(
            user=admin_user,
            tipo_usuario='administrador'
        )
        print(f"✓ Usuario admin creado con perfil: {perfil.tipo_usuario}")

if __name__ == '__main__':
    verificar_usuarios()
