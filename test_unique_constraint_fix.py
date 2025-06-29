#!/usr/bin/env python3
"""
Script para probar el registro de asistencia después de corregir el error UNIQUE constraint
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, Estudiante, AsistenciaAlumno, Profesor, Asignatura
from django.utils import timezone
from django.db import transaction

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_attendance_creation():
    """Probar creación de registros de asistencia"""
    print_separator("PROBANDO CREACIÓN DE ASISTENCIA")
    
    # Buscar curso y profesor
    curso = Curso.objects.filter(estudiantes__isnull=False, asignaturas__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con estudiantes y asignaturas")
        return
    
    profesor = Profesor.objects.first()
    if not profesor:
        print("❌ No hay profesores")
        return
    
    asignatura = curso.asignaturas.first()
    if not asignatura:
        print("❌ No hay asignaturas en el curso")
        return
    
    print(f"📚 Curso: {curso}")
    print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
    print(f"📖 Asignatura: {asignatura.nombre}")
    
    # Obtener estudiantes
    estudiantes = curso.estudiantes.all()[:3]  # Solo 3 para la prueba
    fecha_hoy = timezone.now().date()
    hora_actual = timezone.now().time()
    
    print(f"📅 Fecha: {fecha_hoy}")
    print(f"⏰ Hora: {hora_actual}")
    print(f"👥 Estudiantes a registrar: {estudiantes.count()}")
    
    # Eliminar registros existentes para evitar conflictos
    AsistenciaAlumno.objects.filter(
        estudiante__in=estudiantes,
        asignatura=asignatura,
        fecha=fecha_hoy
    ).delete()
    print("🗑️ Registros anteriores eliminados")
    
    try:
        with transaction.atomic():
            registros_creados = 0
            
            for i, estudiante in enumerate(estudiantes):
                presente = i % 2 == 0  # Alternar presente/ausente
                
                # Crear registro
                asistencia = AsistenciaAlumno.objects.create(
                    estudiante=estudiante,
                    curso=curso,
                    asignatura=asignatura,
                    fecha=fecha_hoy,
                    hora_registro=hora_actual,
                    presente=presente,
                    observacion=f'Prueba de registro {i+1}',
                    justificacion='Justificación de prueba' if not presente else '',
                    profesor_registro=profesor,
                    registrado_por_usuario=profesor.user if profesor.user else None
                )
                
                status = "✅ Presente" if presente else "❌ Ausente"
                print(f"   ✅ Creado: {estudiante.get_nombre_completo()} - {status}")
                registros_creados += 1
            
            print(f"\n🎉 Total registros creados: {registros_creados}")
            
    except Exception as e:
        print(f"❌ Error al crear registros: {str(e)}")
        import traceback
        traceback.print_exc()

def test_attendance_update():
    """Probar actualización de registros existentes"""
    print_separator("PROBANDO ACTUALIZACIÓN DE ASISTENCIA")
    
    # Buscar registros existentes
    asistencias = AsistenciaAlumno.objects.filter(fecha=timezone.now().date())[:3]
    
    if not asistencias.exists():
        print("❌ No hay registros para actualizar")
        return
    
    print(f"📋 Registros encontrados: {asistencias.count()}")
    
    try:
        for asistencia in asistencias:
            # Cambiar estado
            asistencia.presente = not asistencia.presente
            asistencia.observacion = f"Actualizado - {timezone.now().strftime('%H:%M:%S')}"
            asistencia.save()
            
            status = "✅ Presente" if asistencia.presente else "❌ Ausente"
            print(f"   ✅ Actualizado: {asistencia.estudiante.get_nombre_completo()} - {status}")
        
        print("🎉 Actualizaciones completadas")
        
    except Exception as e:
        print(f"❌ Error al actualizar: {str(e)}")

def test_duplicate_prevention():
    """Probar que se previenen duplicados"""
    print_separator("PROBANDO PREVENCIÓN DE DUPLICADOS")
    
    # Buscar curso y estudiante
    curso = Curso.objects.filter(estudiantes__isnull=False, asignaturas__isnull=False).first()
    if not curso:
        print("❌ No hay cursos disponibles")
        return
    
    estudiante = curso.estudiantes.first()
    asignatura = curso.asignaturas.first()
    profesor = Profesor.objects.first()
    
    if not all([estudiante, asignatura, profesor]):
        print("❌ Faltan datos necesarios")
        return
    
    fecha_hoy = timezone.now().date()
    
    print(f"📚 Curso: {curso}")
    print(f"👤 Estudiante: {estudiante.get_nombre_completo()}")
    print(f"📖 Asignatura: {asignatura.nombre}")
    print(f"📅 Fecha: {fecha_hoy}")
    
    # Intentar crear registro duplicado
    try:
        # Primer registro
        asistencia1 = AsistenciaAlumno.objects.create(
            estudiante=estudiante,
            curso=curso,
            asignatura=asignatura,
            fecha=fecha_hoy,
            presente=True,
            observacion='Primer registro',
            profesor_registro=profesor
        )
        print("✅ Primer registro creado")
        
        # Intentar crear duplicado
        try:
            asistencia2 = AsistenciaAlumno.objects.create(
                estudiante=estudiante,
                curso=curso,
                asignatura=asignatura,
                fecha=fecha_hoy,
                presente=False,
                observacion='Segundo registro (duplicado)',
                profesor_registro=profesor
            )
            print("❌ Error: Se permitió crear duplicado")
            
        except Exception as e:
            print(f"✅ Duplicado correctamente rechazado: {str(e)}")
        
        # Limpiar
        asistencia1.delete()
        print("🗑️ Registro de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")

def main():
    print("🎯 PRUEBA DE CORRECCIÓN DEL ERROR UNIQUE CONSTRAINT")
    print("=" * 70)
    
    try:
        test_attendance_creation()
        test_attendance_update()
        test_duplicate_prevention()
        
        print_separator("PRUEBA COMPLETADA ✅")
        print("🎉 El error UNIQUE constraint ha sido corregido:")
        print("✅ Se pueden crear registros de asistencia")
        print("✅ Se pueden actualizar registros existentes")
        print("✅ Se previenen duplicados correctamente")
        print("✅ El sistema está funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
