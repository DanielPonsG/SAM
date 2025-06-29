#!/usr/bin/env python3
"""
Script para generar HTML de debug final
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

def generar_html_debug_final():
    """Generar archivo HTML para debug manual"""
    print("=== GENERANDO HTML DE DEBUG FINAL ===\n")
    
    # Login
    user = User.objects.get(username='test_admin')
    client = Client()
    client.login(username='test_admin', password='test123')
    
    # Obtener contenido de seleccionar_curso_horarios
    response = client.get('/horarios/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Guardar HTML para inspección manual
        with open('debug_seleccionar_curso_horarios_final.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ HTML guardado en: debug_seleccionar_curso_horarios_final.html")
        
        # Estadísticas básicas
        import re
        
        # Contar elementos importantes
        total_h5 = len(re.findall(r'<h5[^>]*>', content))
        total_buttons = len(re.findall(r'<a[^>]*btn[^>]*>', content))
        total_cards = len(re.findall(r'class="card h-100', content))
        total_href = len(re.findall(r'href="[^"]*"', content))
        
        print(f"Estadísticas del HTML:")
        print(f"- Elementos H5: {total_h5}")
        print(f"- Botones/Enlaces: {total_buttons}")
        print(f"- Cards: {total_cards}")
        print(f"- Total href: {total_href}")
        
        # Buscar específicamente gestionar_horarios
        gestionar_links = re.findall(r'href="[^"]*gestionar_horarios[^"]*"', content)
        print(f"- Enlaces gestionar_horarios: {len(gestionar_links)}")
        
        # Buscar enlaces a cursos
        curso_links = re.findall(r'href="[^"]*cursos/\d+[^"]*"', content)
        print(f"- Enlaces a cursos: {len(curso_links)}")
        
        # Buscar fragmentos específicos
        if 'Cursos Disponibles' in content:
            match = re.search(r'<h3[^>]*>(\d+)</h3>\s*<p[^>]*>Cursos Disponibles</p>', content)
            if match:
                print(f"- Cursos disponibles mostrados: {match.group(1)}")
        
        # Mostrar una muestra del contenido cerca de las cards
        cards_match = re.search(r'(class="card h-100.*?</div>\s*</div>)', content, re.DOTALL)
        if cards_match:
            print("\nMuestra de contenido de card:")
            sample = cards_match.group(1)[:500]
            print(sample)
        
    else:
        print(f"❌ Error obteniendo HTML: {response.status_code}")

if __name__ == '__main__':
    generar_html_debug_final()
