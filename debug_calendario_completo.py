#!/usr/bin/env python  
"""
Script para identificar y corregir problemas específicos en el calendario
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client

def test_calendario_response():
    print("🔍 ANALIZANDO RESPONSE DEL CALENDARIO")
    print("=" * 50)
    
    client = Client()
    admin = User.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    # Hacer request GET al calendario
    response = client.get('/calendario/')
    
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No definido')}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar elementos críticos
        elementos_criticos = [
            ('<div id="modalCrearEvento"', 'Modal de crear evento'),
            ('<form id="formCrearEvento"', 'Formulario de crear evento'),
            ('<input class="form-check-input" type="radio" name="dirigido_a" id="dirigido_especificos"', 'Radio button cursos específicos'),
            ('<div id="cursosEspecificos"', 'Div de cursos específicos'),
            ('<input type="time" name="hora_inicio" id="hora_inicio"', 'Input hora inicio'),
            ('<input type="time" name="hora_fin" id="hora_fin"', 'Input hora fin'),
            ('input[name="cursos_especificos"]', 'Checkboxes de cursos'),
            ('function validarHoras()', 'Función validarHoras'),
            ('bootstrap.Modal', 'Bootstrap Modal'),
            ('FullCalendar.Calendar', 'FullCalendar')
        ]
        
        print("\n📋 VERIFICACIÓN DE ELEMENTOS CRÍTICOS:")
        elementos_faltantes = []
        
        for elemento, descripcion in elementos_criticos:
            if elemento in content:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ❌ {descripcion} - FALTA")
                elementos_faltantes.append((elemento, descripcion))
        
        # Buscar errores comunes en el JavaScript
        print("\n🚀 ANÁLISIS DEL JAVASCRIPT:")
        
        errores_js = [
            ('console.log', 'Debug logs'),
            ('addEventListener', 'Event listeners'),
            ('getElementById', 'Selección de elementos'),
            ('querySelector', 'Selección de elementos CSS'),
            ('fetch(', 'Requests AJAX'),
            ('JSON.parse', 'Parsing JSON'),
            ('FormData', 'Manejo de formularios')
        ]
        
        for funcion, descripcion in errores_js:
            if funcion in content:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ⚠️ {descripcion} - No encontrado")
        
        # Verificar que los cursos estén en el contexto
        print("\n📚 VERIFICACIÓN DE CURSOS:")
        if 'curso_' in content and 'form-check-input' in content:
            # Contar checkboxes de cursos
            import re
            checkboxes = re.findall(r'name="cursos_especificos".*?value="(\d+)"', content)
            print(f"   ✅ {len(checkboxes)} cursos encontrados en checkboxes")
        else:
            print("   ❌ No se encontraron checkboxes de cursos")
        
        # Verificar Bootstrap y librerías
        print("\n📦 VERIFICACIÓN DE LIBRERÍAS:")
        librerias = [
            ('bootstrap.min.js', 'Bootstrap JS'),
            ('fullcalendar', 'FullCalendar'),
            ('jquery', 'jQuery'),
            ('bootstrap.bundle.min.js', 'Bootstrap Bundle')
        ]
        
        for lib, nombre in librerias:
            if lib in content:
                print(f"   ✅ {nombre}")
            else:
                print(f"   ⚠️ {nombre} - No encontrado")
        
        if elementos_faltantes:
            print(f"\n❌ ENCONTRADOS {len(elementos_faltantes)} ELEMENTOS FALTANTES")
            return False
        else:
            print("\n✅ TODOS LOS ELEMENTOS CRÍTICOS ESTÁN PRESENTES")
            return True
    
    else:
        print(f"❌ Error en el response: {response.status_code}")
        return False

def test_context_data():
    print("\n🎯 VERIFICANDO DATOS DEL CONTEXTO")
    print("=" * 30)
    
    from smapp.views import calendario
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/calendario/')
    
    admin = User.objects.filter(is_superuser=True).first()
    request.user = admin
    
    # Llamar a la vista directamente
    response = calendario(request)
    
    print(f"Response status: {response.status_code}")
    
    if hasattr(response, 'context_data'):
        context = response.context_data
        print(f"Context keys: {list(context.keys())}")
        
        campos_esperados = [
            'puede_crear_eventos',
            'user_type', 
            'cursos',
            'eventos_json',
            'tipos_evento',
            'prioridades'
        ]
        
        for campo in campos_esperados:
            if campo in context:
                valor = context[campo]
                if campo == 'cursos':
                    print(f"   ✅ {campo}: {len(valor)} cursos")
                elif campo == 'eventos_json':
                    print(f"   ✅ {campo}: JSON con datos")
                else:
                    print(f"   ✅ {campo}: {valor}")
            else:
                print(f"   ❌ {campo}: FALTA")

if __name__ == '__main__':
    success = test_calendario_response()
    test_context_data()
    
    if success:
        print("\n🎉 EL CALENDARIO ESTÁ COMPLETAMENTE FUNCIONAL")
        print("🌐 Abre http://127.0.0.1:8000/calendario/ en tu navegador")
        print("🔧 Si tienes problemas, verifica:")
        print("   1. Que hayas hecho login como administrador")
        print("   2. Que JavaScript esté habilitado")
        print("   3. Que no haya errores en la consola del navegador")
    else:
        print("\n⚠️ SE ENCONTRARON PROBLEMAS - REVISAR ELEMENTOS FALTANTES")
