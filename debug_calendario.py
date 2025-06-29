#!/usr/bin/env python
"""
Script de depuración para el calendario - verificar cursos disponibles
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario
from django.utils import timezone

def debug_calendario():
    """Debuggear el calendario para ver qué cursos están disponibles"""
    print("🔍 DEBUG DEL CALENDARIO")
    print("=" * 50)
    
    # 1. Verificar cursos actuales
    print(f"\n📚 CURSOS DEL AÑO {timezone.now().year}:")
    cursos = Curso.objects.filter(anio=timezone.now().year).order_by('nivel', 'paralelo')
    print(f"   Total: {cursos.count()}")
    
    if cursos.count() > 0:
        for curso in cursos:
            print(f"   - {curso} (ID: {curso.id})")
            print(f"     Profesor jefe: {curso.profesor_jefe or 'Sin asignar'}")
            print(f"     Estudiantes: {curso.estudiantes.count()}")
    else:
        print("   ⚠️  No hay cursos disponibles")
    
    # 2. Verificar usuarios administradores
    print(f"\n👤 USUARIOS ADMINISTRADORES:")
    
    # Superusuarios
    superusers = User.objects.filter(is_superuser=True, is_active=True)
    print(f"   Superusuarios: {superusers.count()}")
    for user in superusers:
        print(f"   - {user.username} (Superuser)")
    
    # Usuarios con perfil
    try:
        from smapp.models import Perfil
        admins = User.objects.filter(perfil__tipo_usuario='administrador', is_active=True)
        print(f"   Administradores con perfil: {admins.count()}")
        for user in admins:
            print(f"   - {user.username} (Admin)")
    except Exception as e:
        print(f"   Error obteniendo administradores: {e}")
    
    # 3. Simular vista del calendario
    print(f"\n🌐 SIMULACIÓN DE VISTA CALENDARIO:")
    
    # Tomar el primer usuario administrador disponible
    admin_user = None
    if superusers.exists():
        admin_user = superusers.first()
    
    if admin_user:
        print(f"   Usuario de prueba: {admin_user.username}")
        
        # Simular determinación de tipo de usuario
        user_type = 'otro'
        puede_crear_eventos = False
        
        try:
            if hasattr(admin_user, 'perfil'):
                user_type = admin_user.perfil.tipo_usuario
                puede_crear_eventos = user_type in ['administrador', 'director', 'profesor']
            elif admin_user.is_superuser:
                user_type = 'administrador'
                puede_crear_eventos = True
        except:
            if admin_user.is_superuser:
                user_type = 'administrador'
                puede_crear_eventos = True
        
        print(f"   Tipo de usuario detectado: {user_type}")
        print(f"   Puede crear eventos: {puede_crear_eventos}")
        
        # Obtener cursos según tipo de usuario
        cursos_disponibles = []
        if user_type in ['administrador', 'director']:
            cursos_disponibles = Curso.objects.filter(anio=timezone.now().year).order_by('nivel', 'paralelo')
        
        print(f"   Cursos disponibles para el usuario: {cursos_disponibles.count()}")
        for curso in cursos_disponibles:
            print(f"   - {curso}")
    
    # 4. Verificar template context
    print(f"\n📄 CONTEXT PARA TEMPLATE:")
    context_data = {
        'cursos': list(cursos),
        'puede_crear_eventos': puede_crear_eventos if 'puede_crear_eventos' in locals() else False,
        'user_type': user_type if 'user_type' in locals() else 'otro',
        'tipos_evento': EventoCalendario.TIPO_EVENTO_CHOICES,
        'prioridades': EventoCalendario.PRIORIDAD_CHOICES,
    }
    
    print(f"   cursos: {len(context_data['cursos'])} items")
    print(f"   puede_crear_eventos: {context_data['puede_crear_eventos']}")
    print(f"   user_type: {context_data['user_type']}")
    print(f"   tipos_evento: {len(context_data['tipos_evento'])} opciones")
    print(f"   prioridades: {len(context_data['prioridades'])} opciones")
    
    print("\n" + "=" * 50)
    print("✅ DEBUG COMPLETADO")
    
    if cursos.count() == 0:
        print("\n⚠️  PROBLEMA DETECTADO: No hay cursos disponibles")
        print("💡 SOLUCIÓN: Ejecutar 'python crear_cursos_basicos.py'")
    elif not context_data['puede_crear_eventos']:
        print("\n⚠️  PROBLEMA DETECTADO: Usuario sin permisos")
        print("💡 SOLUCIÓN: Usar un usuario administrador o superusuario")
    else:
        print("\n✅ TODO PARECE ESTAR CORRECTO")
        print("💡 El problema puede estar en el template o JavaScript")

if __name__ == "__main__":
    debug_calendario()
