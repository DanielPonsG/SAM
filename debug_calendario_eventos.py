#!/usr/bin/env python
"""
Script para debuggear el estado actual de los eventos del calendario
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, Curso, Profesor, User
from django.contrib.auth.models import User
from datetime import datetime, date
import json

def main():
    print("=== DEBUG CALENDARIO EVENTOS ===")
    
    # 1. Verificar eventos existentes
    eventos = EventoCalendario.objects.all()
    print(f"\n📊 Total de eventos en la base: {eventos.count()}")
    
    if eventos.count() > 0:
        print("\n📋 Lista de eventos:")
        for evento in eventos:
            print(f"  - ID: {evento.id}")
            print(f"    Título: {evento.titulo}")
            print(f"    Fecha: {evento.fecha}")
            print(f"    Creado por: {evento.creado_por.username if evento.creado_por else 'N/A'}")
            print(f"    Para todos: {evento.para_todos_los_cursos}")
            print(f"    Solo profesores: {evento.solo_profesores}")
            print(f"    Cursos asignados: {evento.cursos.count()}")
            print(f"    Color: {evento.color_por_tipo}")
            print("    ---")
    
    # 2. Verificar usuarios
    print(f"\n👥 Total usuarios: {User.objects.count()}")
    print("Usuarios disponibles:")
    for user in User.objects.all():
        print(f"  - {user.username} (ID: {user.id}) - Staff: {user.is_staff} - Super: {user.is_superuser}")
    
    # 3. Verificar cursos
    print(f"\n🎓 Total cursos: {Curso.objects.count()}")
    
    # 4. Simular serialización de eventos (como en la vista)
    print("\n🔧 Simulando serialización para FullCalendar:")
    eventos_json = []
    for evento in eventos:
        evento_serializado = {
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha.isoformat(),
            'description': evento.descripcion or '',
            'backgroundColor': evento.color_por_tipo,
            'borderColor': evento.color_por_tipo,
            'textColor': '#fff',
            'extendedProps': {
                'description': evento.descripcion or '',
                'responsable': evento.creado_por.first_name if evento.creado_por and evento.creado_por.first_name else (evento.creado_por.username if evento.creado_por else 'Sistema'),
                'tipo': evento.get_tipo_evento_display(),
                'prioridad': evento.get_prioridad_display()
            }
        }
        eventos_json.append(evento_serializado)
    
    print(f"Eventos JSON para FullCalendar: {len(eventos_json)}")
    if eventos_json:
        print("Ejemplo del primer evento:")
        print(json.dumps(eventos_json[0], indent=2, default=str))
    
    # 5. Crear evento de prueba si no hay eventos
    if eventos.count() == 0:
        print("\n🎯 No hay eventos. Creando evento de prueba...")
        try:
            # Buscar un usuario administrador
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                admin_user = User.objects.first()
            
            if admin_user:
                evento_test = EventoCalendario.objects.create(
                    titulo="Evento de Prueba - Calendario",
                    descripcion="Este es un evento de prueba para verificar el funcionamiento del calendario",
                    fecha=date.today(),
                    hora_inicio="09:00",
                    hora_fin="10:00",
                    tipo_evento="general",
                    prioridad="media",
                    para_todos_los_cursos=True,
                    solo_profesores=False,
                    creado_por=admin_user
                )
                print(f"✅ Evento de prueba creado: ID {evento_test.id}")
            else:
                print("❌ No se encontró ningún usuario para crear el evento")
        except Exception as e:
            print(f"❌ Error al crear evento de prueba: {e}")
    
    print("\n🔍 Verificando método color_por_tipo:")
    for evento in EventoCalendario.objects.all():
        print(f"  - {evento.titulo}: {evento.color_por_tipo}")
    
    print("\n=== FIN DEBUG ===")

if __name__ == "__main__":
    main()
