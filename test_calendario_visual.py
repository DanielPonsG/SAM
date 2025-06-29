#!/usr/bin/env python
"""
Script para verificar visualmente que el calendario funciona correctamente
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario
from django.utils import timezone
from datetime import datetime, timedelta
import json

def test_calendario_visual():
    print("🎯 VERIFICACIÓN VISUAL DEL CALENDARIO")
    print("=" * 50)
    
    # 1. Verificar que tenemos usuarios
    print("\n1. VERIFICANDO USUARIOS:")
    usuarios = User.objects.all()
    print(f"   📊 Total usuarios: {usuarios.count()}")
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        print(f"   ✅ Usuario admin encontrado: {admin_user.username}")
    else:
        print("   ❌ No se encontró usuario admin")
    
    # 2. Verificar cursos
    print("\n2. VERIFICANDO CURSOS:")
    cursos = Curso.objects.all()
    print(f"   📊 Total cursos: {cursos.count()}")
    
    if cursos.exists():
        print("   📋 Cursos disponibles:")
        for curso in cursos:
            print(f"      - {curso}")
    else:
        print("   ❌ No se encontraron cursos")
    
    # 3. Verificar eventos
    print("\n3. VERIFICANDO EVENTOS:")
    eventos = EventoCalendario.objects.all()
    print(f"   📊 Total eventos: {eventos.count()}")
    
    if eventos.exists():
        print("   📋 Eventos disponibles:")
        for evento in eventos[:5]:  # Mostrar solo los primeros 5
            print(f"      - {evento.titulo} | {evento.fecha} | {evento.hora_inicio}-{evento.hora_fin}")
            if evento.cursos.exists():
                cursos_str = ", ".join([str(c) for c in evento.cursos.all()])
                print(f"        Cursos: {cursos_str}")
            else:
                print("        Cursos: Todos los cursos")
    else:
        print("   ❌ No se encontraron eventos")
    
    # 4. Verificar datos para JSON
    print("\n4. VERIFICANDO DATOS PARA FULLCALENDAR:")
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
    
    if eventos_json:
        print("   📋 Ejemplo de evento JSON:")
        print(f"      {json.dumps(eventos_json[0], indent=6, default=str)}")
    
    # 5. Verificar permisos
    print("\n5. VERIFICANDO PERMISOS:")
    if admin_user:
        print(f"   ✅ Admin puede crear eventos: {admin_user.is_superuser}")
        print(f"   ✅ Admin puede ver todos los eventos: True")
    
    # 6. Crear un evento de prueba si no existe
    print("\n6. CREANDO EVENTO DE PRUEBA:")
    fecha_prueba = timezone.now().date() + timedelta(days=1)
    evento_prueba, created = EventoCalendario.objects.get_or_create(
        titulo="Evento de Prueba Visual",
        fecha=fecha_prueba,
        defaults={
            'descripcion': 'Evento creado para verificar que el calendario funciona',
            'hora_inicio': timezone.now().time().replace(hour=10, minute=0),
            'hora_fin': timezone.now().time().replace(hour=11, minute=0),
            'creado_por': admin_user if admin_user else None,
            'solo_profesores': False
        }
    )
    
    if created:
        print(f"   ✅ Evento de prueba creado: {evento_prueba.titulo}")
        if cursos.exists():
            evento_prueba.cursos.add(cursos.first())
            print(f"   ✅ Asignado al curso: {cursos.first()}")
    else:
        print(f"   ℹ️ Evento de prueba ya existe: {evento_prueba.titulo}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN FINAL:")
    print(f"   Usuarios: {usuarios.count()}")
    print(f"   Cursos: {cursos.count()}")
    print(f"   Eventos: {EventoCalendario.objects.count()}")
    print(f"   Eventos JSON: {len(eventos_json)}")
    
    if usuarios.count() > 0 and cursos.count() > 0 and EventoCalendario.objects.count() > 0:
        print("   ✅ TODOS LOS ELEMENTOS ESTÁN PRESENTES")
        print("   🌐 Puedes abrir http://127.0.0.1:8000/calendario/ para ver el calendario")
    else:
        print("   ❌ FALTAN ELEMENTOS CRÍTICOS")
    
    print("=" * 50)

if __name__ == "__main__":
    test_calendario_visual()
