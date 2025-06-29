#!/usr/bin/env python3
"""
Script para verificar y configurar el calendario completamente funcional
"""

import os
import sys
import django
from datetime import date, time, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import EventoCalendario, Curso, Profesor, Estudiante, Perfil
from django.utils import timezone

def verificar_calendario():
    print("🗓️ VERIFICANDO SISTEMA DE CALENDARIO")
    print("=" * 50)
    
    # 1. Verificar modelos
    print("\n📊 1. VERIFICANDO MODELOS")
    eventos_count = EventoCalendario.objects.count()
    cursos_count = Curso.objects.count()
    usuarios_count = User.objects.count()
    
    print(f"   • Eventos: {eventos_count}")
    print(f"   • Cursos: {cursos_count}")
    print(f"   • Usuarios: {usuarios_count}")
    
    # 2. Verificar usuarios por tipo
    print("\n👥 2. VERIFICANDO USUARIOS POR TIPO")
    
    # Administradores
    admins = User.objects.filter(is_superuser=True)
    print(f"   • Administradores: {admins.count()}")
    for admin in admins:
        print(f"     - {admin.username} (email: {admin.email})")
    
    # Perfiles
    perfiles = Perfil.objects.all()
    print(f"   • Perfiles: {perfiles.count()}")
    tipos_count = {}
    for perfil in perfiles:
        tipo = perfil.tipo_usuario
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    for tipo, count in tipos_count.items():
        print(f"     - {tipo}: {count}")
    
    # 3. Crear eventos de prueba si no existen
    print("\n🎯 3. CREANDO EVENTOS DE PRUEBA")
    
    if eventos_count == 0:
        print("   • No hay eventos. Creando eventos de prueba...")
        crear_eventos_prueba()
    else:
        print(f"   • Ya existen {eventos_count} eventos")
        mostrar_eventos_existentes()
    
    # 4. Verificar permisos por tipo de usuario
    print("\n🔐 4. VERIFICANDO PERMISOS DE ACCESO")
    verificar_permisos_usuarios()
    
    # 5. Mostrar URLs importantes
    print("\n🌐 5. URLS DEL SISTEMA")
    print("   • Calendario: http://localhost:8000/calendario/")
    print("   • Login: http://localhost:8000/login/")
    print("   • Admin: http://localhost:8000/admin/")
    
    print("\n✅ VERIFICACIÓN COMPLETADA")

def crear_eventos_prueba():
    """Crear eventos de prueba para diferentes tipos"""
    try:
        usuario_admin = User.objects.filter(is_superuser=True).first()
        if not usuario_admin:
            print("   ⚠️ No hay usuarios administrador")
            return
        
        hoy = date.today()
        
        # Eventos generales (para todos)
        eventos_generales = [
            {
                'titulo': 'Inicio del Año Escolar 2025',
                'descripcion': 'Ceremonia de inicio del año académico',
                'fecha': hoy + timedelta(days=1),
                'tipo_evento': 'general',
                'prioridad': 'alta',
                'para_todos_los_cursos': True
            },
            {
                'titulo': 'Reunión de Apoderados',
                'descripcion': 'Reunión general con todos los apoderados',
                'fecha': hoy + timedelta(days=7),
                'hora_inicio': time(19, 0),
                'hora_fin': time(21, 0),
                'tipo_evento': 'reunion',
                'prioridad': 'media',
                'para_todos_los_cursos': True
            },
            {
                'titulo': 'Día del Estudiante',
                'descripcion': 'Celebración del día del estudiante con actividades especiales',
                'fecha': hoy + timedelta(days=14),
                'tipo_evento': 'actividad',
                'prioridad': 'media',
                'para_todos_los_cursos': True
            }
        ]
        
        for evento_data in eventos_generales:
            evento, created = EventoCalendario.objects.get_or_create(
                titulo=evento_data['titulo'],
                defaults={**evento_data, 'creado_por': usuario_admin}
            )
            if created:
                print(f"   ✅ Creado: {evento.titulo}")
        
        # Eventos específicos por curso (si hay cursos)
        cursos = Curso.objects.all()[:3]  # Primeros 3 cursos
        if cursos:
            eventos_especificos = [
                {
                    'titulo': 'Prueba de Matemáticas',
                    'descripcion': 'Evaluación de contenidos del primer semestre',
                    'fecha': hoy + timedelta(days=3),
                    'hora_inicio': time(8, 0),
                    'hora_fin': time(9, 30),
                    'tipo_evento': 'evaluacion',
                    'prioridad': 'alta',
                    'para_todos_los_cursos': False
                },
                {
                    'titulo': 'Trabajo en Grupo - Historia',
                    'descripcion': 'Presentación de trabajos grupales',
                    'fecha': hoy + timedelta(days=5),
                    'hora_inicio': time(10, 0),
                    'hora_fin': time(11, 30),
                    'tipo_evento': 'evaluacion',
                    'prioridad': 'media',
                    'para_todos_los_cursos': False
                }
            ]
            
            for i, evento_data in enumerate(eventos_especificos):
                evento, created = EventoCalendario.objects.get_or_create(
                    titulo=evento_data['titulo'],
                    defaults={**evento_data, 'creado_por': usuario_admin}
                )
                if created:
                    # Asignar a un curso específico
                    if i < len(cursos):
                        evento.cursos.add(cursos[i])
                    print(f"   ✅ Creado: {evento.titulo} (para {cursos[i] if i < len(cursos) else 'curso específico'})")
        
        # Eventos administrativos
        eventos_admin = [
            {
                'titulo': 'Reunión de Profesores',
                'descripcion': 'Reunión mensual del cuerpo docente',
                'fecha': hoy + timedelta(days=10),
                'hora_inicio': time(15, 30),
                'hora_fin': time(17, 0),
                'tipo_evento': 'administrativo',
                'prioridad': 'media',
                'para_todos_los_cursos': True
            }
        ]
        
        for evento_data in eventos_admin:
            evento, created = EventoCalendario.objects.get_or_create(
                titulo=evento_data['titulo'],
                defaults={**evento_data, 'creado_por': usuario_admin}
            )
            if created:
                print(f"   ✅ Creado: {evento.titulo}")
        
        print(f"   🎯 Total eventos creados: {EventoCalendario.objects.count()}")
        
    except Exception as e:
        print(f"   ❌ Error al crear eventos: {e}")

def mostrar_eventos_existentes():
    """Mostrar eventos existentes"""
    eventos = EventoCalendario.objects.all().order_by('fecha')
    for evento in eventos[:5]:  # Mostrar primeros 5
        cursos_info = ""
        if evento.para_todos_los_cursos:
            cursos_info = "(Todos los cursos)"
        else:
            cursos_nombres = [str(c) for c in evento.cursos.all()]
            cursos_info = f"({', '.join(cursos_nombres)})" if cursos_nombres else "(Sin cursos)"
        
        print(f"   • {evento.titulo} - {evento.fecha} {cursos_info}")
    
    if eventos.count() > 5:
        print(f"   ... y {eventos.count() - 5} eventos más")

def verificar_permisos_usuarios():
    """Verificar qué usuarios pueden acceder al calendario"""
    
    # Administradores
    admins = User.objects.filter(is_superuser=True)
    print(f"   👑 Administradores ({admins.count()}): Acceso completo")
    
    # Directores
    directores = Perfil.objects.filter(tipo_usuario='director')
    print(f"   🏢 Directores ({directores.count()}): Acceso completo")
    
    # Profesores
    profesores = Perfil.objects.filter(tipo_usuario='profesor')
    print(f"   👨‍🏫 Profesores ({profesores.count()}): Crear/ver eventos de sus cursos")
    
    # Estudiantes
    estudiantes = Perfil.objects.filter(tipo_usuario='estudiante')
    print(f"   🎓 Estudiantes ({estudiantes.count()}): Solo ver eventos")
    
    # Mostrar algunos usuarios de ejemplo
    print("\n   📋 USUARIOS DE EJEMPLO:")
    
    for perfil in Perfil.objects.all()[:3]:
        user = perfil.user
        print(f"   • {user.username} ({perfil.tipo_usuario}) - email: {user.email}")

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    print("\n🔧 VERIFICANDO DEPENDENCIAS")
    
    try:
        import django
        print(f"   ✅ Django: {django.get_version()}")
    except ImportError:
        print("   ❌ Django no está instalado")
    
    # Verificar base de datos
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("   ✅ Base de datos: Conectada")
    except Exception as e:
        print(f"   ❌ Base de datos: Error - {e}")

if __name__ == '__main__':
    verificar_dependencias()
    verificar_calendario()
    
    print(f"\n🚀 Para probar el calendario:")
    print("   1. Ejecuta: python manage.py runserver")
    print("   2. Ve a: http://localhost:8000/calendario/")
    print("   3. Inicia sesión con un usuario administrador")
    print("\n📝 Nota: Si no tienes usuarios, crea uno con:")
    print("   python manage.py createsuperuser")
