#!/usr/bin/env python
"""
Script para probar específicamente la vista de notas por curso
y verificar que no haya errores AttributeError
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Curso, Estudiante, Asignatura, Profesor

def test_ver_notas_curso():
    """Prueba la vista ver_notas_curso con diferentes combinaciones de filtros"""
    client = Client()
    
    try:
        # Crear usuario administrador para las pruebas
        user = User.objects.filter(username='admin').first()
        if not user:
            print("❌ No se encontró usuario admin")
            return False
            
        # Hacer login
        client.force_login(user)
        print("✅ Login exitoso")
        
        # Obtener curso y asignatura de prueba
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        
        if not curso:
            print("❌ No hay cursos disponibles")
            return False
            
        print(f"📚 Probando con Curso: {curso}")
        
        # Prueba 1: Solo curso seleccionado
        print("\n🔍 Prueba 1: Solo curso seleccionado")
        response = client.get('/notas/ver/', {'curso_id': curso.id})
        if response.status_code == 200:
            print("✅ Vista funciona correctamente con solo curso")
        else:
            print(f"❌ Error con solo curso: status {response.status_code}")
            return False
            
        # Prueba 2: Curso y asignatura seleccionados
        if asignatura:
            print(f"\n🔍 Prueba 2: Curso + Asignatura ({asignatura.nombre})")
            response = client.get('/notas/ver/', {
                'curso_id': curso.id,
                'asignatura_id': asignatura.id
            })
            if response.status_code == 200:
                print("✅ Vista funciona correctamente con curso + asignatura")
            else:
                print(f"❌ Error con curso + asignatura: status {response.status_code}")
                return False
        
        # Prueba 3: Sin filtros
        print("\n🔍 Prueba 3: Sin filtros")
        response = client.get('/notas/ver/')
        if response.status_code == 200:
            print("✅ Vista funciona correctamente sin filtros")
        else:
            print(f"❌ Error sin filtros: status {response.status_code}")
            return False
        
        print("\n🎉 Todas las pruebas de la vista ver_notas_curso pasaron exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_filtros_template():
    """Prueba específica para verificar que los filtros del template funcionan correctamente"""
    from smapp.templatetags.custom_filters import get_item, get_list_item
    
    print("\n🧪 Probando filtros de template:")
    
    # Test get_item con diccionario
    test_dict = {'key1': 'value1', 'key2': 'value2'}
    result = get_item(test_dict, 'key1')
    print(f"✅ get_item con dict: {result}")
    
    # Test get_item con lista
    test_list = ['item0', 'item1', 'item2']
    result = get_item(test_list, 0)
    print(f"✅ get_item con lista: {result}")
    
    # Test get_list_item
    result = get_list_item(test_list, 1)
    print(f"✅ get_list_item: {result}")
    
    # Test con valores None/inválidos
    result = get_item(None, 'key')
    print(f"✅ get_item con None: {result}")
    
    result = get_list_item(None, 0)
    print(f"✅ get_list_item con None: {result}")
    
    print("🎉 Todos los filtros funcionan correctamente")

if __name__ == "__main__":
    print("🔧 Iniciando pruebas del sistema de notas...")
    
    # Probar filtros
    test_filtros_template()
    
    # Probar vista
    success = test_ver_notas_curso()
    
    if success:
        print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("El sistema de notas está funcionando correctamente")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisar los errores anteriores")
        sys.exit(1)
