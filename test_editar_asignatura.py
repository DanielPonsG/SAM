#!/usr/bin/env python3
"""
Script para probar el acceso a la vista de editar asignatura
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Estudiante, Profesor, Asignatura

def test_editar_asignatura():
    """Probar el acceso a la vista de editar asignatura"""
    print("=== TEST EDITAR ASIGNATURA ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # Verificar que exista al menos una asignatura
    asignatura = Asignatura.objects.first()
    if not asignatura:
        print("✗ No hay asignaturas en la base de datos")
        return
    
    print(f"Probando con asignatura: {asignatura.nombre} (ID: {asignatura.id})")
    
    # Probar sin login (debería redirigir)
    url = f'/asignaturas/editar/{asignatura.id}/'
    response = client.get(url)
    print(f"Sin login - Status: {response.status_code}")
    
    # Crear usuario administrador de prueba si no existe
    try:
        admin_user = User.objects.get(username='admin_test')
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin_test',
            password='admin123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        print("✓ Usuario admin creado")
    
    # Login como admin
    login_success = client.login(username='admin_test', password='admin123')
    if login_success:
        print("✓ Login exitoso")
        
        # Probar acceso a editar asignatura
        response = client.get(url)
        print(f"Con login admin - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Acceso exitoso a editar asignatura")
        elif response.status_code == 403:
            print("✗ Acceso denegado (problema de permisos)")
        elif response.status_code == 404:
            print("✗ Página no encontrada")
        else:
            print(f"✗ Error inesperado: {response.status_code}")
    else:
        print("✗ Error en login")

def verificar_usuarios_con_permisos():
    """Verificar qué usuarios tienen permisos de administrador"""
    print("\n=== USUARIOS CON PERMISOS ===")
    
    # Usuarios Django con permisos de staff/superuser
    admins = User.objects.filter(is_staff=True)
    print(f"Usuarios con is_staff=True: {admins.count()}")
    for admin in admins:
        print(f"  - {admin.username} (staff: {admin.is_staff}, super: {admin.is_superuser})")
    
    # Profesores con tipo 'director'
    try:
        directores = Profesor.objects.filter(user__isnull=False)
        print(f"Profesores registrados: {directores.count()}")
        for director in directores:
            print(f"  - {director.user.username} - {director.get_nombre_completo()}")
    except Exception as e:
        print(f"Error obteniendo profesores: {e}")

if __name__ == "__main__":
    print("Probando acceso a editar asignatura...")
    test_editar_asignatura()
    verificar_usuarios_con_permisos()
    print("\n¡Pruebas completadas!")
