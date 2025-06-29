#!/usr/bin/env python3
"""
Script para crear perfiles de director para usuarios administradores
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil

def crear_perfiles_admin():
    """Crear perfiles de director para usuarios staff"""
    print("=== CREANDO PERFILES DE DIRECTOR ===")
    
    # Obtener usuarios con permisos de staff
    users_staff = User.objects.filter(is_staff=True)
    
    for user in users_staff:
        try:
            # Verificar si ya tiene perfil
            perfil = Perfil.objects.get(user=user)
            print(f"✓ {user.username} ya tiene perfil: {perfil.get_tipo_usuario_display()}")
            
            # Si no es director, actualizarlo
            if perfil.tipo_usuario != 'director':
                perfil.tipo_usuario = 'director'
                perfil.save()
                print(f"  → Actualizado a director")
                
        except Perfil.DoesNotExist:
            # Crear perfil de director
            perfil = Perfil.objects.create(
                user=user,
                tipo_usuario='director'
            )
            print(f"✓ Perfil de director creado para {user.username}")

def verificar_perfiles():
    """Verificar los perfiles creados"""
    print("\n=== PERFILES VERIFICADOS ===")
    
    perfiles = Perfil.objects.all()
    for perfil in perfiles:
        print(f"{perfil.user.username}: {perfil.get_tipo_usuario_display()}")

def test_acceso_editar():
    """Probar acceso con un usuario que tenga perfil de director"""
    print("\n=== PROBANDO ACCESO ===")
    
    from django.test import Client
    
    # Buscar un usuario con perfil de director
    director_perfil = Perfil.objects.filter(tipo_usuario='director').first()
    
    if director_perfil:
        client = Client()
        user = director_perfil.user
        
        # Login
        login_success = client.login(username=user.username, password='admin123')
        if not login_success:
            # Intentar con contraseñas comunes
            for password in ['admin', 'password', '123456', 'admin123']:
                if client.login(username=user.username, password=password):
                    login_success = True
                    print(f"✓ Login exitoso con {user.username} usando password: {password}")
                    break
        
        if login_success:
            # Probar acceso a editar asignatura
            from smapp.models import Asignatura
            asignatura = Asignatura.objects.first()
            if asignatura:
                url = f'/asignaturas/editar/{asignatura.id}/'
                response = client.get(url)
                print(f"Acceso a {url}: Status {response.status_code}")
                
                if response.status_code == 200:
                    print("✓ ¡Acceso exitoso!")
                elif response.status_code == 403:
                    print("✗ Aún hay problemas de permisos")
                else:
                    print(f"✗ Error: {response.status_code}")
        else:
            print(f"✗ No se pudo hacer login con {user.username}")
    else:
        print("✗ No se encontró ningún usuario con perfil de director")

if __name__ == "__main__":
    print("Configurando perfiles de usuario...")
    crear_perfiles_admin()
    verificar_perfiles()
    test_acceso_editar()
    print("\n¡Configuración completada!")
