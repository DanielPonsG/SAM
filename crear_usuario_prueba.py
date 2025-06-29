#!/usr/bin/env python3
"""
Script para crear un usuario de prueba y validar el sistema.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from smapp.models import Perfil
from django.utils import timezone

def crear_usuario_prueba():
    """Crea un usuario de prueba y valida el login"""
    print("=== CREANDO USUARIO DE PRUEBA ===\n")
    
    # Eliminar usuario de prueba anterior si existe
    try:
        User.objects.filter(username='test_admin').delete()
        print("✅ Usuario de prueba anterior eliminado")
    except:
        pass
    
    # Crear nuevo usuario
    try:
        user = User.objects.create_user(
            username='test_admin',
            password='test123',
            email='test@example.com',
            first_name='Test',
            last_name='Admin',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuario creado: {user.username}")
        
        # Crear perfil
        perfil = Perfil.objects.create(
            user=user,
            tipo_usuario='director'  # director está en las opciones del modelo
        )
        print(f"✅ Perfil creado: {perfil.tipo_usuario}")
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return
    
    # Probar login
    print("\n=== PROBANDO LOGIN ===")
    client = Client()
    
    # Probar login
    login_data = {
        'username': 'test_admin',
        'password': 'test123'
    }
    
    response = client.post('/login/', login_data)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect después de login exitoso
        print("✅ Login exitoso (redirect detectado)")
        
        # Probar acceso a páginas protegidas
        print("\n=== PROBANDO PÁGINAS PROTEGIDAS ===")
        
        # Listar cursos
        response = client.get('/cursos/')
        print(f"Listar cursos: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Seleccionar curso horarios
        response = client.get('/horarios/')
        print(f"Seleccionar curso horarios: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Index
        response = client.get('/')
        print(f"Página principal: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
    else:
        print(f"❌ Error en login: {response.status_code}")
        print("Contenido de respuesta:", response.content.decode('utf-8')[:500])

if __name__ == '__main__':
    crear_usuario_prueba()
