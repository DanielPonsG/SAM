#!/usr/bin/env python3
"""
Script para probar las funcionalidades del calendario por tipo de usuario
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
from django.test import Client
from django.urls import reverse

def probar_calendario_admin():
    """Probar funcionalidades de administrador"""
    print("👑 PROBANDO FUNCIONALIDADES DE ADMINISTRADOR")
    print("-" * 50)
    
    client = Client()
    
    # Buscar usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuarios administrador")
        return
    
    # Iniciar sesión
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        print(f"⚠️ No se pudo iniciar sesión con {admin_user.username}")
        print("   Probando con contraseña alternativa...")
        login_success = client.login(username=admin_user.username, password='admin')
    
    if login_success:
        print(f"✅ Sesión iniciada como {admin_user.username}")
        
        # Probar acceso al calendario
        response = client.get('/calendario/')
        if response.status_code == 200:
            print("✅ Acceso al calendario: OK")
            
            # Verificar que puede ver todos los eventos
            context = response.context
            eventos = context.get('eventos', [])
            print(f"   • Puede ver {len(eventos)} eventos")
            
            # Verificar permisos de creación
            puede_crear = context.get('puede_crear_eventos', False)
            print(f"   • Puede crear eventos: {'SÍ' if puede_crear else 'NO'}")
            
            # Verificar cursos disponibles
            cursos = context.get('cursos', [])
            print(f"   • Cursos disponibles: {len(cursos)}")
            
        else:
            print(f"❌ Error al acceder al calendario: {response.status_code}")
    else:
        print(f"❌ No se pudo iniciar sesión como administrador")

def probar_calendario_profesor():
    """Probar funcionalidades de profesor"""
    print("\n👨‍🏫 PROBANDO FUNCIONALIDADES DE PROFESOR")
    print("-" * 50)
    
    client = Client()
    
    # Buscar usuario profesor
    prof_perfil = Perfil.objects.filter(tipo_usuario='profesor').first()
    if not prof_perfil:
        print("❌ No hay usuarios profesor")
        return
    
    prof_user = prof_perfil.user
    
    # Intentar login con contraseñas comunes
    passwords = ['profesor123', 'profesor', 'password', '123456']
    login_success = False
    
    for password in passwords:
        if client.login(username=prof_user.username, password=password):
            login_success = True
            print(f"✅ Sesión iniciada como {prof_user.username}")
            break
    
    if login_success:
        # Probar acceso al calendario
        response = client.get('/calendario/')
        if response.status_code == 200:
            print("✅ Acceso al calendario: OK")
            
            context = response.context
            eventos = context.get('eventos', [])
            puede_crear = context.get('puede_crear_eventos', False)
            cursos = context.get('cursos', [])
            
            print(f"   • Puede ver {len(eventos)} eventos")
            print(f"   • Puede crear eventos: {'SÍ' if puede_crear else 'NO'}")
            print(f"   • Cursos asignados: {len(cursos)}")
            
        else:
            print(f"❌ Error al acceder al calendario: {response.status_code}")
    else:
        print(f"⚠️ No se pudo iniciar sesión como profesor")
        print("   Esto es normal si no se han configurado contraseñas específicas")

def probar_calendario_estudiante():
    """Probar funcionalidades de estudiante"""
    print("\n🎓 PROBANDO FUNCIONALIDADES DE ESTUDIANTE")
    print("-" * 50)
    
    client = Client()
    
    # Buscar usuario estudiante
    est_perfil = Perfil.objects.filter(tipo_usuario='estudiante').first()
    if not est_perfil:
        print("❌ No hay usuarios estudiante")
        return
    
    est_user = est_perfil.user
    
    # Intentar login
    passwords = ['estudiante123', 'estudiante', 'password', '123456']
    login_success = False
    
    for password in passwords:
        if client.login(username=est_user.username, password=password):
            login_success = True
            print(f"✅ Sesión iniciada como {est_user.username}")
            break
    
    if login_success:
        # Probar acceso al calendario
        response = client.get('/calendario/')
        if response.status_code == 200:
            print("✅ Acceso al calendario: OK")
            
            context = response.context
            eventos = context.get('eventos', [])
            puede_crear = context.get('puede_crear_eventos', False)
            
            print(f"   • Puede ver {len(eventos)} eventos")
            print(f"   • Puede crear eventos: {'NO' if not puede_crear else 'SÍ'}")
            
        else:
            print(f"❌ Error al acceder al calendario: {response.status_code}")
    else:
        print(f"⚠️ No se pudo iniciar sesión como estudiante")

def mostrar_eventos_disponibles():
    """Mostrar todos los eventos disponibles"""
    print("\n📋 EVENTOS DISPONIBLES EN EL SISTEMA")
    print("-" * 50)
    
    eventos = EventoCalendario.objects.all().order_by('fecha')
    
    for evento in eventos:
        tipo_icon = {
            'general': '📅',
            'evaluacion': '📝',
            'reunion': '👥',
            'actividad': '🎯',
            'administrativo': '📊',
            'otro': '❓'
        }.get(evento.tipo_evento, '📅')
        
        audiencia = "Todos los cursos" if evento.para_todos_los_cursos else f"{evento.cursos.count()} cursos específicos"
        
        hora_info = ""
        if evento.hora_inicio:
            hora_info = f" a las {evento.hora_inicio.strftime('%H:%M')}"
            if evento.hora_fin:
                hora_info += f" - {evento.hora_fin.strftime('%H:%M')}"
        
        print(f"   {tipo_icon} {evento.titulo}")
        print(f"      📅 Fecha: {evento.fecha}{hora_info}")
        print(f"      👥 Audiencia: {audiencia}")
        print(f"      🎯 Tipo: {evento.get_tipo_evento_display()}")
        print()

def crear_evento_prueba():
    """Crear un evento de prueba usando POST"""
    print("\n➕ CREANDO EVENTO DE PRUEBA")
    print("-" * 50)
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if admin_user and client.login(username=admin_user.username, password='admin123'):
        # Datos del evento
        evento_data = {
            'titulo': 'Evento de Prueba Automatizado',
            'descripcion': 'Este evento fue creado automáticamente para probar el sistema',
            'fecha': (date.today() + timedelta(days=15)).isoformat(),
            'hora_inicio': '10:00',
            'hora_fin': '11:30',
            'tipo_evento': 'general',
            'prioridad': 'media',
            'dirigido_a': 'todos'
        }
        
        # Enviar POST con AJAX headers
        response = client.post('/calendario/', 
                             data=evento_data,
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        if response.status_code == 200:
            import json
            result = json.loads(response.content)
            if result.get('success'):
                print("✅ Evento creado exitosamente")
                print(f"   • ID del evento: {result.get('evento_id')}")
            else:
                print(f"❌ Error al crear evento: {result.get('error')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    else:
        print("❌ No se pudo iniciar sesión para crear evento de prueba")

def mostrar_informacion_usuarios():
    """Mostrar información de usuarios para testing"""
    print("\n🔑 INFORMACIÓN DE USUARIOS PARA TESTING")
    print("-" * 50)
    
    print("👑 ADMINISTRADORES:")
    for user in User.objects.filter(is_superuser=True):
        print(f"   • Usuario: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Contraseñas sugeridas: admin123, admin, password")
    
    print("\n👨‍🏫 PROFESORES:")
    for perfil in Perfil.objects.filter(tipo_usuario='profesor')[:3]:
        user = perfil.user
        print(f"   • Usuario: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Contraseñas sugeridas: profesor123, profesor, password")
    
    print("\n🎓 ESTUDIANTES:")
    for perfil in Perfil.objects.filter(tipo_usuario='estudiante')[:3]:
        user = perfil.user
        print(f"   • Usuario: {user.username}")
        print(f"     Email: {user.email}")
        print(f"     Contraseñas sugeridas: estudiante123, estudiante, password")

if __name__ == '__main__':
    print("🧪 PRUEBAS DEL SISTEMA DE CALENDARIO")
    print("=" * 60)
    
    mostrar_informacion_usuarios()
    mostrar_eventos_disponibles()
    
    # Probar funcionalidades por tipo de usuario
    probar_calendario_admin()
    probar_calendario_profesor()
    probar_calendario_estudiante()
    
    # Crear evento de prueba
    crear_evento_prueba()
    
    print("\n🏁 PRUEBAS COMPLETADAS")
    print("\n📝 PARA PROBAR MANUALMENTE:")
    print("1. Inicia el servidor: python manage.py runserver")
    print("2. Ve a: http://localhost:8000/login/")
    print("3. Usa las credenciales mostradas arriba")
    print("4. Ve al calendario: http://localhost:8000/calendario/")
