#!/usr/bin/env python
"""
Test directo del calendario desde el navegador
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_calendario_view():
    """Probar la vista del calendario directamente"""
    print("🔍 PROBANDO VISTA DEL CALENDARIO")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario administrador disponible")
        return
    
    # Hacer login
    client.force_login(admin_user)
    print(f"✅ Login como: {admin_user.username}")
    
    # Hacer request a la vista del calendario
    response = client.get('/calendario/')
    print(f"📄 Response status: {response.status_code}")
    
    if response.status_code == 200:
        # Verificar contenido
        content = response.content.decode('utf-8')
        
        # Verificar que el modal esté presente
        if 'modalCrearEvento' in content:
            print("✅ Modal de crear evento está presente")
        else:
            print("❌ Modal de crear evento NO encontrado")
        
        # Verificar que los cursos estén en el contexto
        context = response.context
        if context:
            cursos = context.get('cursos', [])
            print(f"📚 Cursos en contexto: {len(cursos)}")
            for curso in cursos[:3]:  # Mostrar solo los primeros 3
                print(f"   - {curso}")
            
            puede_crear = context.get('puede_crear_eventos', False)
            user_type = context.get('user_type', 'desconocido')
            print(f"👤 Tipo de usuario: {user_type}")
            print(f"🔐 Puede crear eventos: {puede_crear}")
        
        # Verificar HTML específico de los checkboxes
        if 'name="cursos_especificos"' in content:
            import re
            checkboxes = re.findall(r'name="cursos_especificos".*?value="(\d+)"', content)
            print(f"✅ Checkboxes de cursos encontrados: {len(checkboxes)}")
            print(f"   IDs de cursos: {checkboxes}")
        else:
            print("❌ No se encontraron checkboxes de cursos específicos")
        
        # Verificar JavaScript
        if 'dirigido_especificos' in content:
            print("✅ JavaScript para mostrar/ocultar cursos está presente")
        else:
            print("❌ JavaScript para cursos NO encontrado")
    
    else:
        print(f"❌ Error en la vista: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Contenido del error: {response.content.decode('utf-8')[:500]}...")
    
    print("\n" + "=" * 50)
    print("✅ TEST COMPLETADO")

if __name__ == "__main__":
    test_calendario_view()
