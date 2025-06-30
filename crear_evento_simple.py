#!/usr/bin/env python
"""
Script simple para crear un evento de prueba
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, User
from datetime import date

try:
    # Buscar un usuario
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.filter(is_staff=True).first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("❌ No hay usuarios en el sistema")
        exit(1)
    
    # Crear evento simple
    evento = EventoCalendario.objects.create(
        titulo="Evento de Prueba Básico",
        descripcion="Evento para probar el calendario",
        fecha=date.today(),
        tipo_evento="general",
        prioridad="media",
        para_todos_los_cursos=True,
        solo_profesores=False,
        creado_por=user
    )
    
    print(f"✅ Evento creado: {evento.titulo} (ID: {evento.id})")
    print(f"📅 Total eventos: {EventoCalendario.objects.count()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
