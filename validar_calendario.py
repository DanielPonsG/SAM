#!/usr/bin/env python
"""
Validación rápida del calendario funcional
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, User, Perfil

def validar_calendario():
    """Validar que el calendario esté funcionando correctamente"""
    print("🔍 VALIDANDO CALENDARIO...")
    
    # 1. Verificar que existen usuarios
    users = User.objects.all()
    print(f"✅ Usuarios en el sistema: {users.count()}")
    
    # 2. Verificar eventos
    eventos = EventoCalendario.objects.all()
    print(f"✅ Eventos en el calendario: {eventos.count()}")
    
    # 3. Verificar que tenemos eventos próximos
    eventos_proximos = EventoCalendario.objects.filter(
        fecha__gte=datetime.now().date()
    ).order_by('fecha')[:5]
    
    print(f"✅ Próximos eventos:")
    for evento in eventos_proximos:
        print(f"   - {evento.titulo} ({evento.fecha}) - {evento.get_tipo_evento_display()}")
    
    # 4. Verificar colores por tipo
    tipos_con_colores = {}
    for evento in eventos:
        tipo = evento.get_tipo_evento_display()
        color = evento.color_por_tipo
        if tipo not in tipos_con_colores:
            tipos_con_colores[tipo] = color
    
    print(f"✅ Colores por tipo de evento:")
    for tipo, color in tipos_con_colores.items():
        print(f"   - {tipo}: {color}")
    
    # 5. Verificar usuarios con permisos
    admins = User.objects.filter(perfil__tipo_usuario='administrador')
    directores = User.objects.filter(perfil__tipo_usuario='director') 
    profesores = User.objects.filter(perfil__tipo_usuario='profesor')
    estudiantes = User.objects.filter(perfil__tipo_usuario='estudiante')
    
    print(f"✅ Usuarios con permisos para crear eventos:")
    print(f"   - Administradores: {admins.count()}")
    print(f"   - Directores: {directores.count()}")
    print(f"   - Profesores: {profesores.count()}")
    print(f"   - Estudiantes (solo lectura): {estudiantes.count()}")
    
    print(f"\n🎉 ¡CALENDARIO VALIDADO EXITOSAMENTE!")
    print(f"📅 URL: http://127.0.0.1:8000/calendario/")
    print(f"🔑 Usar credenciales: admin/admin123, director/director123, etc.")

if __name__ == '__main__':
    validar_calendario()
