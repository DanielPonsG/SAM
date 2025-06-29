#!/usr/bin/env python3
"""
Script para verificar las URLs
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def verificar_urls():
    """Verificar que las URLs funcionen"""
    print("=== VERIFICANDO URLs ===\n")
    
    # Probar URL sin parámetros
    try:
        url_seleccionar = reverse('seleccionar_curso_horarios')
        print(f"✅ seleccionar_curso_horarios: {url_seleccionar}")
    except NoReverseMatch as e:
        print(f"❌ Error con seleccionar_curso_horarios: {e}")
    
    # Probar URL con parámetros
    try:
        url_gestionar = reverse('gestionar_horarios', args=[1])
        print(f"✅ gestionar_horarios: {url_gestionar}")
    except NoReverseMatch as e:
        print(f"❌ Error con gestionar_horarios: {e}")
    
    # Probar con diferentes argumentos
    try:
        for curso_id in [1, 15, 20]:
            url = reverse('gestionar_horarios', args=[curso_id])
            print(f"✅ gestionar_horarios(curso {curso_id}): {url}")
    except NoReverseMatch as e:
        print(f"❌ Error con múltiples cursos: {e}")
    
    # Verificar todas las URLs disponibles
    from django.urls import get_resolver
    resolver = get_resolver()
    
    print("\n=== URLs DISPONIBLES ===")
    url_patterns = resolver.url_patterns
    for pattern in url_patterns:
        if hasattr(pattern, 'name') and pattern.name:
            print(f"- {pattern.name}: {pattern.pattern}")

if __name__ == '__main__':
    verificar_urls()
