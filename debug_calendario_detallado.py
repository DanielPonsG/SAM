#!/usr/bin/env python3
"""
Script de depuración del calendario
Identifica problemas específicos en el sistema de calendario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from smapp.models import Curso, EventoCalendario
import json

def test_calendario_debug():
    print("🔍 DEPURANDO CALENDARIO...")
    print("=" * 50)
    
    # 1. Verificar datos en la base de datos
    print("1. VERIFICANDO DATOS EN BD:")
    cursos_count = Curso.objects.count()
    eventos_count = EventoCalendario.objects.count()
    print(f"   - Cursos: {cursos_count}")
    print(f"   - Eventos: {eventos_count}")
    
    if cursos_count == 0:
        print("   ❌ NO HAY CURSOS - Creando curso de prueba...")
        curso = Curso.objects.create(
            nivel='1B',
            paralelo='A',
            anio=2025
        )
        print(f"   ✅ Curso creado: {curso.nombre_completo}")
    
    # 2. Test de la vista calendario
    print("\n2. TESTEANDO VISTA CALENDARIO:")
    client = Client()
    
    # Login como admin
    try:
        admin_user = User.objects.get(username='admin')
        client.force_login(admin_user)
        print("   ✅ Login como admin exitoso")
    except User.DoesNotExist:
        print("   ❌ Usuario admin no existe")
        return False
    
    # Acceder al calendario
    response = client.get('/calendario/')
    print(f"   - Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Verificar elementos importantes
        checks = [
            ('id="calendar"', 'Elemento calendar'),
            ('modalCrearEvento', 'Modal crear evento'),
            ('formCrearEvento', 'Formulario crear evento'),
            ('cursos_especificos', 'Sección cursos específicos'),
            ('FullCalendar', 'Biblioteca FullCalendar'),
            ('eventos_json', 'Variable eventos JSON'),
        ]
        
        print("   Elementos encontrados:")
        for check, desc in checks:
            if check in content:
                print(f"   ✅ {desc}")
            else:
                print(f"   ❌ {desc}")
        
        # Verificar específicamente los cursos en el template
        cursos_html_count = content.count('cursos_especificos')
        print(f"   - Referencias a cursos_especificos: {cursos_html_count}")
        
        # Verificar si aparecen los nombres de cursos
        cursos = Curso.objects.all()
        for curso in cursos:
            if curso.nombre_completo in content:
                print(f"   ✅ Curso {curso.nombre_completo} aparece en HTML")
            else:
                print(f"   ❌ Curso {curso.nombre_completo} NO aparece en HTML")
    
    # 3. Test de creación de evento
    print("\n3. TESTEANDO CREACIÓN DE EVENTO:")
    data = {
        'titulo': 'Evento Debug Test',
        'descripcion': 'Evento de prueba para debug',
        'fecha': '2025-07-01',
        'hora_inicio': '09:00',
        'hora_fin': '10:00',
        'tipo_evento': 'general',
        'prioridad': 'media',
        'dirigido_a': 'todos'
    }
    
    response = client.post(
        '/calendario/',
        data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"   - Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content)
            if response_data.get('success'):
                print("   ✅ Evento creado exitosamente via AJAX")
            else:
                print(f"   ❌ Error al crear evento: {response_data.get('error')}")
        except json.JSONDecodeError:
            print("   ❌ Respuesta no es JSON válido")
            print(f"   Contenido: {response.content.decode()[:200]}...")
    else:
        print(f"   ❌ Error HTTP: {response.status_code}")
    
    # 4. Verificar contexto de la vista
    print("\n4. VERIFICANDO CONTEXTO DE VISTA:")
    from smapp.views import calendario
    from django.http import HttpRequest
    
    request = HttpRequest()
    request.method = 'GET'
    request.user = admin_user
    request.GET = {}
    
    try:
        # Usar el RequestFactory para hacer un test más real
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/calendario/')
        request.user = admin_user
        
        # Ejecutar la vista
        from smapp.views import calendario
        response = calendario(request)
        
        print("   ✅ Vista ejecutada correctamente")
        
        # Verificar que el response contenga el template
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'calendario' in content:
                print("   ✅ Template calendario renderizado")
            else:
                print("   ❌ Template calendario NO renderizado")
        
    except Exception as e:
        print(f"   ❌ Error en vista: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG COMPLETADO")
    
    return True

if __name__ == "__main__":
    test_calendario_debug()
