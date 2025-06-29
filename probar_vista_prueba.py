#!/usr/bin/env python3
"""
Script para probar la vista de prueba
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

def probar_vista_prueba():
    """Probar la vista de prueba"""
    print("=== PROBANDO VISTA DE PRUEBA ===\n")
    
    # Login
    user = User.objects.get(username='test_admin')
    client = Client()
    client.login(username='test_admin', password='test123')
    
    # Probar vista de prueba
    response = client.get('/prueba-cursos/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print("✅ Vista de prueba cargada correctamente")
        
        # Buscar información básica
        if 'Total cursos_info:' in content:
            match = re.search(r'Total cursos_info: (\d+)', content)
            if match:
                total = match.group(1)
                print(f"✅ Total cursos_info: {total}")
        
        # Buscar enlaces
        enlaces = re.findall(r'href="([^"]*gestionar_horarios[^"]*)"', content)
        print(f"✅ Enlaces encontrados: {len(enlaces)}")
        
        # Mostrar algunos enlaces
        for i, enlace in enumerate(enlaces[:5]):
            print(f"   {i+1}. {enlace}")
            
        # Buscar nombres de cursos
        nombres = re.findall(r'<h5>([^<]+)</h5>', content)
        print(f"✅ Nombres de cursos: {len(nombres)}")
        
        for i, nombre in enumerate(nombres[:5]):
            print(f"   {i+1}. {nombre}")
            
    else:
        print(f"❌ Error cargando vista de prueba: {response.status_code}")

if __name__ == '__main__':
    probar_vista_prueba()
