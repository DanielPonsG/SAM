#!/usr/bin/env python3
"""
Script para verificar que el menú "Gestionar Horarios" se agregó correctamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Perfil, Curso, Asignatura

def test_menu_horarios():
    """Test que verifica que el menú de horarios está disponible"""
    print("=" * 60)
    print("VERIFICACIÓN DEL MENÚ GESTIONAR HORARIOS")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    try:
        # 1. Verificar que existe un usuario administrador
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("❌ Error: No existe usuario administrador")
            return False
            
        # 2. Hacer login como administrador
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ Error: No se pudo hacer login como administrador")
            return False
            
        print("✅ Login exitoso como administrador")
        
        # 3. Obtener la página principal
        response = client.get('/')
        if response.status_code != 200:
            print(f"❌ Error: No se pudo acceder a inicio (status: {response.status_code})")
            return False
            
        print("✅ Acceso exitoso a página de inicio")
        
        # 4. Verificar que el menú contiene "Gestionar Horarios"
        content = response.content.decode('utf-8')
        if 'Gestionar Horarios' in content:
            print("✅ Menú 'Gestionar Horarios' encontrado en la página")
        else:
            print("❌ Error: Menú 'Gestionar Horarios' NO encontrado en la página")
            return False
            
        # 5. Verificar que el enlace apunta a la URL correcta
        if '/horarios/' in content:
            print("✅ URL '/horarios/' encontrada en el menú")
        else:
            print("❌ Error: URL '/horarios/' NO encontrada")
            return False
            
        # 6. Verificar que el icono está presente
        if 'fas fa-clock' in content:
            print("✅ Icono de reloj (fas fa-clock) encontrado")
        else:
            print("❌ Advertencia: Icono de reloj no encontrado")
            
        # 7. Intentar acceder a la página de gestión de horarios
        response = client.get('/horarios/')
        if response.status_code == 200:
            print("✅ Acceso exitoso a la página de gestión de horarios")
        else:
            print(f"❌ Error: No se pudo acceder a horarios (status: {response.status_code})")
            return False
            
        print("\n" + "=" * 60)
        print("🎉 TODAS LAS VERIFICACIONES EXITOSAS")
        print("   El menú 'Gestionar Horarios' se agregó correctamente")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_menu_horarios()
    sys.exit(0 if success else 1)
