#!/usr/bin/env python3
"""
Script para corregir registros de asistencia problemáticos
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

def corregir_asistencias():
    """Corrige registros de asistencia problemáticos"""
    print("🔧 CORRECCIÓN DE REGISTROS DE ASISTENCIA PROBLEMÁTICOS")
    print("=" * 60)
    
    # 1. Identificar registros sin profesor_registro
    sin_profesor = AsistenciaAlumno.objects.filter(profesor_registro__isnull=True)
    print(f"📊 Registros sin profesor_registro: {sin_profesor.count()}")
    
    if sin_profesor.count() == 0:
        print("✅ No hay registros problemáticos para corregir")
        return True
    
    # 2. Buscar un profesor por defecto para asignar
    profesor_defecto = None
    
    # Intentar encontrar un profesor administrador o director
    profesores_admin = Profesor.objects.filter(
        user__groups__name__in=['director', 'administrador']
    ).first()
    
    if profesores_admin:
        profesor_defecto = profesores_admin
        print(f"✅ Profesor administrador encontrado: {profesor_defecto.get_nombre_completo()}")
    else:
        # Si no hay admin, usar el primer profesor disponible
        profesor_defecto = Profesor.objects.first()
        if profesor_defecto:
            print(f"⚠️  Usando primer profesor disponible: {profesor_defecto.get_nombre_completo()}")
        else:
            print("❌ No hay profesores en el sistema para asignar")
            return False
    
    # 3. Corregir registros uno por uno
    corregidos = 0
    errores = 0
    
    for asistencia in sin_profesor:
        try:
            # Intentar encontrar un profesor apropiado para esta asignatura
            profesor_apropiado = None
            
            # Buscar profesor responsable de la asignatura
            if asistencia.asignatura.profesor_responsable:
                profesor_apropiado = asistencia.asignatura.profesor_responsable
            elif asistencia.asignatura.profesores_responsables.exists():
                profesor_apropiado = asistencia.asignatura.profesores_responsables.first()
            else:
                # Usar profesor por defecto
                profesor_apropiado = profesor_defecto
            
            # Asignar el profesor
            asistencia.profesor_registro = profesor_apropiado
            asistencia.save()
            
            print(f"✅ Corregido ID {asistencia.id}: Asignado profesor {profesor_apropiado.get_nombre_completo()}")
            corregidos += 1
            
        except Exception as e:
            print(f"❌ Error corrigiendo ID {asistencia.id}: {e}")
            errores += 1
    
    # 4. Verificar otros problemas
    print(f"\n🔍 Verificando otros problemas...")
    
    # Corregir registros sin curso
    sin_curso = AsistenciaAlumno.objects.filter(curso__isnull=True)
    if sin_curso.exists():
        print(f"⚠️  Encontrados {sin_curso.count()} registros sin curso")
        for asistencia in sin_curso:
            try:
                # Intentar encontrar el curso del estudiante
                curso_estudiante = asistencia.estudiante.cursos.first()
                if curso_estudiante:
                    asistencia.curso = curso_estudiante
                    asistencia.save()
                    print(f"✅ Asignado curso {curso_estudiante} a registro ID {asistencia.id}")
                    corregidos += 1
            except Exception as e:
                print(f"❌ Error asignando curso a ID {asistencia.id}: {e}")
                errores += 1
    
    # 5. Verificar relaciones rotas
    print(f"\n🔍 Verificando relaciones estudiante-curso...")
    
    for asistencia in AsistenciaAlumno.objects.all():
        try:
            if asistencia.curso and asistencia.estudiante:
                # Verificar que el estudiante está en el curso
                if not asistencia.curso.estudiantes.filter(id=asistencia.estudiante.id).exists():
                    print(f"⚠️  Estudiante {asistencia.estudiante.get_nombre_completo()} no está en curso {asistencia.curso}")
                    # Agregar estudiante al curso
                    asistencia.curso.estudiantes.add(asistencia.estudiante)
                    print(f"✅ Agregado estudiante al curso")
                    
                # Verificar que la asignatura está en el curso
                if not asistencia.curso.asignaturas.filter(id=asistencia.asignatura.id).exists():
                    print(f"⚠️  Asignatura {asistencia.asignatura.nombre} no está en curso {asistencia.curso}")
                    # Agregar asignatura al curso
                    asistencia.curso.asignaturas.add(asistencia.asignatura)
                    print(f"✅ Agregada asignatura al curso")
                    
        except Exception as e:
            print(f"❌ Error verificando relaciones en ID {asistencia.id}: {e}")
            errores += 1
    
    # 6. Resumen
    print(f"\n📋 RESUMEN DE CORRECCIONES")
    print("=" * 40)
    print(f"✅ Registros corregidos: {corregidos}")
    print(f"❌ Errores encontrados: {errores}")
    
    if errores == 0:
        print("🎉 Todas las correcciones fueron exitosas")
        return True
    else:
        print("⚠️  Algunas correcciones fallaron, revisar errores")
        return False

def main():
    """Función principal"""
    try:
        success = corregir_asistencias()
        
        if success:
            print("\n🎯 RESULTADO: Correcciones completadas exitosamente")
            print("📝 RECOMENDACIÓN: Probar edición de asistencias ahora")
            return 0
        else:
            print("\n❌ RESULTADO: Algunas correcciones fallaron")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
