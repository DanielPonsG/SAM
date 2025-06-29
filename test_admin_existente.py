#!/usr/bin/env python
"""
Script para probar directamente con un usuario admin existente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Perfil

def test_with_existing_admin():
    """Probar con usuario admin existente"""
    print("=== PRUEBA CON USUARIO ADMIN EXISTENTE ===")
    
    # Buscar usuario admin existente
    admin_users = User.objects.filter(is_superuser=True)
    if not admin_users.exists():
        print("❌ No hay usuarios administradores en la base de datos")
        return
    
    admin_user = admin_users.first()
    print(f"✓ Usuario admin encontrado: {admin_user.username}")
    
    # Buscar asignatura existente
    asignatura = Asignatura.objects.first()
    if not asignatura:
        print("❌ No hay asignaturas en la base de datos")
        return
    
    print(f"✓ Asignatura encontrada: {asignatura.nombre} (ID: {asignatura.id})")
    
    # Verificar profesores responsables
    profesores = asignatura.profesores_responsables.all()
    print(f"✓ Profesores responsables: {profesores.count()}")
    
    for i, profesor in enumerate(profesores):
        print(f"  {i+1}. {profesor.get_nombre_completo()} (código: {profesor.codigo_profesor})")
        print(f"     - User: {profesor.user}")
        print(f"     - Tiene atributo 'usuario': {hasattr(profesor, 'usuario')}")
    
    # Probar acceso con el cliente
    client = Client()
    
    # Intentar login
    try:
        # Como no sabemos la contraseña, vamos a forzar el login
        client.force_login(admin_user)
        print(f"✓ Login forzado exitoso para {admin_user.username}")
        
        # Probar acceso a la vista
        url = f'/asignaturas/editar/{asignatura.id}/'
        response = client.get(url)
        
        print(f"✓ Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 ¡Template se renderizó exitosamente!")
            print("✅ No hay error de profesor.usuario")
            
            # Verificar el contexto
            context_keys = list(response.context.keys()) if response.context else []
            print(f"✓ Claves del contexto: {context_keys}")
            
            if 'form' in response.context:
                form = response.context['form']
                print(f"✓ Formulario presente: {type(form).__name__}")
                
            if 'asignatura' in response.context:
                asig_ctx = response.context['asignatura']
                print(f"✓ Asignatura en contexto: {asig_ctx.nombre}")
            
        elif response.status_code == 403:
            print("❌ Error de permisos (403 Forbidden)")
            print("   El usuario no tiene permisos para editar asignaturas")
            
        elif response.status_code == 500:
            print("❌ Error interno del servidor (500)")
            print("   Posible error en el template o vista")
            
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        print(f"   Tipo: {type(e).__name__}")

def check_template_syntax():
    """Verificar sintaxis del template"""
    print("\n=== VERIFICACIÓN DE SINTAXIS DEL TEMPLATE ===")
    
    from django.template import Template
    from django.template.loader import get_template
    
    try:
        template = get_template('editar_asignatura.html')
        print("✓ Template cargado sin errores de sintaxis")
        
        # Crear contexto mínimo para probar renderizado
        from smapp.forms import AsignaturaForm
        from django.http import HttpRequest
        
        # Crear contexto básico
        context = {
            'form': AsignaturaForm(),
            'asignatura': None,
            'request': HttpRequest(),
        }
        
        # Intentar renderizar
        rendered = template.render(context)
        print("✓ Template renderizado sin errores con contexto básico")
        
        # Verificar que no hay referencias a 'usuario'
        if 'VariableDoesNotExist' in rendered:
            print("❌ Error VariableDoesNotExist encontrado en el renderizado")
        else:
            print("✓ No hay errores VariableDoesNotExist")
            
    except Exception as e:
        print(f"❌ Error en template: {e}")
        print(f"   Tipo: {type(e).__name__}")

if __name__ == '__main__':
    test_with_existing_admin()
    check_template_syntax()
    
    print("\n=== CONCLUSIÓN ===")
    print("Si las pruebas muestran éxito, el error profesor.usuario ya está corregido.")
    print("Si persiste el error, puede ser un problema de permisos o decoradores.")
