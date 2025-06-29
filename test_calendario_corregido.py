#!/usr/bin/env python
"""
Script para probar las correcciones del calendario
"""
import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario, Profesor, Estudiante, Perfil

def test_calendario_corregido():
    """Función para probar las correcciones del calendario"""
    print("=" * 60)
    print("🔧 PROBANDO CORRECCIONES DEL CALENDARIO")
    print("=" * 60)
    
    # 1. Verificar que hay cursos disponibles
    print("\n📚 VERIFICANDO CURSOS DISPONIBLES:")
    cursos = Curso.objects.filter(anio=datetime.now().year)
    print(f"   Total cursos del año actual: {cursos.count()}")
    
    if cursos.count() == 0:
        print("   ⚠️  No hay cursos del año actual. Creando algunos...")
        
        # Crear algunos cursos de prueba
        curso1 = Curso.objects.create(nivel='1M', paralelo='A', anio=datetime.now().year)
        curso2 = Curso.objects.create(nivel='2M', paralelo='A', anio=datetime.now().year)
        curso3 = Curso.objects.create(nivel='3M', paralelo='B', anio=datetime.now().year)
        print(f"   ✅ Creados 3 cursos de prueba")
        cursos = Curso.objects.filter(anio=datetime.now().year)
    
    for curso in cursos[:5]:  # Mostrar solo los primeros 5
        print(f"   - {curso} (ID: {curso.id})")
    
    # 2. Verificar usuarios con permisos
    print("\n👤 VERIFICANDO USUARIOS CON PERMISOS:")
    usuarios_con_permisos = []
    
    # Verificar administradores
    try:
        admins = User.objects.filter(perfil__tipo_usuario='administrador', is_active=True)
        for admin in admins:
            usuarios_con_permisos.append(f"Admin: {admin.username}")
    except:
        pass
    
    # Verificar profesores
    try:
        profesores = Profesor.objects.filter(user__is_active=True)
        for prof in profesores[:3]:  # Solo primeros 3
            usuarios_con_permisos.append(f"Profesor: {prof.user.username if prof.user else 'Sin usuario'}")
    except:
        pass
    
    if usuarios_con_permisos:
        for usuario in usuarios_con_permisos:
            print(f"   ✅ {usuario}")
    else:
        print("   ⚠️  No se encontraron usuarios con permisos para crear eventos")
    
    # 3. Verificar eventos existentes
    print("\n📅 VERIFICANDO EVENTOS EXISTENTES:")
    eventos = EventoCalendario.objects.all().order_by('-fecha')[:5]
    print(f"   Total eventos: {EventoCalendario.objects.count()}")
    
    for evento in eventos:
        cursos_asignados = evento.cursos.count()
        print(f"   - {evento.titulo} ({evento.fecha}) - {cursos_asignados} cursos")
    
    # 4. Crear un evento de prueba
    print("\n🎯 CREANDO EVENTO DE PRUEBA:")
    try:
        # Buscar un usuario administrador o crear uno
        admin_user = None
        try:
            admin_user = User.objects.filter(perfil__tipo_usuario='administrador').first()
        except:
            # Buscar superusuario
            admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            print("   ⚠️  No hay usuario administrador disponible")
        else:
            evento_prueba = EventoCalendario.objects.create(
                titulo="Evento de Prueba - Calendario Corregido",
                descripcion="Este es un evento creado para probar las correcciones",
                fecha=date.today(),
                tipo_evento='general',
                prioridad='media',
                para_todos_los_cursos=False,
                creado_por=admin_user
            )
            
            # Asignar algunos cursos
            if cursos.count() > 0:
                evento_prueba.cursos.set(cursos[:2])  # Asignar primeros 2 cursos
                print(f"   ✅ Evento creado: {evento_prueba.titulo}")
                print(f"   📚 Asignado a {evento_prueba.cursos.count()} cursos")
            else:
                print("   ⚠️  No hay cursos para asignar al evento")
                
    except Exception as e:
        print(f"   ❌ Error creando evento de prueba: {e}")
    
    # 5. Verificar datos JSON para FullCalendar
    print("\n🔄 VERIFICANDO DATOS PARA FULLCALENDAR:")
    import json
    
    eventos_json = []
    for evento in EventoCalendario.objects.all():
        eventos_json.append({
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha.isoformat(),
            'description': evento.descripcion or '',
            'backgroundColor': '#f8f9fa',  # Color por defecto
            'borderColor': '#dee2e6',
        })
    
    print(f"   📊 Eventos para FullCalendar: {len(eventos_json)}")
    
    if eventos_json:
        print("   📝 Ejemplo de evento JSON:")
        print(f"      {json.dumps(eventos_json[0], indent=6)}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    print("   1. Abrir http://127.0.0.1:8000/calendario/ en el navegador")
    print("   2. Probar crear un evento seleccionando cursos específicos")
    print("   3. Verificar que no aparezcan áreas blancas en el calendario")
    print("   4. Confirmar que los checkboxes de cursos funcionen correctamente")

if __name__ == "__main__":
    test_calendario_corregido()
