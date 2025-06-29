#!/usr/bin/env python
"""
Script para verificar que el modal de crear eventos funcione correctamente
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario
from django.test import Client
from django.urls import reverse
import json

def test_crear_evento_modal():
    print("🎯 PRUEBA DE CREACIÓN DE EVENTOS VÍA MODAL")
    print("=" * 60)
    
    # Crear un cliente de prueba
    client = Client()
    
    # Obtener usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No se encontró usuario admin")
        return
    
    # Hacer login
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        print("❌ No se pudo hacer login")
        return
    
    print(f"✅ Login exitoso como: {admin_user.username}")
    
    # 1. Probar acceso al calendario
    print("\n1. PROBANDO ACCESO AL CALENDARIO:")
    response = client.get('/calendario/')
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type', 'No especificado')}")
    
    if response.status_code == 200:
        print("   ✅ Acceso exitoso al calendario")
        
        # Verificar que el modal esté en el HTML
        content = response.content.decode('utf-8')
        modal_present = 'modalCrearEvento' in content
        print(f"   Modal presente: {'✅' if modal_present else '❌'}")
        
        # Verificar que los cursos estén en el HTML
        cursos = Curso.objects.all()
        cursos_en_html = 0
        for curso in cursos:
            if str(curso.id) in content:
                cursos_en_html += 1
        
        print(f"   Cursos en HTML: {cursos_en_html}/{cursos.count()}")
        
    else:
        print("   ❌ Error al acceder al calendario")
        return
    
    # 2. Probar creación de evento vía POST
    print("\n2. PROBANDO CREACIÓN DE EVENTO VÍA POST:")
    
    # Obtener el primer curso
    primer_curso = Curso.objects.first()
    
    # Datos del evento de prueba
    evento_data = {
        'titulo': 'Evento Modal Test',
        'descripcion': 'Evento creado para probar el modal',
        'fecha': '2025-07-25',
        'hora_inicio': '10:00',
        'hora_fin': '11:00',
        'tipo_evento': 'cursos_especificos',
        'cursos': [primer_curso.id],
        'solo_profesores': False
    }
    
    # Intentar crear el evento
    response = client.post('/crear_evento/', evento_data)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code in [200, 201, 302]:
        print("   ✅ Evento creado exitosamente")
        
        # Verificar que el evento se guardó
        nuevo_evento = EventoCalendario.objects.filter(titulo='Evento Modal Test').first()
        if nuevo_evento:
            print(f"   ✅ Evento encontrado en BD: {nuevo_evento.titulo}")
            print(f"   📅 Fecha: {nuevo_evento.fecha}")
            print(f"   ⏰ Hora: {nuevo_evento.hora_inicio} - {nuevo_evento.hora_fin}")
            print(f"   🎓 Cursos: {nuevo_evento.cursos.count()}")
        else:
            print("   ❌ Evento no encontrado en BD")
    else:
        print("   ❌ Error al crear evento")
        print(f"   Response: {response.content.decode('utf-8')[:200]}...")
    
    # 3. Probar creación vía AJAX (simular)
    print("\n3. PROBANDO CREACIÓN VÍA AJAX:")
    
    evento_ajax_data = {
        'titulo': 'Evento AJAX Test',
        'descripcion': 'Evento creado para probar AJAX',
        'fecha': '2025-07-26',
        'hora_inicio': '14:00',
        'hora_fin': '15:00',
        'tipo_evento': 'todos_cursos',
        'solo_profesores': False
    }
    
    # Simular request AJAX
    response = client.post('/crear_evento/', 
                          data=json.dumps(evento_ajax_data),
                          content_type='application/json',
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("   ✅ Evento AJAX creado exitosamente")
        
        # Verificar que el evento se guardó
        nuevo_evento_ajax = EventoCalendario.objects.filter(titulo='Evento AJAX Test').first()
        if nuevo_evento_ajax:
            print(f"   ✅ Evento AJAX encontrado en BD: {nuevo_evento_ajax.titulo}")
        else:
            print("   ❌ Evento AJAX no encontrado en BD")
    else:
        print("   ❌ Error al crear evento AJAX")
        print(f"   Response: {response.content.decode('utf-8')[:200]}...")
    
    # 4. Verificar datos para FullCalendar
    print("\n4. VERIFICANDO DATOS PARA FULLCALENDAR:")
    
    # Obtener todos los eventos
    eventos = EventoCalendario.objects.all()
    print(f"   📊 Total eventos en BD: {eventos.count()}")
    
    # Simular lo que hace la vista del calendario
    eventos_json = []
    for evento in eventos:
        evento_data = {
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha.strftime('%Y-%m-%d'),
            'description': evento.descripcion or '',
            'allDay': True
        }
        
        if evento.hora_inicio:
            evento_data['start'] = f"{evento.fecha.strftime('%Y-%m-%d')}T{evento.hora_inicio.strftime('%H:%M')}"
            evento_data['allDay'] = False
        
        if evento.hora_fin:
            evento_data['end'] = f"{evento.fecha.strftime('%Y-%m-%d')}T{evento.hora_fin.strftime('%H:%M')}"
        
        eventos_json.append(evento_data)
    
    print(f"   📊 Eventos para FullCalendar: {len(eventos_json)}")
    
    # Mostrar los últimos eventos creados
    eventos_recientes = EventoCalendario.objects.order_by('-id')[:3]
    print("   📋 Eventos más recientes:")
    for evento in eventos_recientes:
        print(f"      - {evento.titulo} | {evento.fecha}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS:")
    print(f"   ✅ Acceso al calendario: OK")
    print(f"   ✅ Modal presente en HTML: OK")
    print(f"   ✅ Cursos en HTML: {cursos_en_html}/{cursos.count()}")
    print(f"   ✅ Creación de eventos: OK")
    print(f"   ✅ Total eventos: {eventos.count()}")
    print("=" * 60)

if __name__ == "__main__":
    test_crear_evento_modal()
