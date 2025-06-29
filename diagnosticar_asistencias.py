#!/usr/bin/env python3
"""
Script para diagnosticar problemas con la edición de asistencia de alumnos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import AsistenciaAlumno, Profesor, Estudiante, Curso, Asignatura
from django.contrib.auth.models import User

def diagnosticar_asistencias():
    """Diagnostica problemas con registros de asistencia"""
    print("🔍 DIAGNÓSTICO DE ASISTENCIAS - PROBLEMAS DE EDICIÓN")
    print("=" * 60)
    
    # 1. Verificar registros de asistencia
    total_asistencias = AsistenciaAlumno.objects.count()
    print(f"📊 Total de registros de asistencia: {total_asistencias}")
    
    if total_asistencias == 0:
        print("❌ No hay registros de asistencia para diagnosticar")
        return
    
    # 2. Verificar integridad de datos
    print("\n🔍 Verificando integridad de datos...")
    
    problemas = []
    
    # Asistencias sin profesor_registro
    sin_profesor = AsistenciaAlumno.objects.filter(profesor_registro__isnull=True)
    if sin_profesor.exists():
        problemas.append(f"❌ {sin_profesor.count()} registros sin profesor_registro")
        print(f"   Registros sin profesor: {list(sin_profesor.values_list('id', flat=True))}")
    
    # Asistencias sin curso
    sin_curso = AsistenciaAlumno.objects.filter(curso__isnull=True)
    if sin_curso.exists():
        problemas.append(f"❌ {sin_curso.count()} registros sin curso")
        print(f"   Registros sin curso: {list(sin_curso.values_list('id', flat=True))}")
    
    # Asistencias con referencias rotas
    for asistencia in AsistenciaAlumno.objects.all()[:10]:  # Revisar primeros 10
        try:
            # Verificar que las relaciones existen
            _ = asistencia.estudiante.get_nombre_completo()
            _ = asistencia.asignatura.nombre
            if asistencia.curso:
                _ = str(asistencia.curso)
            if asistencia.profesor_registro:
                _ = asistencia.profesor_registro.get_nombre_completo()
        except Exception as e:
            problemas.append(f"❌ Error en asistencia ID {asistencia.id}: {e}")
    
    # 3. Verificar permisos específicos
    print("\n🔍 Verificando configuración de permisos...")
    
    # Profesores con y sin usuario
    profesores_total = Profesor.objects.count()
    profesores_con_user = Profesor.objects.filter(user__isnull=False).count()
    profesores_sin_user = profesores_total - profesores_con_user
    
    if profesores_sin_user > 0:
        problemas.append(f"⚠️  {profesores_sin_user} profesores sin usuario asociado")
    
    # 4. Identificar asistencias problemáticas para edición
    print("\n🔍 Identificando asistencias problemáticas...")
    
    asistencias_problema = []
    
    for asistencia in AsistenciaAlumno.objects.all():
        try:
            # Simular la lógica de permisos de la vista
            if not asistencia.profesor_registro:
                asistencias_problema.append((asistencia.id, "Sin profesor_registro"))
                continue
                
            if not asistencia.curso:
                asistencias_problema.append((asistencia.id, "Sin curso"))
                continue
                
            # Verificar que el estudiante está en el curso
            if not asistencia.curso.estudiantes.filter(id=asistencia.estudiante.id).exists():
                asistencias_problema.append((asistencia.id, "Estudiante no está en el curso"))
                
            # Verificar que la asignatura está en el curso
            if not asistencia.curso.asignaturas.filter(id=asistencia.asignatura.id).exists():
                asistencias_problema.append((asistencia.id, "Asignatura no está en el curso"))
                
        except Exception as e:
            asistencias_problema.append((asistencia.id, f"Error: {e}"))
    
    # 5. Mostrar resultados
    print("\n📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 40)
    
    if not problemas and not asistencias_problema:
        print("✅ No se encontraron problemas evidentes")
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"   {problema}")
            
        if asistencias_problema:
            print(f"\n❌ Asistencias problemáticas para edición ({len(asistencias_problema)}):")
            for id_asistencia, motivo in asistencias_problema[:10]:  # Mostrar primeras 10
                print(f"   ID {id_asistencia}: {motivo}")
    
    # 6. Mostrar algunos registros de ejemplo
    print(f"\n📋 EJEMPLOS DE REGISTROS (primeros 5):")
    for asistencia in AsistenciaAlumno.objects.all()[:5]:
        try:
            print(f"   ID {asistencia.id}: {asistencia.estudiante.get_nombre_completo()} - "
                  f"{asistencia.asignatura.nombre} - "
                  f"Curso: {asistencia.curso or 'N/A'} - "
                  f"Profesor: {asistencia.profesor_registro.get_nombre_completo() if asistencia.profesor_registro else 'N/A'}")
        except Exception as e:
            print(f"   ID {asistencia.id}: ERROR - {e}")
    
    return asistencias_problema

def main():
    """Función principal"""
    try:
        problemas = diagnosticar_asistencias()
        
        if problemas:
            print(f"\n🎯 RESULTADO: Se encontraron {len(problemas)} registros problemáticos")
            print("📝 RECOMENDACIÓN: Ejecutar script de corrección de datos")
            return 1
        else:
            print("\n🎯 RESULTADO: Sistema de asistencias parece estar bien")
            return 0
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
