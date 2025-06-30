#!/usr/bin/env python
"""
Script para probar la funcionalidad del calendario
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import EventoCalendario

def crear_evento_prueba():
    """Crear un evento de prueba para verificar el calendario"""
    
    # Obtener o crear un usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        print("✅ Usuario admin creado")
    
    # Crear evento de prueba para hoy
    evento = EventoCalendario.objects.create(
        titulo="Evento de Prueba - Calendario Funcional",
        descripcion="Este evento verifica que el calendario esté funcionando correctamente",
        fecha=date.today(),
        hora_inicio="10:00",
        hora_fin="11:00",
        tipo_evento="general",
        prioridad="media",
        para_todos_los_cursos=True,
        solo_profesores=False,
        creado_por=admin_user
    )
    
    print(f"✅ Evento creado: {evento.titulo}")
    print(f"📅 Fecha: {evento.fecha}")
    print(f"👤 Responsable: {evento.creado_por.username}")
    print(f"🎨 Color: {evento.color_por_tipo}")
    
    # Crear otro evento para mañana
    evento2 = EventoCalendario.objects.create(
        titulo="Reunión de Profesores",
        descripcion="Reunión mensual del cuerpo docente",
        fecha=date.today() + timedelta(days=1),
        hora_inicio="14:00",
        hora_fin="16:00",
        tipo_evento="reunion",
        prioridad="alta",
        para_todos_los_cursos=False,
        solo_profesores=True,
        creado_por=admin_user
    )
    
    print(f"✅ Segundo evento creado: {evento2.titulo}")
    print(f"📅 Fecha: {evento2.fecha}")
    
    # Mostrar estadísticas
    total_eventos = EventoCalendario.objects.count()
    eventos_hoy = EventoCalendario.objects.filter(fecha=date.today()).count()
    
    print(f"\n📊 Estadísticas del calendario:")
    print(f"   Total de eventos: {total_eventos}")
    print(f"   Eventos hoy: {eventos_hoy}")
    
    print(f"\n🌐 Accede al calendario en: http://127.0.0.1:8000/calendario/")
    print(f"🔐 Usuario: {admin_user.username}")
    print(f"🔑 Contraseña: admin123")

if __name__ == "__main__":
    crear_evento_prueba()
