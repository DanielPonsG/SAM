#!/usr/bin/env python
"""
Script para configurar usuarios de prueba con contraseñas conocidas
"""

import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil

def configurar_usuarios_prueba():
    """Configurar usuarios de prueba con contraseñas conocidas"""
    print("🔐 CONFIGURANDO USUARIOS DE PRUEBA")
    print("=" * 50)
    
    # Usuarios de prueba con contraseñas conocidas
    usuarios_prueba = [
        {
            'username': 'admin_demo',
            'password': 'admin123',
            'tipo': 'director',
            'email': 'admin@demo.com',
            'first_name': 'Admin',
            'last_name': 'Demo'
        },
        {
            'username': 'profesor_demo',
            'password': 'prof123',
            'tipo': 'profesor',
            'email': 'profesor@demo.com',
            'first_name': 'Profesor',
            'last_name': 'Demo'
        },
        {
            'username': 'alumno_demo',
            'password': 'alumno123',
            'tipo': 'alumno',
            'email': 'alumno@demo.com',
            'first_name': 'Alumno',
            'last_name': 'Demo'
        }
    ]
    
    for user_data in usuarios_prueba:
        # Crear o actualizar usuario
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_active': True
            }
        )
        
        # Establecer contraseña
        user.set_password(user_data['password'])
        user.save()
        
        # Crear o actualizar perfil
        perfil, perfil_created = Perfil.objects.get_or_create(
            user=user,
            defaults={'tipo_usuario': user_data['tipo']}
        )
        
        if not perfil_created:
            perfil.tipo_usuario = user_data['tipo']
            perfil.save()
        
        status = "creado" if created else "actualizado"
        print(f"✓ Usuario {status}: {user_data['username']} ({user_data['tipo']})")
        print(f"  - Email: {user_data['email']}")
        print(f"  - Password: {user_data['password']}")
    
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("-" * 30)
    for user_data in usuarios_prueba:
        print(f"{user_data['tipo'].upper()}: {user_data['username']} / {user_data['password']}")
    
    print("\n🌐 URL de acceso: http://127.0.0.1:8000/login/")
    print("✅ Usuarios de prueba configurados correctamente")

if __name__ == '__main__':
    configurar_usuarios_prueba()
