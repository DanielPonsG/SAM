#!/usr/bin/env python
"""
Script para probar la funcionalidad corregida de ver notas por curso y asignatura
"""

import requests
import sys

def test_notas_scenarios():
    """Probar diferentes escenarios de visualización de notas"""
    
    print("=== PRUEBA: Escenarios de Notas ===")
    
    base_url = "http://127.0.0.1:8000/notas/ver/"
    
    # Escenario 1: Solo página base
    print("\n1. Probando página base...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Página base carga correctamente")
        else:
            print(f"   ✗ Error en página base: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Escenario 2: Solo curso seleccionado (debería mostrar todas las asignaturas)
    print("\n2. Probando solo curso seleccionado...")
    try:
        url = f"{base_url}?curso_id=28"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Vista de curso completo funciona")
            if "Todas las Asignaturas" in response.text:
                print("   ✓ Mensaje de curso completo presente")
        else:
            print(f"   ✗ Error en vista de curso: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Escenario 3: Curso y asignatura seleccionados (el que causaba error)
    print("\n3. Probando curso + asignatura...")
    try:
        url = f"{base_url}?curso_id=28&asignatura_id=64"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Vista de asignatura específica funciona")
            if "agregar-btn" in response.text:
                print("   ✓ Botones de agregar presentes")
        else:
            print(f"   ✗ Error en vista de asignatura: {response.status_code}")
            if response.status_code == 500:
                print("   ✗ Error interno del servidor")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Escenario 4: Múltiples parámetros (URL que causaba el error original)
    print("\n4. Probando URL con múltiples parámetros...")
    try:
        url = f"{base_url}?curso_id=28&asignatura_id=64&curso_id=28"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ URL con parámetros duplicados funciona")
        else:
            print(f"   ✗ Error con parámetros duplicados: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_notas_scenarios()
