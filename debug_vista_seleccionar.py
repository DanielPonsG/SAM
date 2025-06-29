#!/usr/bin/env python3
"""
Script para debug de la vista seleccionar_curso_horarios
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from smapp.models import Curso, HorarioCurso, Asignatura
from smapp.views import seleccionar_curso_horarios

def debug_vista_seleccionar_curso():
    """Debug completo de la vista seleccionar_curso_horarios"""
    print("=== DEBUG VISTA SELECCIONAR_CURSO_HORARIOS ===\n")
    
    # Obtener usuario
    user = User.objects.get(username='test_admin')
    
    # Crear request
    factory = RequestFactory()
    request = factory.get('/horarios/')
    request.user = user
    
    print("1. EJECUTANDO VISTA PASO A PASO:")
    print("-" * 50)
    
    try:
        # Simular el contenido de la vista paso a paso
        from django.utils import timezone
        
        # Paso 1: Obtener cursos del año actual
        anio_actual = timezone.now().year
        cursos_queryset = Curso.objects.filter(anio=anio_actual)
        print(f"✅ Cursos queryset count: {cursos_queryset.count()}")
        
        # Paso 2: Ordenar correctamente
        cursos = sorted(cursos_queryset, key=lambda c: (c.orden_nivel, c.paralelo))
        print(f"✅ Cursos ordenados: {len(cursos)}")
        
        # Paso 3: Preparar información de cursos
        cursos_info = []
        total_horarios = 0
        total_asignaturas = Asignatura.objects.count()
        
        print(f"✅ Total asignaturas en sistema: {total_asignaturas}")
        
        for i, curso in enumerate(cursos):
            try:
                horarios_count = HorarioCurso.objects.filter(curso=curso).count()
                asignaturas_count = curso.asignaturas.count()
                estudiantes_count = curso.estudiantes.count()
                
                total_horarios += horarios_count
                
                info = {
                    'curso': curso,
                    'horarios_count': horarios_count,
                    'asignaturas_count': asignaturas_count,
                    'estudiantes_count': estudiantes_count,
                }
                cursos_info.append(info)
                
                if i < 3:  # Solo mostrar primeros 3 para debug
                    print(f"   Curso {i+1}: {curso.get_nivel_display()}{curso.paralelo}")
                    print(f"     Horarios: {horarios_count}")
                    print(f"     Asignaturas: {asignaturas_count}")
                    print(f"     Estudiantes: {estudiantes_count}")
                
            except Exception as e:
                print(f"❌ Error procesando curso {curso}: {e}")
                info = {
                    'curso': curso,
                    'horarios_count': 0,
                    'asignaturas_count': 0,
                    'estudiantes_count': 0,
                }
                cursos_info.append(info)
        
        print(f"✅ cursos_info preparado: {len(cursos_info)} elementos")
        print(f"✅ total_horarios: {total_horarios}")
        
        # Paso 4: Preparar contexto
        total_cursos = len(cursos)
        total_estudiantes_asignados = sum(curso.estudiantes.count() for curso in cursos)
        
        context = {
            'cursos_info': cursos_info,
            'cursos': cursos,
            'total_cursos': total_cursos,
            'total_estudiantes_asignados': total_estudiantes_asignados,
            'anio_actual': anio_actual,
            'total_horarios': total_horarios,
            'total_asignaturas': total_asignaturas,
        }
        
        print(f"✅ Contexto preparado con {len(context)} claves")
        for key in context.keys():
            if key == 'cursos_info':
                print(f"   {key}: {len(context[key])} elementos")
            elif key == 'cursos':
                print(f"   {key}: {len(context[key])} elementos")
            else:
                print(f"   {key}: {context[key]}")
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. LLAMANDO VISTA REAL:")
    print("-" * 50)
    
    try:
        response = seleccionar_curso_horarios(request)
        print(f"✅ Vista ejecutada, status: {response.status_code}")
        
        # Verificar si hay contexto
        if hasattr(response, 'context_data'):
            print(f"✅ Contexto disponible: {list(response.context_data.keys())}")
        else:
            print("⚠️  No hay context_data disponible (normal para render)")
            
    except Exception as e:
        print(f"❌ Error ejecutando vista: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_vista_seleccionar_curso()
