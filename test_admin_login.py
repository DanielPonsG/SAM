#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
    django.setup()

    from django.contrib.auth.models import User
    from smapp.models import Perfil

    try:
        # Probar autenticación
        from django.contrib.auth import authenticate
        
        user = authenticate(username='admin', password='admin123')
        if user:
            print(f"✅ Login exitoso para usuario: {user.username}")
            print(f"  - Es superuser: {user.is_superuser}")
            print(f"  - Está activo: {user.is_active}")
            
            # Verificar perfil
            try:
                perfil = user.perfil
                print(f"  - Tipo de usuario: {perfil.tipo_usuario}")
                print(f"  - Perfil completo: {perfil}")
            except Exception as e:
                print(f"  - Error con perfil: {e}")
        else:
            print("❌ Error en el login - credenciales incorrectas")
        
        # Verificar que puede acceder a vistas de admin
        print("\n--- Verificando permisos ---")
        
        # Simular request mock
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        if user and hasattr(user, 'perfil'):
            tipo = user.perfil.tipo_usuario
            print(f"Tipo de usuario en perfil: {tipo}")
            
            # Verificar si cumple con los requisitos del decorador
            if tipo == 'director':
                print("✅ Usuario cumple requisitos para acceso administrativo")
            else:
                print("❌ Usuario NO cumple requisitos para acceso administrativo")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
