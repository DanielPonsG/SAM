#!/usr/bin/env python
"""
Script para probar la funcionalidad de creación de eventos vía AJAX
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import EventoCalendario, Curso
from datetime import date, timedelta

def test_crear_evento_ajax():
    print("🧪 PROBANDO CREACIÓN DE EVENTOS VÍA AJAX")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener usuario admin
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No se encontró usuario administrador")
        return
    
    # Hacer login
    client.force_login(admin)
    print(f"✅ Login realizado con usuario: {admin.username}")
    
    # Datos del evento de prueba
    fecha_evento = date.today() + timedelta(days=3)
    
    evento_data = {
        'titulo': 'Evento de Prueba AJAX',
        'descripcion': 'Este evento fue creado mediante una prueba AJAX automatizada',
        'fecha': fecha_evento.strftime('%Y-%m-%d'),
        'hora_inicio': '10:00',
        'hora_fin': '11:30',
        'tipo_evento': 'general',
        'prioridad': 'media',
        'dirigido_a': 'todos'
    }
    
    print(f"📝 Datos del evento: {evento_data}")
    
    # Enviar request AJAX
    response = client.post('/calendario/', 
                          data=evento_data,
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            response_data = json.loads(response.content.decode())
            print(f"📋 Response data: {response_data}")
            
            if response_data.get('success'):
                print("✅ Evento creado exitosamente vía AJAX")
                
                # Verificar que el evento se creó en la BD
                evento_id = response_data.get('evento_id')
                if evento_id:
                    evento = EventoCalendario.objects.get(id=evento_id)
                    print(f"✅ Evento verificado en BD: {evento}")
                    print(f"   - Título: {evento.titulo}")
                    print(f"   - Fecha: {evento.fecha}")
                    print(f"   - Color: {evento.color_por_tipo}")
                else:
                    print("⚠️ No se retornó ID del evento")
            else:
                print(f"❌ Error en la creación: {response_data.get('error')}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            print(f"Response content: {response.content.decode()}")
    else:
        print(f"❌ Error en la request: {response.status_code}")
    
    # Probar también con cursos específicos
    print("\n" + "-" * 30)
    print("🎯 PROBANDO CON CURSOS ESPECÍFICOS")
    
    cursos = Curso.objects.all()[:2]  # Tomar 2 cursos
    if cursos:
        evento_data_cursos = {
            'titulo': 'Evento para Cursos Específicos',
            'descripcion': 'Evento solo para cursos seleccionados',
            'fecha': (fecha_evento + timedelta(days=1)).strftime('%Y-%m-%d'),
            'hora_inicio': '14:00',
            'hora_fin': '15:30',
            'tipo_evento': 'reunion',
            'prioridad': 'alta',
            'dirigido_a': 'cursos_especificos',
            'cursos_especificos': [str(curso.id) for curso in cursos]
        }
        
        print(f"📝 Cursos seleccionados: {[str(curso) for curso in cursos]}")
        
        response2 = client.post('/calendario/', 
                               data=evento_data_cursos,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        if response2.status_code == 200:
            try:
                response_data2 = json.loads(response2.content.decode())
                
                if response_data2.get('success'):
                    print("✅ Evento con cursos específicos creado exitosamente")
                    
                    evento_id2 = response_data2.get('evento_id')
                    if evento_id2:
                        evento2 = EventoCalendario.objects.get(id=evento_id2)
                        print(f"✅ Cursos asignados: {evento2.cursos.count()}")
                        for curso in evento2.cursos.all():
                            print(f"   - {curso}")
                else:
                    print(f"❌ Error: {response_data2.get('error')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error JSON: {e}")
        else:
            print(f"❌ Error status: {response2.status_code}")
    
    print("\n" + "=" * 50)
    print("✅ PRUEBA AJAX COMPLETADA")

def test_validaciones():
    print("\n🔍 PROBANDO VALIDACIONES")
    print("=" * 30)
    
    client = Client()
    admin = User.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    # 1. Título vacío
    print("1. Probando título vacío...")
    response = client.post('/calendario/', 
                          data={'titulo': '', 'fecha': '2025-07-01'},
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        if not data.get('success'):
            print(f"   ✅ Validación correcta: {data.get('error')}")
        else:
            print("   ❌ Debería haber fallado")
    
    # 2. Fecha vacía
    print("2. Probando fecha vacía...")
    response = client.post('/calendario/', 
                          data={'titulo': 'Test', 'fecha': ''},
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        if not data.get('success'):
            print(f"   ✅ Validación correcta: {data.get('error')}")
        else:
            print("   ❌ Debería haber fallado")
    
    # 3. Horas inválidas
    print("3. Probando horas inválidas...")
    response = client.post('/calendario/', 
                          data={
                              'titulo': 'Test',
                              'fecha': '2025-07-01',
                              'hora_inicio': '15:00',
                              'hora_fin': '14:00'  # Hora fin menor que inicio
                          },
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        if not data.get('success'):
            print(f"   ✅ Validación correcta: {data.get('error')}")
        else:
            print("   ❌ Debería haber fallado")
    
    print("✅ Validaciones completadas")

if __name__ == '__main__':
    test_crear_evento_ajax()
    test_validaciones()
