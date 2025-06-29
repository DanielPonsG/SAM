#!/usr/bin/env python3
"""
Script para probar los errores en templates de editar y eliminar notas
"""

import os
import sys

# Configurar Django ANTES de importar cualquier cosa
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
sys.path.append('.')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

from smapp.models import Calificacion, Perfil

def test_errores_templates():
    """Probar acceso a templates que fallan"""
    
    client = Client()
    
    print("=== PROBANDO ERRORES EN TEMPLATES ===\n")
    
    # Conseguir usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✓ Usuario admin encontrado: {admin_user.username}")
    except User.DoesNotExist:
        print("✗ No se encontró usuario admin")
        return
    
    # Login como admin
    client.force_login(admin_user)
    print("✓ Login como admin exitoso")
    
    # Conseguir una nota para probar
    try:
        nota = Calificacion.objects.first()
        if not nota:
            print("✗ No hay notas en la base de datos")
            return
        print(f"✓ Nota encontrada: {nota.nombre_evaluacion} (ID: {nota.id})")
    except Exception as e:
        print(f"✗ Error al obtener nota: {e}")
        return
    
    # Test 1: Ver notas curso
    print("\n--- Test 1: Ver notas curso ---")
    try:
        response = client.get('/notas/ver/', follow=True)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Ver notas curso funciona")
            if 'NoReverseMatch' in response.content.decode():
                print("✗ Error de URL encontrado en la respuesta")
            else:
                print("✓ No hay errores de URL en la respuesta")
        else:
            print(f"✗ Error en ver notas curso")
            print("Redirects:", response.redirect_chain)
    except Exception as e:
        print(f"✗ Error en ver notas curso: {e}")
    
    # Test 2: Editar nota
    print("\n--- Test 2: Editar nota ---")
    try:
        response = client.get(f'/notas/editar/{nota.id}/', follow=True)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Editar nota funciona")
            if 'NoReverseMatch' in response.content.decode():
                print("✗ Error de URL encontrado en la respuesta")
            else:
                print("✓ No hay errores de URL en la respuesta")
        else:
            print(f"✗ Error en editar nota")
            print("Redirects:", response.redirect_chain)
    except Exception as e:
        print(f"✗ Error en editar nota: {e}")
    
    # Test 3: Eliminar nota
    print("\n--- Test 3: Eliminar nota ---")
    try:
        response = client.get(f'/notas/eliminar/{nota.id}/', follow=True)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Eliminar nota funciona")
            if 'NoReverseMatch' in response.content.decode():
                print("✗ Error de URL encontrado en la respuesta")
            else:
                print("✓ No hay errores de URL en la respuesta")
        else:
            print(f"✗ Error en eliminar nota")
            print("Redirects:", response.redirect_chain)
    except Exception as e:
        print(f"✗ Error en eliminar nota: {e}")
    
    # Test 4: Ingresar notas
    print("\n--- Test 4: Ingresar notas ---")
    try:
        response = client.get('/notas/ingresar/', follow=True)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("✓ Ingresar notas funciona")
            if 'NoReverseMatch' in response.content.decode():
                print("✗ Error de URL encontrado en la respuesta")
            else:
                print("✓ No hay errores de URL en la respuesta")
        else:
            print(f"✗ Error en ingresar notas")
            print("Redirects:", response.redirect_chain)
    except Exception as e:
        print(f"✗ Error en ingresar notas: {e}")

if __name__ == '__main__':
    test_errores_templates()
