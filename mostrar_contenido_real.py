#!/usr/bin/env python3
"""
Script final para mostrar el contenido real de la página
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
import re

def mostrar_contenido_real():
    """Muestra el contenido HTML real de ambas páginas"""
    print("=== CONTENIDO REAL DE LAS PÁGINAS ===\n")
    
    # Login
    user = User.objects.get(username='test_admin')
    client = Client()
    client.login(username='test_admin', password='test123')
    
    print("1. PÁGINA SELECCIONAR_CURSO_HORARIOS:")
    print("-" * 80)
    
    # Obtener contenido de seleccionar_curso_horarios
    response = client.get('/horarios/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Mostrar estadísticas en la página
        stats_match = re.search(r'<h3[^>]*>(\d+)</h3>\s*<p[^>]*>Cursos Disponibles</p>', content)
        if stats_match:
            cursos_disponibles = stats_match.group(1)
            print(f"✅ Cursos Disponibles mostrados: {cursos_disponibles}")
        
        # Buscar todas las tarjetas de curso
        cards = re.findall(r'<div class="card h-100 border shadow-sm">(.*?)</div>\s*</div>\s*</div>', content, re.DOTALL)
        print(f"✅ Tarjetas de curso encontradas: {len(cards)}")
        
        # Extraer información de cada tarjeta
        for i, card in enumerate(cards[:5]):  # Solo primeras 5
            # Buscar nombre del curso
            title_match = re.search(r'<h5[^>]*card-title[^>]*>([^<]+)</h5>', card)
            if title_match:
                curso_nombre = title_match.group(1).strip()
                print(f"   {i+1}. {curso_nombre}")
                
                # Buscar enlace a gestionar_horarios
                link_match = re.search(r'href="([^"]*gestionar_horarios[^"]*)"', card)
                if link_match:
                    link = link_match.group(1)
                    print(f"      ✅ Enlace: {link}")
                else:
                    print(f"      ❌ Sin enlace")
            else:
                print(f"   {i+1}. ❌ No se pudo extraer nombre")
        
        # Buscar todos los enlaces de gestionar_horarios
        all_links = re.findall(r'href="([^"]*gestionar_horarios[^"]*)"', content)
        print(f"\n✅ Total enlaces gestionar_horarios: {len(all_links)}")
        
        if len(all_links) > 0:
            print("   Enlaces encontrados:")
            for i, link in enumerate(all_links[:5]):
                print(f"     {i+1}. {link}")
        
    else:
        print(f"❌ Error cargando página: {response.status_code}")
    
    print("\n2. PÁGINA LISTAR_CURSOS (Para comparación):")
    print("-" * 80)
    
    # Obtener contenido de listar_cursos
    response = client.get('/cursos/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Contar filas de cursos en la tabla
        table_rows = re.findall(r'<tr[^>]*>.*?</tr>', content, re.DOTALL)
        # Filtrar filas que contienen datos de cursos
        curso_rows = []
        for row in table_rows:
            if ('Básico' in row or 'Medio' in row) and 'gestionar_horarios' in row:
                curso_rows.append(row)
        
        print(f"✅ Filas de cursos en tabla: {len(curso_rows)}")
        
        # Buscar enlaces a gestionar_horarios
        horario_links_listar = re.findall(r'href="([^"]*gestionar_horarios[^"]*)"', content)
        print(f"✅ Enlaces a gestionar_horarios: {len(horario_links_listar)}")
        
    else:
        print(f"❌ Error cargando listar_cursos: {response.status_code}")
    
    print("\n3. RESUMEN FINAL:")
    print("-" * 80)
    
    try:
        print(f"seleccionar_curso_horarios: {len(all_links)} enlaces")
        print(f"listar_cursos: {len(horario_links_listar)} enlaces")
        
        if len(all_links) == len(horario_links_listar):
            print("✅ CONSISTENCIA CONFIRMADA: Ambas páginas tienen la misma cantidad de enlaces")
        else:
            print("❌ INCONSISTENCIA: Diferentes cantidades de enlaces")
            
    except:
        print("⚠️  Error comparando enlaces")

if __name__ == '__main__':
    mostrar_contenido_real()
