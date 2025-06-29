#!/usr/bin/env python3
"""
Script para verificar URLs de horarios
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

def test_horarios_urls():
    """Test URLs relacionadas con horarios"""
    print("=" * 50)
    print("VERIFICACIÓN DE URLs DE HORARIOS")
    print("=" * 50)
    
    try:
        # Verificar que la URL existe
        url = reverse('seleccionar_curso_horarios')
        print(f"✅ URL 'seleccionar_curso_horarios' encontrada: {url}")
        
        # Crear cliente y hacer login
        client = Client()
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            client.login(username='admin', password='admin123')
            
            # Probar acceso a la URL
            response = client.get(url)
            print(f"✅ Respuesta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Página de horarios accesible")
            else:
                print(f"❌ Error al acceder a horarios: {response.status_code}")
        
        # Verificar otras URLs de horarios
        try:
            url2 = reverse('gestionar_horarios', kwargs={'curso_id': 1})
            print(f"✅ URL 'gestionar_horarios' encontrada: {url2}")
        except:
            print("❌ URL 'gestionar_horarios' no encontrada o requiere parámetros")
            
        try:
            url3 = reverse('mis_horarios')
            print(f"✅ URL 'mis_horarios' encontrada: {url3}")
        except:
            print("❌ URL 'mis_horarios' no encontrada")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_horarios_urls()
