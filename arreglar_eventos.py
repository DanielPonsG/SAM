#!/usr/bin/env python
"""
Script para arreglar eventos sin usuario asignado
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, User
from datetime import date, timedelta

def arreglar_eventos():
    print("🔧 Arreglando eventos sin usuario asignado...")
    
    # Buscar un usuario por defecto
    usuario_defecto = User.objects.filter(is_superuser=True).first()
    if not usuario_defecto:
        usuario_defecto = User.objects.filter(is_staff=True).first()
    if not usuario_defecto:
        usuario_defecto = User.objects.first()
    
    if not usuario_defecto:
        print("❌ No hay usuarios en el sistema. Creando usuario admin...")
        usuario_defecto = User.objects.create_superuser(
            username='admin',
            email='admin@escuela.com',
            password='admin123'
        )
        print(f"✅ Usuario admin creado: {usuario_defecto.username}")
    
    # Arreglar eventos sin usuario
    eventos_sin_usuario = EventoCalendario.objects.filter(creado_por__isnull=True)
    print(f"📊 Eventos sin usuario: {eventos_sin_usuario.count()}")
    
    for evento in eventos_sin_usuario:
        evento.creado_por = usuario_defecto
        evento.save()
        print(f"✅ Evento '{evento.titulo}' asignado a {usuario_defecto.username}")
    
    # Crear algunos eventos de prueba si no hay ninguno
    if EventoCalendario.objects.count() == 0:
        print("📅 Creando eventos de prueba...")
        
        eventos_prueba = [
            {
                'titulo': 'Reunión de Profesores',
                'descripcion': 'Reunión mensual del equipo docente',
                'fecha': date.today(),
                'tipo_evento': 'reunion',
                'hora_inicio': '14:00',
                'hora_fin': '16:00'
            },
            {
                'titulo': 'Examen de Matemáticas',
                'descripcion': 'Evaluación del primer trimestre',
                'fecha': date.today() + timedelta(days=1),
                'tipo_evento': 'evaluacion',
                'hora_inicio': '08:00',
                'hora_fin': '10:00'
            },
            {
                'titulo': 'Actividad Deportiva',
                'descripcion': 'Campeonato inter-cursos',
                'fecha': date.today() + timedelta(days=3),
                'tipo_evento': 'actividad',
                'hora_inicio': '15:00',
                'hora_fin': '17:00'
            },
            {
                'titulo': 'Día del Estudiante',
                'descripcion': 'Celebración especial para los estudiantes',
                'fecha': date.today() + timedelta(days=7),
                'tipo_evento': 'general'
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
                prioridad='media',
                para_todos_los_cursos=True,
                solo_profesores=False,
                creado_por=usuario_defecto
            )
            print(f"✅ Evento creado: {evento.titulo}")
    
    # Estadísticas finales
    total_eventos = EventoCalendario.objects.count()
    eventos_con_usuario = EventoCalendario.objects.filter(creado_por__isnull=False).count()
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total eventos: {total_eventos}")
    print(f"   Con usuario asignado: {eventos_con_usuario}")
    print(f"   Sin usuario: {total_eventos - eventos_con_usuario}")
    
    if total_eventos == eventos_con_usuario:
        print("✅ ¡Todos los eventos tienen usuario asignado!")
    else:
        print("⚠️  Algunos eventos aún sin usuario")
    
    return total_eventos > 0

if __name__ == "__main__":
    try:
        success = arreglar_eventos()
        if success:
            print("\n🎉 ¡Arreglo completado! Ahora prueba el calendario en:")
            print("   http://127.0.0.1:8000/calendario/")
        else:
            print("\n❌ No se pudieron crear eventos")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
