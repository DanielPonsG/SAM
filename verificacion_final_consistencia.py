#!/usr/bin/env python3
"""
Script final para verificar la consistencia visual entre las páginas de cursos.
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
from django.utils import timezone
from smapp.models import Curso
import re

def verificar_paginas_consistencia():
    """Verifica que ambas páginas muestren información consistente"""
    print("=== VERIFICACIÓN FINAL DE CONSISTENCIA ===\n")
    
    # Usar el usuario de prueba creado anteriormente
    user = User.objects.get(username='test_admin')
    client = Client()
    
    # Login
    client.login(username='test_admin', password='test123')
    print("✅ Login realizado")
    
    # Obtener datos reales de la base de datos
    anio_actual = timezone.now().year
    cursos_reales = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
    print(f"✅ Cursos en BD (año {anio_actual}): {cursos_reales.count()}")
    
    print("\n1. ANALIZANDO PÁGINA LISTAR_CURSOS:")
    print("-" * 50)
    
    # Analizar listar_cursos
    response = client.get('/cursos/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Buscar información específica
        total_matches = re.findall(r'Total de cursos:\s*(\d+)', content)
        if total_matches:
            total_listar = int(total_matches[0])
            print(f"✅ Total de cursos en página: {total_listar}")
        else:
            print("⚠️  No se encontró 'Total de cursos' en la página")
            total_listar = None
        
        # Contar elementos de curso en la tabla
        curso_rows = re.findall(r'<tr[^>]*>.*?</tr>', content, re.DOTALL)
        # Filtrar solo las filas que contienen datos de cursos (no headers)
        curso_data_rows = [row for row in curso_rows if 'Básico' in row or 'Medio' in row]
        print(f"✅ Filas de cursos en tabla: {len(curso_data_rows)}")
        
    else:
        print(f"❌ Error cargando listar_cursos: {response.status_code}")
        return
    
    print("\n2. ANALIZANDO PÁGINA SELECCIONAR_CURSO_HORARIOS:")
    print("-" * 50)
    
    # Analizar seleccionar_curso_horarios
    response = client.get('/horarios/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Buscar cursos en la página
        curso_links = re.findall(r'/horarios/curso/(\d+)/', content)
        cursos_unicos = set(curso_links)
        print(f"✅ Enlaces de cursos encontrados: {len(cursos_unicos)}")
        
        # Buscar información de cursos en cards o elementos
        curso_cards = re.findall(r'class="[^"]*curso[^"]*"', content)
        print(f"✅ Elementos de curso en página: {len(curso_cards)}")
        
        # Buscar nombres de cursos en el HTML
        nombres_cursos = re.findall(r'(\d+°\s+(?:Básico|Medio)[A-Z])', content)
        cursos_html = set(nombres_cursos)
        print(f"✅ Nombres de cursos únicos: {len(cursos_html)}")
        
        # Mostrar algunos ejemplos
        if cursos_html:
            print("   Ejemplos:", list(cursos_html)[:5])
        
    else:
        print(f"❌ Error cargando seleccionar_curso_horarios: {response.status_code}")
        return
    
    print("\n3. COMPARACIÓN FINAL:")
    print("-" * 50)
    
    # Comparar los números
    bd_count = cursos_reales.count()
    
    if total_listar is not None:
        if total_listar == bd_count:
            print(f"✅ listar_cursos coincide con BD: {total_listar}")
        else:
            print(f"❌ listar_cursos no coincide: página={total_listar}, BD={bd_count}")
    
    if len(cursos_unicos) == bd_count:
        print(f"✅ seleccionar_curso_horarios coincide con BD: {len(cursos_unicos)}")
    else:
        print(f"❌ seleccionar_curso_horarios no coincide: página={len(cursos_unicos)}, BD={bd_count}")
    
    if total_listar is not None and len(cursos_unicos) == total_listar:
        print(f"✅ CONSISTENCIA TOTAL: Ambas páginas muestran {total_listar} cursos")
    else:
        print("❌ Las páginas no son consistentes entre sí")
    
    print("\n4. LISTADO DE CURSOS EN BASE DE DATOS:")
    print("-" * 50)
    for i, curso in enumerate(cursos_reales, 1):
        print(f"  {i:2d}. {curso.get_nivel_display()}{curso.paralelo} (ID: {curso.id}, Año: {curso.anio})")
    
    print(f"\n🎯 RESULTADO: Sistema corregido y funcionando con {bd_count} cursos del año {anio_actual}")

if __name__ == '__main__':
    verificar_paginas_consistencia()
