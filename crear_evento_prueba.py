#!/usr/bin/env python
"""
Script para crear un evento de prueba desde la consola y verificar funcionalidad
"""
import os
import sys
import django
from datetime import datetime, date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario, Profesor, Estudiante

def crear_evento_completo():
    """Crear un evento completo con cursos asignados"""
    print("🎯 CREANDO EVENTO COMPLETO DE PRUEBA")
    print("=" * 50)
    
    # Obtener un usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return
    
    # Obtener cursos del año actual
    cursos = Curso.objects.filter(anio=datetime.now().year)
    if cursos.count() == 0:
        print("❌ No hay cursos disponibles")
        return
    
    # Crear evento
    evento = EventoCalendario.objects.create(
        titulo="Evento de Prueba - Selección de Cursos",
        descripcion="Evento creado para probar la funcionalidad de selección de cursos específicos",
        fecha=date.today() + timedelta(days=7),  # Evento en una semana
        hora_inicio="09:00",
        hora_fin="11:00",
        tipo_evento='evaluacion',
        prioridad='alta',
        para_todos_los_cursos=False,
        creado_por=admin_user
    )
    
    # Asignar cursos específicos
    cursos_seleccionados = cursos[:3]  # Primeros 3 cursos
    evento.cursos.set(cursos_seleccionados)
    
    print(f"✅ Evento creado: {evento.titulo}")
    print(f"📅 Fecha: {evento.fecha}")
    print(f"⏰ Hora: {evento.hora_inicio} - {evento.hora_fin}")
    print(f"🎨 Color: {evento.color_por_tipo}")
    print(f"📚 Cursos asignados: {evento.cursos.count()}")
    
    for curso in evento.cursos.all():
        print(f"   - {curso}")
    
    print("\n" + "=" * 50)
    print("🌐 DATOS JSON PARA FULLCALENDAR:")
    print("=" * 50)
    
    # Simular datos JSON como en la vista
    evento_json = {
        'id': evento.id,
        'title': evento.titulo,
        'start': evento.fecha.isoformat(),
        'description': evento.descripcion or '',
        'backgroundColor': evento.color_por_tipo,
        'borderColor': evento.color_por_tipo,
        'textColor': '#fff'
    }
    
    import json
    print(json.dumps(evento_json, indent=2))
    
    print("\n" + "=" * 50)
    print("✅ EVENTO CREADO EXITOSAMENTE")
    print("💡 Ahora puedes ver el evento en el calendario web")
    print("=" * 50)

if __name__ == "__main__":
    crear_evento_completo()
