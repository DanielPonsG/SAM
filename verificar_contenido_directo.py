#!/usr/bin/env python3
"""
Script para verificar el contenido exacto de las páginas
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def verificar_contenido_paginas():
    """Verifica el contenido específico de las páginas"""
    print("=== VERIFICACIÓN DE CONTENIDO ESPECÍFICO ===\n")
    
    # Login
    user = User.objects.get(username='test_admin')
    client = Client()
    client.login(username='test_admin', password='test123')
    
    print("1. VERIFICANDO SELECCIONAR_CURSO_HORARIOS:")
    print("-" * 50)
    
    # Verificar seleccionar_curso_horarios
    response = client.get('/horarios/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Buscar elementos específicos
        if 'cursos_info' in content:
            print("✅ La variable cursos_info se está usando en el template")
        else:
            print("❌ No se encuentra cursos_info en el template")
        
        # Buscar si hay cursos mostrándose
        if 'Básico' in content or 'Medio' in content:
            print("✅ Se encuentran nombres de cursos en la página")
        else:
            print("❌ No se encuentran nombres de cursos")
        
        # Buscar enlaces específicos
        if 'gestionar_horarios' in content:
            print("✅ Se encuentran enlaces a gestionar_horarios")
        else:
            print("❌ No se encuentran enlaces a gestionar_horarios")
        
        # Buscar el card de estadísticas
        if 'Cursos Disponibles' in content:
            print("✅ Se encuentra el card de estadísticas")
        else:
            print("❌ No se encuentra el card de estadísticas")
        
        # Buscar bucle for en el template
        if 'for info in cursos_info' in content:
            print("✅ Se encuentra el bucle for del template")
        else:
            print("⚠️  No se encuentra el bucle for visible (normal en HTML renderizado)")
        
        # Buscar si hay contenido del bucle
        import re
        cards = re.findall(r'<div class="card h-100 border shadow-sm">', content)
        print(f"✅ Tarjetas de curso encontradas: {len(cards)}")
        
        # Buscar enlaces específicos
        horario_links = re.findall(r'href="[^"]*gestionar_horarios[^"]*"', content)
        print(f"✅ Enlaces a gestionar_horarios: {len(horario_links)}")
        
        if len(horario_links) > 0:
            print("   Ejemplos de enlaces:", horario_links[:3])
        
    else:
        print(f"❌ Error cargando página: {response.status_code}")
    
    print("\n2. DATOS DESDE LA VISTA:")
    print("-" * 50)
    
    # Simular la llamada directa a la vista
    from smapp.views import seleccionar_curso_horarios
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/horarios/')
    request.user = user
    
    # Llamar a la vista directamente
    try:
        response_direct = seleccionar_curso_horarios(request)
        context = response_direct.context_data if hasattr(response_direct, 'context_data') else {}
        
        # Verificar el contexto
        if 'cursos_info' in context:
            cursos_info = context['cursos_info']
            print(f"✅ cursos_info en contexto: {len(cursos_info)} elementos")
            
            for i, info in enumerate(cursos_info[:5]):  # Solo primeros 5
                curso = info['curso']
                print(f"   {i+1}. {curso.get_nivel_display()}{curso.paralelo} (ID: {curso.id})")
        else:
            print("❌ No se encuentra cursos_info en el contexto")
    
    except Exception as e:
        print(f"❌ Error llamando vista directamente: {e}")

if __name__ == '__main__':
    verificar_contenido_paginas()
