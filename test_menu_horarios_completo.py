#!/usr/bin/env python3
"""
Script para verificar que el menú "Gestionar Horarios" funciona para diferentes tipos de usuarios
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
from smapp.models import Perfil

def test_menu_horarios_roles():
    """Test que verifica el menú de horarios para diferentes roles"""
    print("=" * 70)
    print("VERIFICACIÓN DEL MENÚ GESTIONAR HORARIOS POR ROLES")
    print("=" * 70)
    
    client = Client()
    
    # Roles a verificar (admin y profesores pueden gestionar horarios)
    roles_to_test = [
        ('admin', 'admin123', 'administrador'),
        ('profesor', 'profesor123', 'profesor')
    ]
    
    for username, password, expected_role in roles_to_test:
        print(f"\n--- Probando usuario: {username} ({expected_role}) ---")
        
        try:
            # Verificar que el usuario existe
            user = User.objects.filter(username=username).first()
            if not user:
                print(f"❌ Usuario {username} no existe")
                continue
                
            # Verificar perfil
            if hasattr(user, 'perfil'):
                actual_role = user.perfil.tipo_usuario
                print(f"✅ Usuario encontrado con rol: {actual_role}")
            else:
                print(f"❌ Usuario {username} no tiene perfil")
                continue
            
            # Hacer login
            login_success = client.login(username=username, password=password)
            if not login_success:
                print(f"❌ No se pudo hacer login como {username}")
                continue
                
            print(f"✅ Login exitoso como {username}")
            
            # Obtener página principal
            response = client.get('/')
            if response.status_code != 200:
                print(f"❌ Error al acceder a inicio (status: {response.status_code})")
                continue
                
            content = response.content.decode('utf-8')
            
            # Verificar menú según el rol
            if actual_role == 'estudiante':
                # Los estudiantes NO deberían ver "Gestionar Horarios"
                if 'Gestionar Horarios' in content:
                    print("❌ ERROR: Estudiante puede ver 'Gestionar Horarios' (no debería)")
                else:
                    print("✅ Estudiante NO ve 'Gestionar Horarios' (correcto)")
            else:
                # Admin y profesores SÍ deberían ver "Gestionar Horarios"
                if 'Gestionar Horarios' in content:
                    print("✅ Menú 'Gestionar Horarios' visible para admin/profesor")
                    
                    # Verificar URL
                    if '/horarios/' in content:
                        print("✅ URL '/horarios/' encontrada")
                    else:
                        print("❌ URL '/horarios/' NO encontrada")
                        
                    # Verificar icono
                    if 'fas fa-clock' in content:
                        print("✅ Icono de reloj encontrado")
                    else:
                        print("❌ Icono de reloj NO encontrado")
                        
                    # Probar acceso a la página
                    response = client.get('/horarios/')
                    if response.status_code == 200:
                        print("✅ Acceso exitoso a página de horarios")
                    else:
                        print(f"❌ Error al acceder a horarios (status: {response.status_code})")
                else:
                    print("❌ ERROR: Admin/profesor NO puede ver 'Gestionar Horarios'")
            
            # Cerrar sesión
            client.logout()
            
        except Exception as e:
            print(f"❌ Error con usuario {username}: {str(e)}")
    
    print("\n" + "=" * 70)
    print("🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    test_menu_horarios_roles()
