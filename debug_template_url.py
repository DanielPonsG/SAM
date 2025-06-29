#!/usr/bin/env python3
"""
Script para debug del template URL
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Curso

def debug_template_url():
    """Debug del template URL"""
    print("=== DEBUG TEMPLATE URL ===\n")
    
    # Verificar que las URLs funcionen
    print("1. VERIFICANDO URLs:")
    print("-" * 50)
    
    try:
        # Probar URL sin parámetros
        url_seleccionar = reverse('seleccionar_curso_horarios')
        print(f"✅ seleccionar_curso_horarios: {url_seleccionar}")
        
        # Probar URL con parámetro
        curso_test = Curso.objects.first()
        if curso_test:
            url_gestionar = reverse('gestionar_horarios', args=[curso_test.id])
            print(f"✅ gestionar_horarios (curso {curso_test.id}): {url_gestionar}")
        else:
            print("❌ No hay cursos para probar gestionar_horarios")
            
    except Exception as e:
        print(f"❌ Error con URLs: {e}")
    
    print("\n2. VERIFICANDO TEMPLATE RENDERING:")
    print("-" * 50)
    
    # Crear un template simple para probar
    from django.template import Template, Context
    from django.utils import timezone
    from smapp.models import Curso
    
    # Obtener datos reales
    anio_actual = timezone.now().year
    cursos = Curso.objects.filter(anio=anio_actual)[:3]  # Solo primeros 3
    
    # Preparar cursos_info como lo hace la vista
    cursos_info = []
    for curso in cursos:
        cursos_info.append({
            'curso': curso,
            'horarios_count': 0,
            'asignaturas_count': curso.asignaturas.count(),
            'estudiantes_count': curso.estudiantes.count(),
        })
    
    # Template simple para probar
    template_str = """
    {% load static %}
    {% for info in cursos_info %}
        <div class="curso-card">
            <h5>{{ info.curso.get_nivel_display }}{{ info.curso.paralelo }}</h5>
            <p>Año: {{ info.curso.anio }}</p>
            <p>ID: {{ info.curso.id }}</p>
            <a href="{% url 'gestionar_horarios' info.curso.id %}">Gestionar Horarios</a>
        </div>
    {% endfor %}
    """
    
    try:
        template = Template(template_str)
        context = Context({'cursos_info': cursos_info})
        rendered = template.render(context)
        
        print("✅ Template renderizado exitosamente")
        print("Contenido:")
        print(rendered)
        
        # Verificar si contiene enlaces
        if 'href=' in rendered:
            print("✅ Enlaces generados correctamente")
        else:
            print("❌ No se generaron enlaces")
            
    except Exception as e:
        print(f"❌ Error renderizando template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_template_url()
