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
        # Buscar usuario admin
        admin = User.objects.filter(username='admin').first()
        
        if admin:
            print(f"✓ Usuario admin encontrado: {admin.username}")
            print(f"  - Es superuser: {admin.is_superuser}")
            print(f"  - Está activo: {admin.is_active}")
            
            # Verificar si tiene perfil
            try:
                perfil = admin.perfil
                print(f"  - Tiene perfil: Sí")
                print(f"  - Tipo de usuario: {perfil.tipo_usuario}")
            except Perfil.DoesNotExist:
                print(f"  - Tiene perfil: No")
                # Crear perfil de administrador
                perfil = Perfil.objects.create(
                    user=admin,  # Corregir: es 'user' no 'usuario'
                    tipo_usuario='director',  # Usar 'director' en lugar de 'administrador'
                )
                print(f"  ✓ Perfil de director creado")
            
            # Asegurar que es superuser y está activo
            if not admin.is_superuser:
                admin.is_superuser = True
                admin.save()
                print(f"  ✓ Usuario configurado como superuser")
            
            if not admin.is_active:
                admin.is_active = True
                admin.save()
                print(f"  ✓ Usuario activado")
                
        else:
            print("❌ Usuario admin no encontrado. Creando...")
            # Crear usuario admin
            admin = User.objects.create_user(
                username='admin',
                email='admin@sma.com',
                password='admin123',
                is_superuser=True,
                is_staff=True,
                is_active=True
            )
            print(f"✓ Usuario admin creado: admin/admin123")
            
            # Crear perfil
            perfil = Perfil.objects.create(
                user=admin,  # Corregir: es 'user' no 'usuario'
                tipo_usuario='director',  # Usar 'director' en lugar de 'administrador'
            )
            print(f"✓ Perfil de director creado")
        
        print("\n🎉 Usuario admin configurado correctamente")
        print("Credenciales: admin/admin123")
        print("Tipo de usuario: director (equivale a administrador)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
