#!/usr/bin/env python3
"""
Script para diagnosticar y probar los problemas específicos:
1. Menú de acciones no despliega
2. No se puede cambiar profesor asignado
3. Modal de asignar profesor no funciona (botones Cancelar/Asignar)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor
from django.urls import reverse
import json

def test_login_admin():
    """Verificar que el usuario admin puede hacer login"""
    print("=== PRUEBA 1: Login de Admin ===")
    
    client = Client()
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    if response.status_code == 302:  # Redirect después de login exitoso
        print("✓ Login exitoso")
        return client
    else:
        print("✗ Error en login")
        print(f"Status code: {response.status_code}")
        return None

def test_listar_asignaturas_view(client):
    """Probar que la vista de listar asignaturas carga correctamente"""
    print("\n=== PRUEBA 2: Vista Listar Asignaturas ===")
    
    response = client.get('/asignaturas/')
    
    if response.status_code == 200:
        print("✓ Vista carga correctamente")
        
        # Verificar que el contexto tiene los datos necesarios
        context = response.context
        if 'asignaturas' in context:
            print(f"✓ Contexto contiene {len(context['asignaturas'])} asignaturas")
        else:
            print("✗ Contexto no contiene asignaturas")
        
        if 'profesores' in context:
            print(f"✓ Contexto contiene {len(context['profesores'])} profesores")
        else:
            print("✗ Contexto no contiene profesores")
        
        # Verificar contenido HTML
        content = response.content.decode('utf-8')
        
        if 'dropdown-toggle' in content:
            print("✓ HTML contiene dropdowns")
        else:
            print("✗ HTML no contiene dropdowns")
        
        if 'modalProfesor' in content:
            print("✓ HTML contiene modal de profesor")
        else:
            print("✗ HTML no contiene modal de profesor")
        
        if 'asignarProfesor' in content:
            print("✓ HTML contiene función JavaScript asignarProfesor")
        else:
            print("✗ HTML no contiene función JavaScript asignarProfesor")
        
        return True
    else:
        print(f"✗ Error al cargar vista: {response.status_code}")
        return False

def test_ajax_asignar_profesor(client):
    """Probar la funcionalidad AJAX de asignar profesor"""
    print("\n=== PRUEBA 3: AJAX Asignar Profesor ===")
    
    # Buscar una asignatura y un profesor
    asignatura = Asignatura.objects.first()
    profesor = Profesor.objects.first()
    
    if not asignatura:
        print("✗ No hay asignaturas disponibles")
        return False
    
    if not profesor:
        print("✗ No hay profesores disponibles")
        return False
    
    print(f"Probando asignar {profesor.primer_nombre} a {asignatura.nombre}")
    
    # Hacer petición AJAX
    response = client.post(
        f'/ajax/asignar-profesor/{asignatura.id}/',
        {
            'profesor_id': profesor.id
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            if data.get('success'):
                print("✓ AJAX funciona correctamente")
                print(f"  Mensaje: {data.get('message')}")
                return True
            else:
                print("✗ AJAX retorna error:")
                print(f"  Error: {data.get('error')}")
                return False
        except json.JSONDecodeError:
            print("✗ Respuesta AJAX no es JSON válido")
            print(f"  Contenido: {response.content}")
            return False
    else:
        print(f"✗ Error HTTP en AJAX: {response.status_code}")
        return False

def test_static_files():
    """Verificar que los archivos estáticos necesarios estén disponibles"""
    print("\n=== PRUEBA 4: Archivos Estáticos ===")
    
    client = Client()
    
    # Intentar cargar Bootstrap CSS (si está servido por Django)
    try:
        response = client.get('/static/css/bootstrap.min.css')
        if response.status_code == 200:
            print("✓ Bootstrap CSS disponible")
        else:
            print("⚠ Bootstrap CSS no encontrado (puede estar en CDN)")
    except:
        print("⚠ No se puede verificar Bootstrap CSS")
    
    # Intentar cargar jQuery (si está servido por Django)
    try:
        response = client.get('/static/js/jquery.min.js')
        if response.status_code == 200:
            print("✓ jQuery disponible")
        else:
            print("⚠ jQuery no encontrado (puede estar en CDN)")
    except:
        print("⚠ No se puede verificar jQuery")

def test_template_inheritance():
    """Verificar que la herencia de templates funcione"""
    print("\n=== PRUEBA 5: Herencia de Templates ===")
    
    client = Client()
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)
    
    response = client.get('/asignaturas/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar elementos del template base
        if 'index_master.html' in content or 'bootstrap' in content.lower():
            print("✓ Template base cargado")
        else:
            print("✗ Problema con template base")
        
        # Verificar que jQuery está incluido
        if 'jquery' in content.lower():
            print("✓ jQuery incluido")
        else:
            print("✗ jQuery no incluido")
        
        # Verificar que Bootstrap está incluido
        if 'bootstrap' in content.lower():
            print("✓ Bootstrap incluido")
        else:
            print("✗ Bootstrap no incluido")
        
        return True
    else:
        print("✗ No se puede verificar herencia de templates")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("DIAGNÓSTICO DE PROBLEMAS EN GESTIÓN DE ASIGNATURAS")
    print("=" * 60)
    
    resultados = []
    
    # Test 1: Login
    client = test_login_admin()
    resultados.append(client is not None)
    
    if client:
        # Test 2: Vista principal
        resultados.append(test_listar_asignaturas_view(client))
        
        # Test 3: AJAX
        resultados.append(test_ajax_asignar_profesor(client))
        
        # Test 4: Archivos estáticos
        test_static_files()
        
        # Test 5: Templates
        resultados.append(test_template_inheritance())
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO:")
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Pruebas exitosas: {exitosas}/{total}")
    print(f"❌ Pruebas fallidas: {total - exitosas}/{total}")
    
    if exitosas == total:
        print("\n🎉 TODOS LOS COMPONENTES FUNCIONAN")
        print("El problema puede ser:")
        print("1. Versión de Bootstrap/jQuery en el template base")
        print("2. Conflictos de CSS/JavaScript")
        print("3. Cache del navegador")
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS")
        print("Revisar los errores específicos arriba")
    
    print(f"\n🔧 RECOMENDACIONES:")
    print("1. Limpiar cache del navegador (Ctrl+F5)")
    print("2. Verificar consola del navegador (F12)")
    print("3. Verificar que bootstrap.js y jquery estén cargados")
    print("4. Probar en modo incógnito")

if __name__ == '__main__':
    main()
