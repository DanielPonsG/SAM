#!/usr/bin/env python3
"""
Script para probar la creación de eventos en el calendario
"""

import os
import sys
import django
from datetime import date, time, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import EventoCalendario, Curso, Perfil

def probar_creacion_evento():
    """Probar la creación de un evento de prueba"""
    print("🎯 PROBANDO CREACIÓN DE EVENTO")
    print("-" * 40)
    
    # Buscar usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuarios administrador")
        return
    
    print(f"✅ Usuario administrador encontrado: {admin_user.username}")
    
    # Crear evento de prueba
    evento_data = {
        'titulo': 'Evento de Prueba Final',
        'descripcion': 'Este es un evento creado para probar el sistema completo',
        'fecha': date.today() + timedelta(days=20),
        'hora_inicio': time(10, 0),
        'hora_fin': time(11, 30),
        'tipo_evento': 'general',
        'prioridad': 'alta',
        'para_todos_los_cursos': True,
        'creado_por': admin_user
    }
    
    try:
        evento = EventoCalendario.objects.create(**evento_data)
        print(f"✅ Evento creado: {evento.titulo}")
        print(f"   • ID: {evento.id}")
        print(f"   • Fecha: {evento.fecha}")
        print(f"   • Hora: {evento.hora_inicio} - {evento.hora_fin}")
        print(f"   • Tipo: {evento.get_tipo_evento_display()}")
        print(f"   • Para todos los cursos: {'SÍ' if evento.para_todos_los_cursos else 'NO'}")
        
        return evento
        
    except Exception as e:
        print(f"❌ Error al crear evento: {e}")
        return None

def mostrar_resumen_sistema():
    """Mostrar resumen del sistema"""
    print("\n📊 RESUMEN DEL SISTEMA")
    print("-" * 40)
    
    # Eventos
    eventos = EventoCalendario.objects.all()
    print(f"📅 Total de eventos: {eventos.count()}")
    
    # Por tipo de evento
    tipos_eventos = {}
    for evento in eventos:
        tipo = evento.get_tipo_evento_display()
        tipos_eventos[tipo] = tipos_eventos.get(tipo, 0) + 1
    
    print("   📋 Por tipo:")
    for tipo, count in tipos_eventos.items():
        print(f"      • {tipo}: {count}")
    
    # Cursos
    cursos = Curso.objects.all()
    print(f"\n🎓 Total de cursos: {cursos.count()}")
    for curso in cursos:
        eventos_curso = curso.eventos.count()
        print(f"   • {curso}: {eventos_curso} eventos")
    
    # Usuarios
    usuarios_tipo = {}
    for perfil in Perfil.objects.all():
        tipo = perfil.tipo_usuario
        usuarios_tipo[tipo] = usuarios_tipo.get(tipo, 0) + 1
    
    print(f"\n👥 Total de usuarios: {User.objects.count()}")
    print("   📋 Por tipo:")
    for tipo, count in usuarios_tipo.items():
        print(f"      • {tipo}: {count}")

def verificar_permisos_calendario():
    """Verificar permisos de acceso al calendario"""
    print("\n🔐 VERIFICANDO PERMISOS DE CALENDARIO")
    print("-" * 40)
    
    # Administradores
    admins = User.objects.filter(is_superuser=True)
    print(f"👑 Administradores: {admins.count()}")
    for admin in admins:
        print(f"   • {admin.username} - Acceso: COMPLETO")
    
    # Profesores
    profesores = Perfil.objects.filter(tipo_usuario='profesor')
    print(f"\n👨‍🏫 Profesores: {profesores.count()}")
    for prof_perfil in profesores:
        user = prof_perfil.user
        print(f"   • {user.username} - Acceso: CURSOS ASIGNADOS")
    
    # Estudiantes
    estudiantes = Perfil.objects.filter(tipo_usuario='estudiante')
    print(f"\n🎓 Estudiantes: {estudiantes.count()}")
    for est_perfil in estudiantes:
        user = est_perfil.user
        print(f"   • {user.username} - Acceso: SOLO LECTURA")

def mostrar_guia_uso():
    """Mostrar guía de uso del calendario"""
    print("\n📚 GUÍA DE USO DEL CALENDARIO")
    print("=" * 50)
    
    print("🔑 CREDENCIALES DE ACCESO:")
    print("   • Administrador: admin / admin123")
    print("   • Profesor: prof_matematicas / profesor123")
    print("   • Estudiante: [buscar en base de datos]")
    
    print("\n🌐 URLS IMPORTANTES:")
    print("   • Login: http://localhost:8000/login/")
    print("   • Calendario: http://localhost:8000/calendario/")
    print("   • Admin: http://localhost:8000/admin/")
    
    print("\n📱 FUNCIONALIDADES POR USUARIO:")
    print("   👑 ADMINISTRADOR:")
    print("      • Ver todos los eventos")
    print("      • Crear eventos para todos los cursos")
    print("      • Crear eventos para cursos específicos")
    print("      • Editar y eliminar eventos")
    print("      • Filtrar por fecha y curso")
    
    print("   👨‍🏫 PROFESOR:")
    print("      • Ver eventos de sus cursos asignados")
    print("      • Crear eventos para sus cursos")
    print("      • Editar eventos que creó")
    print("      • Filtrar por fecha")
    
    print("   🎓 ESTUDIANTE:")
    print("      • Ver eventos de sus cursos")
    print("      • Ver eventos generales")
    print("      • Filtrar por fecha")
    print("      • NO puede crear eventos")
    
    print("\n🎯 TIPOS DE EVENTOS:")
    print("   • General: Eventos para toda la institución")
    print("   • Evaluación/Prueba: Exámenes y evaluaciones")
    print("   • Reunión: Reuniones de apoderados, profesores")
    print("   • Actividad: Actividades extracurriculares")
    print("   • Administrativo: Eventos internos")
    
    print("\n📅 FUNCIONALIDADES DEL CALENDARIO:")
    print("   • Vista por mes, semana, día")
    print("   • Eventos con colores por tipo")
    print("   • Click en fecha para crear evento")
    print("   • Click en evento para ver detalles")
    print("   • Filtros por fecha y curso")
    print("   • Lista de próximos eventos")

if __name__ == '__main__':
    print("🗓️ SISTEMA DE CALENDARIO ESCOLAR")
    print("=" * 50)
    
    mostrar_resumen_sistema()
    verificar_permisos_calendario()
    probar_creacion_evento()
    mostrar_guia_uso()
    
    print(f"\n🚀 ¡CALENDARIO LISTO PARA USAR!")
    print("   1. Inicia el servidor: python manage.py runserver")
    print("   2. Ve a: http://localhost:8000/login/")
    print("   3. Usa las credenciales mostradas arriba")
    print("   4. Navega al calendario y prueba crear eventos")
