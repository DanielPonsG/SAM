#!/usr/bin/env python
"""
Script de validación completa del calendario
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, User, Curso
from datetime import date
import json

def validar_calendario():
    print("🔍 === VALIDACIÓN COMPLETA DEL CALENDARIO ===")
    
    # 1. Verificar usuarios
    usuarios = User.objects.all()
    print(f"\n👥 Usuarios: {usuarios.count()}")
    if usuarios.count() == 0:
        print("❌ No hay usuarios. Creando admin...")
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print(f"✅ Usuario admin creado: {user.username}")
    
    # 2. Verificar eventos
    eventos = EventoCalendario.objects.all()
    print(f"\n📅 Eventos: {eventos.count()}")
    
    eventos_sin_usuario = eventos.filter(creado_por__isnull=True)
    print(f"⚠️  Eventos sin usuario: {eventos_sin_usuario.count()}")
    
    if eventos_sin_usuario.count() > 0:
        usuario_admin = User.objects.filter(is_superuser=True).first()
        for evento in eventos_sin_usuario:
            evento.creado_por = usuario_admin
            evento.save()
        print(f"✅ Eventos sin usuario arreglados")
    
    # 3. Simular vista del calendario
    print(f"\n🔧 Simulando vista del calendario...")
    eventos_json = []
    for evento in eventos:
        try:
            responsable = "Sistema"
            if evento.creado_por:
                responsable = evento.creado_por.first_name or evento.creado_por.username
            
            evento_json = {
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.fecha.isoformat(),
                'backgroundColor': evento.color_por_tipo,
                'extendedProps': {
                    'responsable': responsable,
                    'descripcion': evento.descripcion or ''
                }
            }
            eventos_json.append(evento_json)
            print(f"✅ Evento serializado: {evento.titulo} - Responsable: {responsable}")
        except Exception as e:
            print(f"❌ Error al serializar evento {evento.id}: {e}")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   • Usuarios: {User.objects.count()}")
    print(f"   • Eventos: {EventoCalendario.objects.count()}")
    print(f"   • Eventos con usuario: {EventoCalendario.objects.filter(creado_por__isnull=False).count()}")
    print(f"   • Eventos JSON: {len(eventos_json)}")
    print(f"   • Cursos: {Curso.objects.count()}")
    
    # 4. Crear eventos de prueba si no hay
    if eventos.count() == 0:
        print(f"\n📝 Creando eventos de prueba...")
        usuario = User.objects.first()
        
        EventoCalendario.objects.create(
            titulo="Evento de Prueba Hoy",
            descripcion="Evento para probar el calendario",
            fecha=date.today(),
            tipo_evento="general",
            para_todos_los_cursos=True,
            creado_por=usuario
        )
        
        EventoCalendario.objects.create(
            titulo="Reunión de Profesores",
            descripcion="Reunión mensual",
            fecha=date.today(),
            tipo_evento="reunion",
            solo_profesores=True,
            creado_por=usuario
        )
        
        print(f"✅ Eventos de prueba creados")
    
    print(f"\n🎉 VALIDACIÓN COMPLETADA")
    print(f"📱 URL: http://127.0.0.1:8000/calendario/")
    return True

if __name__ == "__main__":
    try:
        validar_calendario()
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        import traceback
        traceback.print_exc()
