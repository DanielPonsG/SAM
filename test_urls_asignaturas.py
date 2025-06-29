#!/usr/bin/env python3
"""
Script para probar las URLs de asignaturas y verificar si funcionan correctamente.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.urls import reverse
from smapp.models import Asignatura

def test_urls_asignaturas():
    """Probar las URLs relacionadas con asignaturas"""
    print("=== TEST URLs ASIGNATURAS ===")
    
    # Probar URL para listar asignaturas
    try:
        url_listar = reverse('listar_asignaturas')
        print(f"✓ URL listar asignaturas: {url_listar}")
    except Exception as e:
        print(f"✗ Error URL listar asignaturas: {e}")
    
    # Probar URL para agregar asignatura
    try:
        url_agregar = reverse('agregar_asignatura')
        print(f"✓ URL agregar asignatura: {url_agregar}")
    except Exception as e:
        print(f"✗ Error URL agregar asignatura: {e}")
    
    # Probar URL para editar asignatura (necesita ID)
    asignaturas = Asignatura.objects.all()[:3]  # Primeras 3 asignaturas
    
    if asignaturas:
        for asignatura in asignaturas:
            try:
                url_editar = reverse('editar_asignatura', args=[asignatura.id])
                print(f"✓ URL editar asignatura ID {asignatura.id}: {url_editar}")
            except Exception as e:
                print(f"✗ Error URL editar asignatura ID {asignatura.id}: {e}")
                
            try:
                url_eliminar = reverse('eliminar_asignatura', args=[asignatura.id])
                print(f"✓ URL eliminar asignatura ID {asignatura.id}: {url_eliminar}")
            except Exception as e:
                print(f"✗ Error URL eliminar asignatura ID {asignatura.id}: {e}")
    else:
        print("- No hay asignaturas en la base de datos para probar")

def listar_asignaturas_disponibles():
    """Listar asignaturas disponibles en la base de datos"""
    print("\n=== ASIGNATURAS DISPONIBLES ===")
    
    asignaturas = Asignatura.objects.all()
    
    if asignaturas:
        for asignatura in asignaturas:
            print(f"ID: {asignatura.id} - Código: {asignatura.codigo_asignatura} - Nombre: {asignatura.nombre}")
    else:
        print("No hay asignaturas registradas en la base de datos")
        print("Intenta crear algunas asignaturas primero")

if __name__ == "__main__":
    print("Probando URLs de asignaturas...")
    test_urls_asignaturas()
    listar_asignaturas_disponibles()
    print("\n¡Pruebas completadas!")
