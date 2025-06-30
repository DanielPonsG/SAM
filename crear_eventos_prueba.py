#!/usr/bin/env python
"""
Script simple para crear eventos de prueba en el calendario
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, User
from datetime import date, timedelta
from django.contrib.auth.models import User

def crear_eventos_prueba():
    print("🎯 Creando eventos de prueba...")
    
    # Obtener o crear un usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No se encontró ningún usuario administrador")
        return
    
    print(f"✅ Usando usuario: {admin_user.username}")
    
    # Limpiar eventos existentes
    EventoCalendario.objects.all().delete()
    print("🧹 Eventos anteriores eliminados")
    
    # Crear eventos de prueba
    eventos_prueba = [
        {
            'titulo': 'Reunión de Profesores',
            'descripcion': 'Reunión mensual del equipo docente',
            'fecha': date.today() + timedelta(days=1),
            'hora_inicio': '09:00',
            'hora_fin': '11:00',
            'tipo_evento': 'reunion',
            'prioridad': 'alta'
        },
        {
            'titulo': 'Prueba de Matemáticas',
            'descripcion': 'Evaluación del primer trimestre',
            'fecha': date.today() + timedelta(days=3),
            'hora_inicio': '08:00',
            'hora_fin': '09:30',
            'tipo_evento': 'evaluacion',
            'prioridad': 'media'
        },
        {
            'titulo': 'Día del Deporte',
            'descripcion': 'Actividades deportivas para todos los cursos',
            'fecha': date.today() + timedelta(days=7),
            'hora_inicio': '10:00',
            'hora_fin': '16:00',
            'tipo_evento': 'actividad',
            'prioridad': 'media'
        },
        {
            'titulo': 'Entrega de Notas',
            'descripcion': 'Fecha límite para entrega de calificaciones',
            'fecha': date.today() + timedelta(days=10),
            'tipo_evento': 'administrativo',
            'prioridad': 'alta'
        },
        {
            'titulo': 'Evento de Prueba Hoy',
            'descripcion': 'Evento para probar el calendario hoy',
            'fecha': date.today(),
            'hora_inicio': '14:00',
            'hora_fin': '15:00',
            'tipo_evento': 'general',
            'prioridad': 'baja'
        }
    ]
    
    for evento_data in eventos_prueba:
        evento = EventoCalendario.objects.create(
            titulo=evento_data['titulo'],
            descripcion=evento_data['descripcion'],
            fecha=evento_data['fecha'],
            hora_inicio=evento_data.get('hora_inicio'),
            hora_fin=evento_data.get('hora_fin'),
            tipo_evento=evento_data['tipo_evento'],
            prioridad=evento_data['prioridad'],
            para_todos_los_cursos=True,
            solo_profesores=False,
            creado_por=admin_user
        )
        print(f"✅ Evento creado: {evento.titulo} ({evento.fecha})")
    
    print(f"\n🎉 Total de eventos creados: {EventoCalendario.objects.count()}")
    
    # Verificar colores
    print("\n🎨 Verificando colores por tipo:")
    for evento in EventoCalendario.objects.all():
        print(f"  - {evento.titulo}: {evento.color_por_tipo}")

if __name__ == "__main__":
    crear_eventos_prueba()
