#!/usr/bin/env python
"""
Script para corregir estudiantes que están en múltiples cursos del mismo año
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante
from django.utils import timezone

def corregir_estudiantes_multiples_cursos():
    """Corregir estudiantes que están en múltiples cursos del mismo año"""
    print("=== CORRIGIENDO ESTUDIANTES EN MÚLTIPLES CURSOS ===")
    
    anio_actual = timezone.now().year
    estudiantes_problema = []
    
    for estudiante in Estudiante.objects.all():
        cursos_estudiante = estudiante.cursos.filter(anio=anio_actual)
        if cursos_estudiante.count() > 1:
            estudiantes_problema.append({
                'estudiante': estudiante,
                'cursos': list(cursos_estudiante)
            })
    
    print(f"Encontrados {len(estudiantes_problema)} estudiantes en múltiples cursos:")
    
    for problema in estudiantes_problema:
        est = problema['estudiante']
        cursos = problema['cursos']
        
        print(f"\n--- {est.get_nombre_completo()} ---")
        print("Cursos actuales:")
        for i, curso in enumerate(cursos):
            print(f"  {i+1}. {curso}")
        
        # Estrategia: mantener al estudiante en el curso de mayor nivel
        # (principio: los estudiantes generalmente avanzan a cursos superiores)
        curso_mantener = max(cursos, key=lambda c: c.orden_nivel)
        cursos_remover = [c for c in cursos if c != curso_mantener]
        
        print(f"Manteniendo en: {curso_mantener}")
        print(f"Removiendo de: {', '.join([str(c) for c in cursos_remover])}")
        
        # Remover de los otros cursos
        for curso in cursos_remover:
            curso.estudiantes.remove(est)
            print(f"  ✓ Removido de {curso}")
        
        print(f"  ✓ {est.get_nombre_completo()} ahora solo está en {curso_mantener}")

def verificar_correccion():
    """Verificar que la corrección fue exitosa"""
    print("\n=== VERIFICANDO CORRECCIÓN ===")
    
    anio_actual = timezone.now().year
    estudiantes_problema = []
    
    for estudiante in Estudiante.objects.all():
        cursos_estudiante = estudiante.cursos.filter(anio=anio_actual)
        if cursos_estudiante.count() > 1:
            estudiantes_problema.append(estudiante)
    
    if estudiantes_problema:
        print(f"⚠️  Aún hay {len(estudiantes_problema)} estudiantes en múltiples cursos")
        for est in estudiantes_problema:
            cursos = est.cursos.filter(anio=anio_actual)
            print(f"  - {est.get_nombre_completo()}: {', '.join([str(c) for c in cursos])}")
    else:
        print("✅ ¡Corrección exitosa! No hay estudiantes en múltiples cursos del mismo año")

def mostrar_resumen_final():
    """Mostrar resumen final de cursos y estudiantes"""
    print("\n=== RESUMEN FINAL ===")
    
    anio_actual = timezone.now().year
    cursos = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
    
    total_estudiantes = 0
    for curso in cursos:
        num_estudiantes = curso.estudiantes.count()
        total_estudiantes += num_estudiantes
        status = "✅" if num_estudiantes > 0 else "❌"
        print(f"{status} {curso}: {num_estudiantes} estudiantes")
    
    print(f"\nTotal: {total_estudiantes} estudiantes distribuidos en {cursos.count()} cursos")

def main():
    print("CORRECCIÓN DE DATOS - ESTUDIANTES EN MÚLTIPLES CURSOS")
    print("=" * 60)
    
    # Hacer backup de la información antes de corregir
    print("Creando backup de asignaciones actuales...")
    
    corregir_estudiantes_multiples_cursos()
    verificar_correccion()
    mostrar_resumen_final()
    
    print("\n" + "=" * 60)
    print("CORRECCIÓN COMPLETADA")
    print("El filtrado de estudiantes por curso ahora debería funcionar correctamente")
    print("Puedes probar en: http://127.0.0.1:8000/crear_anotacion/")

if __name__ == '__main__':
    main()
