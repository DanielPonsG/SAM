#!/usr/bin/env python3
"""
Script para probar permisos corregidos del administrador
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
from smapp.models import Perfil

def test_admin_permisos_completos():
    """Probar todos los permisos de administrador"""
    
    print("=== PRUEBA DE PERMISOS COMPLETOS PARA ADMINISTRADOR ===\n")
    
    client = Client()
    
    # Login como admin
    login_result = client.login(username='admin', password='admin123')
    if not login_result:
        print("❌ Error en login")
        return
    print("✅ Login exitoso como admin")
    
    # Verificar perfil
    admin_user = User.objects.get(username='admin')
    perfil = Perfil.objects.get(user=admin_user)
    print(f"✅ Tipo de usuario: {perfil.tipo_usuario}")
    
    # Probar todas las funcionalidades que debería tener acceso
    funcionalidades = [
        ('/agregar?tipo=estudiante', 'Agregar Estudiante'),
        ('/agregar?tipo=profesor', 'Agregar Profesor'),
        ('/modificar?tipo=estudiante', 'Modificar Estudiante'),
        ('/modificar?tipo=profesor', 'Modificar Profesor'),
        ('/eliminar?tipo=estudiante', 'Eliminar Estudiante'),
        ('/eliminar?tipo=profesor', 'Eliminar Profesor'),
        ('/estudiantes/listar/', 'Listar Estudiantes'),
        ('/profesores/', 'Listar Profesores'),
        ('/profesores/agregar/', 'Gestionar Profesores'),
        ('/notas/ingresar/', 'Ingresar Notas'),
        ('/notas/ver/', 'Ver Notas'),
        ('/cursos/', 'Gestión de Cursos'),
        ('/asignaturas/', 'Gestión de Asignaturas'),
    ]
    
    resultados = []
    
    for url, nombre in funcionalidades:
        try:
            response = client.get(url, follow=True)
            if response.status_code == 200:
                resultados.append((nombre, "✅ ACCESIBLE"))
                print(f"✅ {nombre}: Accesible")
            elif response.status_code == 403:
                resultados.append((nombre, "❌ PROHIBIDO"))
                print(f"❌ {nombre}: Prohibido")
            else:
                resultados.append((nombre, f"⚠ Error {response.status_code}"))
                print(f"⚠ {nombre}: Error {response.status_code}")
        except Exception as e:
            resultados.append((nombre, f"❌ Error: {e}"))
            print(f"❌ {nombre}: Error - {e}")
    
    # Probar POST en ingresar notas
    print(f"\n--- PRUEBA DE INGRESO DE NOTAS ---")
    try:
        # Primero GET para ver grupos disponibles
        response = client.get('/notas/ingresar/', follow=True)
        if response.status_code == 200:
            print("✅ Página de ingresar notas accesible")
            
            # Simular POST de notas vacío para probar redirección
            response = client.post('/notas/ingresar/', {
                'grupo_id': '1',  # Asumiendo que existe grupo con ID 1
            }, follow=True)
            
            if response.status_code == 200:
                print("✅ POST en ingresar notas funciona")
                
                # Verificar si hay redirección
                if hasattr(response, 'redirect_chain') and response.redirect_chain:
                    print(f"✅ Redirección funcionando: {response.redirect_chain}")
                else:
                    print("⚠ No hay redirección después del POST")
            else:
                print(f"❌ Error en POST de ingresar notas: {response.status_code}")
        else:
            print("❌ No se puede acceder a ingresar notas")
    except Exception as e:
        print(f"❌ Error en prueba de ingreso de notas: {e}")
    
    print(f"\n=== RESUMEN DE RESULTADOS ===")
    accesibles = sum(1 for _, resultado in resultados if "✅" in resultado)
    prohibidos = sum(1 for _, resultado in resultados if "❌" in resultado)
    errores = sum(1 for _, resultado in resultados if "⚠" in resultado)
    
    print(f"✅ Funcionalidades accesibles: {accesibles}")
    print(f"❌ Funcionalidades prohibidas: {prohibidos}")
    print(f"⚠ Errores: {errores}")
    
    if prohibidos == 0:
        print("\n🎉 ¡TODOS LOS PERMISOS FUNCIONAN CORRECTAMENTE!")
        print("🎯 El administrador tiene acceso completo al sistema")
    else:
        print("\n⚠ Aún hay funcionalidades restringidas que necesitan corrección")

if __name__ == '__main__':
    test_admin_permisos_completos()
