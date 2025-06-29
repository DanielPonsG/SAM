#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de gestión de asignaturas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Curso, HorarioCurso, Perfil
from smapp.forms import AsignaturaForm, AsignaturaCompletaForm
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import authenticate
from django.contrib.messages.storage.fallback import FallbackStorage

def test_asignatura_form():
    """Probar que el formulario AsignaturaForm funcione correctamente"""
    print("=== PRUEBA 1: Formulario AsignaturaForm ===")
    
    # Crear un profesor de prueba si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin_test',
        defaults={'email': 'admin@test.com'}
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        Perfil.objects.create(user=admin_user, tipo_usuario='admin')
    
    profesor, created = Profesor.objects.get_or_create(
        codigo_profesor='PROF001',
        defaults={
            'primer_nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'user': admin_user,
            'especialidad': 'Matemáticas',
            'numero_documento': '12345678',
            'tipo_documento': 'CI'
        }
    )
    
    # Probar formulario básico
    form_data = {
        'nombre': 'Matemáticas Test',
        'codigo_asignatura': 'MAT-TEST',
        'descripcion': 'Asignatura de prueba',
        'profesor_responsable': profesor.id
    }
    
    form = AsignaturaForm(data=form_data)
    if form.is_valid():
        print("✓ AsignaturaForm es válido")
        asignatura = form.save()
        print(f"✓ Asignatura creada: {asignatura.nombre}")
        print(f"✓ Profesor asignado: {asignatura.profesor_responsable}")
        return asignatura
    else:
        print("✗ AsignaturaForm inválido:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return None

def test_asignatura_completa_form():
    """Probar que el formulario AsignaturaCompletaForm funcione correctamente"""
    print("\n=== PRUEBA 2: Formulario AsignaturaCompletaForm ===")
    
    # Crear un curso de prueba
    curso, created = Curso.objects.get_or_create(
        nivel='1M',
        paralelo='A',
        defaults={
            'anio': 2024
        }
    )
    
    # Crear profesor
    admin_user = User.objects.get(username='admin_test')
    profesor = Profesor.objects.get(codigo_profesor='PROF001')
    
    form_data = {
        'nombre': 'Historia Test',
        'codigo_asignatura': 'HIS-TEST',
        'descripcion': 'Asignatura de historia de prueba',
        'profesor_responsable': profesor.id,
        'cursos': [curso.id]
    }
    
    form = AsignaturaCompletaForm(data=form_data)
    if form.is_valid():
        print("✓ AsignaturaCompletaForm es válido")
        asignatura = form.save()
        
        # Manejar relación many-to-many de cursos
        if 'cursos' in form.cleaned_data:
            asignatura.cursos.set(form.cleaned_data['cursos'])
        
        print(f"✓ Asignatura creada: {asignatura.nombre}")
        print(f"✓ Profesor asignado: {asignatura.profesor_responsable}")
        print(f"✓ Cursos asociados: {asignatura.cursos.count()}")
        return asignatura
    else:
        print("✗ AsignaturaCompletaForm inválido:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return None

def test_edicion_asignatura():
    """Probar edición de asignatura existente"""
    print("\n=== PRUEBA 3: Edición de Asignatura ===")
    
    # Buscar una asignatura existente
    try:
        asignatura = Asignatura.objects.first()
        if not asignatura:
            print("✗ No hay asignaturas para editar")
            return False
        
        print(f"Editando asignatura: {asignatura.nombre}")
        
        # Datos para editar
        form_data = {
            'nombre': f'{asignatura.nombre} - Editada',
            'codigo_asignatura': asignatura.codigo_asignatura,
            'descripcion': f'{asignatura.descripcion or ""} - Descripción editada',
            'profesor_responsable': asignatura.profesor_responsable.id if asignatura.profesor_responsable else '',
            'cursos': list(asignatura.cursos.values_list('id', flat=True))
        }
        
        form = AsignaturaCompletaForm(data=form_data, instance=asignatura)
        if form.is_valid():
            print("✓ Formulario de edición válido")
            asignatura_editada = form.save()
            
            # Manejar cursos
            if 'cursos' in form.cleaned_data:
                asignatura_editada.cursos.set(form.cleaned_data['cursos'])
            
            print(f"✓ Asignatura editada exitosamente: {asignatura_editada.nombre}")
            return True
        else:
            print("✗ Formulario de edición inválido:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"✗ Error en edición: {e}")
        return False

def test_asignacion_profesor():
    """Probar asignación de profesor a asignatura"""
    print("\n=== PRUEBA 4: Asignación de Profesor ===")
    
    try:
        # Buscar asignatura sin profesor
        asignatura = Asignatura.objects.filter(profesor_responsable__isnull=True).first()
        if not asignatura:
            # Crear una asignatura sin profesor
            asignatura = Asignatura.objects.create(
                nombre='Sin Profesor Test',
                codigo_asignatura='SP-TEST'
            )
        
        # Buscar un profesor
        profesor = Profesor.objects.first()
        if not profesor:
            print("✗ No hay profesores disponibles")
            return False
        
        print(f"Asignando profesor {profesor.primer_nombre} {profesor.apellido_paterno} a {asignatura.nombre}")
        
        # Simular asignación
        asignatura.profesor_responsable = profesor
        asignatura.save()
        
        print("✓ Profesor asignado exitosamente")
        
        # Verificar que se guardó correctamente
        asignatura.refresh_from_db()
        if asignatura.profesor_responsable == profesor:
            print("✓ Asignación verificada en base de datos")
            return True
        else:
            print("✗ Error: Asignación no se guardó correctamente")
            return False
            
    except Exception as e:
        print(f"✗ Error en asignación: {e}")
        return False

def test_listado_asignaturas():
    """Probar que el listado de asignaturas muestre la información correcta"""
    print("\n=== PRUEBA 5: Listado de Asignaturas ===")
    
    try:
        asignaturas = Asignatura.objects.all().prefetch_related('cursos', 'profesor_responsable')
        
        print(f"Total de asignaturas: {asignaturas.count()}")
        
        for asignatura in asignaturas[:3]:  # Mostrar solo las primeras 3
            print(f"\n- {asignatura.nombre} ({asignatura.codigo_asignatura})")
            print(f"  Profesor: {asignatura.profesor_responsable or 'Sin asignar'}")
            print(f"  Cursos: {asignatura.cursos.count()}")
            
            # Verificar horarios
            horarios = HorarioCurso.objects.filter(asignatura=asignatura)
            print(f"  Horarios: {horarios.count()}")
        
        print("✓ Listado generado exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en listado: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("INICIANDO PRUEBAS DE FUNCIONALIDAD DE ASIGNATURAS")
    print("=" * 60)
    
    resultados = []
    
    # Ejecutar pruebas
    asignatura1 = test_asignatura_form()
    resultados.append(asignatura1 is not None)
    
    asignatura2 = test_asignatura_completa_form()
    resultados.append(asignatura2 is not None)
    
    resultados.append(test_edicion_asignatura())
    resultados.append(test_asignacion_profesor())
    resultados.append(test_listado_asignaturas())
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS:")
    print(f"✓ Exitosas: {sum(resultados)}/{len(resultados)}")
    print(f"✗ Fallidas: {len(resultados) - sum(resultados)}/{len(resultados)}")
    
    if all(resultados):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar los errores arriba.")
    
    print("\nPUEDES PROBAR AHORA EN LA INTERFAZ WEB:")
    print("1. Ve a http://127.0.0.1:8000/login/")
    print("2. Inicia sesión con usuario: admin, contraseña: admin123")
    print("3. Ve a Asignaturas → Listar")
    print("4. Prueba editar una asignatura y asignar un profesor")

if __name__ == '__main__':
    main()
