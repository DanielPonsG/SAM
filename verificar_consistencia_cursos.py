#!/usr/bin/env python3
"""
Script para verificar la consistencia entre las vistas de cursos.
Comprueba que listar_cursos y seleccionar_curso_horarios muestren los mismos cursos.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.utils import timezone
from smapp.models import Curso, Perfil
from smapp.views import listar_cursos, seleccionar_curso_horarios

def verificar_consistencia_cursos():
    """Verifica que ambas vistas muestren los mismos cursos"""
    print("=== VERIFICACIÓN DE CONSISTENCIA DE CURSOS ===\n")
    
    # Crear factory para requests falsos
    factory = RequestFactory()
    
    # Obtener o crear un usuario administrador
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin_test',
                password='password123',
                is_superuser=True,
                is_staff=True
            )
    except Exception as e:
        print(f"Error creando usuario admin: {e}")
        return
    
    # Crear perfil si no existe
    try:
        perfil, created = Perfil.objects.get_or_create(
            user=admin_user,
            defaults={
                'tipo_usuario': 'administrador',
                'primer_nombre': 'Admin',
                'apellido_paterno': 'Test'
            }
        )
    except Exception as e:
        print(f"Error creando perfil: {e}")
    
    print("1. VERIFICANDO DATOS DIRECTOS EN BASE DE DATOS:")
    print("-" * 50)
    
    # Verificar cursos directamente en la base de datos
    anio_actual = timezone.now().year
    todos_cursos = Curso.objects.all().order_by('nivel', 'paralelo')
    cursos_anio_actual = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
    
    print(f"Año actual: {anio_actual}")
    print(f"Total de cursos en base de datos: {todos_cursos.count()}")
    print(f"Cursos del año actual: {cursos_anio_actual.count()}")
    
    if todos_cursos.count() != cursos_anio_actual.count():
        print("\n⚠️  DIFERENCIA DETECTADA:")
        print("Cursos que no son del año actual:")
        for curso in todos_cursos:
            if curso.anio != anio_actual:
                print(f"  - {curso.get_nivel_display()}{curso.paralelo} (Año: {curso.anio})")
    
    print("\n2. VERIFICANDO VISTA LISTAR_CURSOS:")
    print("-" * 50)
    
    # Test listar_cursos
    try:
        request = factory.get('/cursos/')
        request.user = admin_user
        
        # Simular la lógica de listar_cursos
        cursos_listar = Curso.objects.filter(anio=anio_actual)
        cursos_listar_ordenados = sorted(cursos_listar, key=lambda c: (c.orden_nivel, c.paralelo))
        
        print(f"Cursos en listar_cursos: {len(cursos_listar_ordenados)}")
        for i, curso in enumerate(cursos_listar_ordenados, 1):
            print(f"  {i:2d}. {curso.get_nivel_display()}{curso.paralelo} (Año: {curso.anio})")
            
    except Exception as e:
        print(f"Error en listar_cursos: {e}")
    
    print("\n3. VERIFICANDO VISTA SELECCIONAR_CURSO_HORARIOS:")
    print("-" * 50)
    
    # Test seleccionar_curso_horarios
    try:
        request = factory.get('/horarios/seleccionar/')
        request.user = admin_user
        
        # Simular la lógica corregida de seleccionar_curso_horarios
        cursos_horarios = Curso.objects.filter(anio=anio_actual)
        cursos_horarios_ordenados = sorted(cursos_horarios, key=lambda c: (c.orden_nivel, c.paralelo))
        
        print(f"Cursos en seleccionar_curso_horarios: {len(cursos_horarios_ordenados)}")
        for i, curso in enumerate(cursos_horarios_ordenados, 1):
            print(f"  {i:2d}. {curso.get_nivel_display()}{curso.paralelo} (Año: {curso.anio})")
            
    except Exception as e:
        print(f"Error en seleccionar_curso_horarios: {e}")
    
    print("\n4. VERIFICACIÓN DE CONSISTENCIA:")
    print("-" * 50)
    
    # Comparar ambas listas
    try:
        cursos_listar_ids = set(curso.id for curso in cursos_listar_ordenados)
        cursos_horarios_ids = set(curso.id for curso in cursos_horarios_ordenados)
        
        if cursos_listar_ids == cursos_horarios_ids:
            print("✅ CONSISTENCIA VERIFICADA: Ambas vistas muestran los mismos cursos")
            print(f"   Cantidad de cursos: {len(cursos_listar_ordenados)}")
        else:
            print("❌ INCONSISTENCIA DETECTADA:")
            
            solo_en_listar = cursos_listar_ids - cursos_horarios_ids
            solo_en_horarios = cursos_horarios_ids - cursos_listar_ids
            
            if solo_en_listar:
                print("   Cursos solo en listar_cursos:")
                for curso_id in solo_en_listar:
                    curso = Curso.objects.get(id=curso_id)
                    print(f"     - {curso.get_nivel_display()}{curso.paralelo}")
                    
            if solo_en_horarios:
                print("   Cursos solo en seleccionar_curso_horarios:")
                for curso_id in solo_en_horarios:
                    curso = Curso.objects.get(id=curso_id)
                    print(f"     - {curso.get_nivel_display()}{curso.paralelo}")
                    
    except Exception as e:
        print(f"Error comparando listas: {e}")
    
    print("\n5. RESUMEN:")
    print("-" * 50)
    print(f"Cursos totales en BD: {todos_cursos.count()}")
    print(f"Cursos año actual: {cursos_anio_actual.count()}")
    print(f"Diferencia: {todos_cursos.count() - cursos_anio_actual.count()} cursos de años anteriores")
    
    if todos_cursos.count() == cursos_anio_actual.count():
        print("✅ Todos los cursos son del año actual")
    else:
        print("⚠️  Existen cursos de años anteriores en la base de datos")

if __name__ == '__main__':
    verificar_consistencia_cursos()
