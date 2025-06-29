#!/usr/bin/env python
"""
Script para detectar y corregir el error profesor.usuario en el template
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
from django.template import Context, Template
from django.template.loader import get_template

def test_template_error():
    """Probar y corregir el error del template"""
    print("=== DIAGNÓSTICO DEL ERROR profesor.usuario ===")
    
    # Crear datos de prueba
    try:
        # Crear usuario admin
        admin_user, created = User.objects.get_or_create(
            username='admin_debug',
            defaults={
                'password': 'admin123',
                'email': 'admin@debug.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Crear perfil admin
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={'tipo_usuario': 'admin'}
        )
        
        # Crear profesor de prueba sin usuario relacionado
        profesor = Profesor.objects.create(
            primer_nombre='Test',
            apellido_paterno='Profesor',
            codigo_profesor='TEST001',
            numero_documento='12345678-9',
            fecha_nacimiento='1980-01-01',
            genero='M',
            email='test@profesor.com',
            especialidad='Matemáticas'
            # Notar que NO se asigna user aquí para simular el problema
        )
        
        # Crear asignatura de prueba
        asignatura = Asignatura.objects.create(
            nombre='Test Asignatura',
            codigo_asignatura='TEST-001',
            descripcion='Asignatura de prueba'
        )
        
        # Asignar profesor a la asignatura
        asignatura.profesores_responsables.add(profesor)
        
        print(f"✓ Datos de prueba creados:")
        print(f"  - Profesor: {profesor.get_nombre_completo()}")
        print(f"  - Asignatura: {asignatura.nombre}")
        print(f"  - Profesor tiene 'user': {hasattr(profesor, 'user')}")
        print(f"  - Valor de profesor.user: {getattr(profesor, 'user', 'NO DISPONIBLE')}")
        
        # Probar el template con datos reales
        client = Client()
        client.login(username='admin_debug', password='admin123')
        
        response = client.get(f'/asignaturas/editar/{asignatura.id}/')
        
        print(f"\nRespuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Template se renderizó exitosamente")
        else:
            print(f"❌ Error en template: {response.status_code}")
            
            # Probar renderizado manual del template
            try:
                template = get_template('editar_asignatura.html')
                context = {
                    'asignatura': asignatura,
                    'form': None,  # Para probar solo la parte que falla
                }
                
                # Intentar renderizar solo la parte problemática
                rendered = template.render(context)
                print("✓ Template renderizado manualmente sin errores")
                
            except Exception as e:
                print(f"❌ Error en renderizado manual: {e}")
                print(f"Tipo de error: {type(e).__name__}")
                
                # Analizar el error específico
                if 'usuario' in str(e):
                    print("🔍 Error confirmado: se está intentando acceder a 'usuario'")
                    print("✅ SOLUCIÓN: Reemplazar todas las referencias a 'profesor.usuario'")
                    print("   con 'profesor.get_nombre_completo' o 'profesor.codigo_profesor'")
                
    except Exception as e:
        print(f"❌ Error en la creación de datos de prueba: {e}")
        
    finally:
        # Limpiar datos de prueba
        print("\n=== LIMPIEZA ===")
        try:
            Asignatura.objects.filter(codigo_asignatura='TEST-001').delete()
            Profesor.objects.filter(codigo_profesor='TEST001').delete()
            User.objects.filter(username='admin_debug').delete()
            print("✓ Datos de prueba eliminados")
        except Exception as e:
            print(f"⚠ Error al limpiar: {e}")

def verify_template_fixes():
    """Verificar que todas las referencias a profesor.usuario estén corregidas"""
    print("\n=== VERIFICACIÓN DE CORRECCIONES ===")
    
    template_path = 'templates/editar_asignatura.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar referencias problemáticas
        problematic_refs = [
            'profesor.usuario',
            'profesor.user.username',
            'profesor.user.get_full_name',
            '{% for profesor in profesores %}{{ profesor.usuario',
        ]
        
        found_issues = []
        for ref in problematic_refs:
            if ref in content:
                found_issues.append(ref)
        
        if found_issues:
            print("❌ Se encontraron referencias problemáticas:")
            for issue in found_issues:
                print(f"  - {issue}")
        else:
            print("✅ No se encontraron referencias problemáticas")
        
        # Verificar que se usan las referencias correctas
        correct_refs = [
            'profesor.get_nombre_completo',
            'profesor.codigo_profesor',
            'profesor.primer_nombre',
            'profesor.apellido_paterno'
        ]
        
        found_correct = []
        for ref in correct_refs:
            if ref in content:
                found_correct.append(ref)
        
        if found_correct:
            print("✅ Se encontraron referencias correctas:")
            for ref in found_correct:
                print(f"  - {ref}")
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {template_path}")
    except Exception as e:
        print(f"❌ Error al verificar template: {e}")

if __name__ == '__main__':
    print("🔧 DIAGNÓSTICO Y CORRECCIÓN DE ERROR profesor.usuario")
    print("=" * 60)
    
    test_template_error()
    verify_template_fixes()
    
    print("\n" + "=" * 60)
    print("📋 RECOMENDACIONES:")
    print("1. Reemplazar todas las referencias 'profesor.usuario' por 'profesor.get_nombre_completo'")
    print("2. Usar 'profesor.codigo_profesor' como fallback si no hay nombre")
    print("3. Verificar que el modelo Profesor tenga el método get_nombre_completo()")
    print("4. Asegurar que el formulario use SelectMultiple en lugar de CheckboxSelectMultiple")
