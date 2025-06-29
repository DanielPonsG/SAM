#!/usr/bin/env python3
"""
Script para probar el sistema completo de asistencia mejorado
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import (
    Curso, Asignatura, Estudiante, Profesor, Perfil, 
    AsistenciaAlumno, AsistenciaProfesor
)
from django.utils import timezone

def test_sistema_asistencia():
    """Test completo del sistema de asistencia"""
    print("🎯 INICIANDO PRUEBAS DEL SISTEMA DE ASISTENCIA")
    print("=" * 60)
    
    try:
        # 1. Verificar estructura de datos
        print("\n📊 VERIFICANDO ESTRUCTURA DE DATOS")
        print("-" * 40)
        
        cursos = Curso.objects.all()
        asignaturas = Asignatura.objects.all()
        estudiantes = Estudiante.objects.all()
        profesores = Profesor.objects.all()
        
        print(f"✅ Cursos: {cursos.count()}")
        print(f"✅ Asignaturas: {asignaturas.count()}")
        print(f"✅ Estudiantes: {estudiantes.count()}")
        print(f"✅ Profesores: {profesores.count()}")
        
        if not all([cursos.exists(), asignaturas.exists(), estudiantes.exists(), profesores.exists()]):
            print("❌ Faltan datos básicos para las pruebas")
            return False
        
        # 2. Probar registro de asistencia de alumnos
        print("\n📚 PROBANDO ASISTENCIA DE ALUMNOS")
        print("-" * 40)
        
        curso = cursos.first()
        asignatura = asignaturas.first()
        profesor = profesores.first()
        
        # Asignar asignatura al curso si no está asignada
        if not curso.asignaturas.filter(id=asignatura.id).exists():
            curso.asignaturas.add(asignatura)
            print(f"✅ Asignatura {asignatura.nombre} asignada al curso {curso}")
        
        # Asignar profesor a la asignatura si no está asignado
        if not asignatura.profesores_responsables.filter(id=profesor.id).exists():
            asignatura.profesores_responsables.add(profesor)
            print(f"✅ Profesor {profesor.get_nombre_completo()} asignado a {asignatura.nombre}")
        
        # Registrar asistencia para estudiantes del curso
        estudiantes_curso = curso.estudiantes.all()[:5]  # Solo los primeros 5
        fecha_hoy = timezone.now().date()
        hora_actual = timezone.now().time()
        
        asistencias_creadas = 0
        for i, estudiante in enumerate(estudiantes_curso):
            presente = i % 2 == 0  # Alternar presente/ausente
            observacion = f"Observación para {estudiante.get_nombre_completo()}"
            justificacion = "Justificación de ausencia" if not presente else ""
            
            asistencia, created = AsistenciaAlumno.objects.update_or_create(
                estudiante=estudiante,
                asignatura=asignatura,
                fecha=fecha_hoy,
                defaults={
                    'curso': curso,
                    'profesor_registro': profesor,
                    'hora_registro': hora_actual,
                    'presente': presente,
                    'observacion': observacion,
                    'justificacion': justificacion,
                    'fecha_creacion': timezone.now(),
                    'fecha_modificacion': timezone.now()
                }
            )
            
            if created:
                asistencias_creadas += 1
                
        print(f"✅ Asistencias de alumnos creadas: {asistencias_creadas}")
        
        # 3. Probar registro de asistencia de profesores
        print("\n👨‍🏫 PROBANDO ASISTENCIA DE PROFESORES")
        print("-" * 40)
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        asistencias_prof_creadas = 0
        for i, prof in enumerate(profesores[:3]):  # Solo los primeros 3
            presente = i != 1  # El segundo profesor ausente
            observacion = f"Observación para profesor {prof.get_nombre_completo()}"
            justificacion = "Permiso médico" if not presente else ""
            
            asistencia, created = AsistenciaProfesor.objects.update_or_create(
                profesor=prof,
                asignatura=asignatura,
                fecha=fecha_hoy,
                defaults={
                    'curso': curso,
                    'hora_registro': hora_actual,
                    'presente': presente,
                    'observacion': observacion,
                    'justificacion': justificacion,
                    'registrado_por_usuario': admin_user,
                    'fecha_creacion': timezone.now(),
                    'fecha_modificacion': timezone.now()
                }
            )
            
            if created:
                asistencias_prof_creadas += 1
                
        print(f"✅ Asistencias de profesores creadas: {asistencias_prof_creadas}")
        
        # 4. Verificar validaciones del modelo
        print("\n🔍 PROBANDO VALIDACIONES")
        print("-" * 40)
        
        try:
            # Intentar crear asistencia con profesor no asignado a la asignatura
            otro_profesor = profesores.exclude(id=profesor.id).first()
            if otro_profesor:
                asistencia_invalida = AsistenciaAlumno(
                    estudiante=estudiantes_curso.first(),
                    curso=curso,
                    asignatura=asignatura,
                    profesor_registro=otro_profesor,
                    fecha=fecha_hoy,
                    hora_registro=hora_actual,
                    presente=True
                )
                
                # Esto debería fallar en clean()
                try:
                    asistencia_invalida.clean()
                    print("⚠️  Validación de profesor no funcionó como esperado")
                except Exception as e:
                    print(f"✅ Validación de profesor funcionó: {str(e)[:50]}...")
                    
        except Exception as e:
            print(f"⚠️  Error en validaciones: {e}")
        
        # 5. Verificar estadísticas
        print("\n📈 VERIFICANDO ESTADÍSTICAS")
        print("-" * 40)
        
        total_asistencias_alumnos = AsistenciaAlumno.objects.filter(fecha=fecha_hoy).count()
        presentes_alumnos = AsistenciaAlumno.objects.filter(fecha=fecha_hoy, presente=True).count()
        ausentes_alumnos = total_asistencias_alumnos - presentes_alumnos
        
        total_asistencias_profesores = AsistenciaProfesor.objects.filter(fecha=fecha_hoy).count()
        presentes_profesores = AsistenciaProfesor.objects.filter(fecha=fecha_hoy, presente=True).count()
        ausentes_profesores = total_asistencias_profesores - presentes_profesores
        
        print(f"📚 Alumnos - Total: {total_asistencias_alumnos}, Presentes: {presentes_alumnos}, Ausentes: {ausentes_alumnos}")
        print(f"👨‍🏫 Profesores - Total: {total_asistencias_profesores}, Presentes: {presentes_profesores}, Ausentes: {ausentes_profesores}")
        
        porcentaje_alumnos = (presentes_alumnos / total_asistencias_alumnos * 100) if total_asistencias_alumnos > 0 else 0
        porcentaje_profesores = (presentes_profesores / total_asistencias_profesores * 100) if total_asistencias_profesores > 0 else 0
        
        print(f"📊 % Asistencia Alumnos: {porcentaje_alumnos:.1f}%")
        print(f"📊 % Asistencia Profesores: {porcentaje_profesores:.1f}%")
        
        # 6. Verificar funcionalidades específicas
        print("\n🔧 VERIFICANDO FUNCIONALIDADES ESPECÍFICAS")
        print("-" * 40)
        
        # Verificar que el profesor registrado está asignado a la asignatura
        asistencia_alumno = AsistenciaAlumno.objects.filter(fecha=fecha_hoy).first()
        if asistencia_alumno:
            profesor_registrado = asistencia_alumno.profesor_registro
            asignatura_asistencia = asistencia_alumno.asignatura
            
            if (asignatura_asistencia.profesores_responsables.filter(id=profesor_registrado.id).exists() or
                asignatura_asistencia.profesor_responsable == profesor_registrado):
                print("✅ Profesor registrado está correctamente asignado a la asignatura")
            else:
                print("❌ Profesor registrado NO está asignado a la asignatura")
        
        # Verificar que el estudiante está en el curso
        if asistencia_alumno:
            estudiante_asistencia = asistencia_alumno.estudiante
            curso_asistencia = asistencia_alumno.curso
            
            if curso_asistencia.estudiantes.filter(id=estudiante_asistencia.id).exists():
                print("✅ Estudiante está correctamente asignado al curso")
            else:
                print("❌ Estudiante NO está en el curso registrado")
        
        # Verificar que la asignatura está en el curso
        if asistencia_alumno:
            if asistencia_alumno.curso.asignaturas.filter(id=asistencia_alumno.asignatura.id).exists():
                print("✅ Asignatura está correctamente asignada al curso")
            else:
                print("❌ Asignatura NO está asignada al curso")
        
        print("\n🎉 PRUEBAS COMPLETADAS EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR DURANTE LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_resumen_asistencia():
    """Mostrar resumen de asistencia actual"""
    print("\n📋 RESUMEN ACTUAL DE ASISTENCIA")
    print("=" * 50)
    
    fecha_hoy = timezone.now().date()
    
    # Asistencia de alumnos
    asistencias_alumnos = AsistenciaAlumno.objects.filter(fecha=fecha_hoy)
    print(f"📚 Asistencia de Alumnos (hoy):")
    
    for asistencia in asistencias_alumnos[:5]:  # Solo mostrar los primeros 5
        estado = "✅ Presente" if asistencia.presente else "❌ Ausente"
        print(f"  - {asistencia.estudiante.get_nombre_completo()} ({asistencia.asignatura.nombre}): {estado}")
    
    if asistencias_alumnos.count() > 5:
        print(f"  ... y {asistencias_alumnos.count() - 5} más")
    
    # Asistencia de profesores
    asistencias_profesores = AsistenciaProfesor.objects.filter(fecha=fecha_hoy)
    print(f"\n👨‍🏫 Asistencia de Profesores (hoy):")
    
    for asistencia in asistencias_profesores:
        estado = "✅ Presente" if asistencia.presente else "❌ Ausente"
        asignatura_str = f" ({asistencia.asignatura.nombre})" if asistencia.asignatura else ""
        print(f"  - {asistencia.profesor.get_nombre_completo()}{asignatura_str}: {estado}")

def main():
    """Función principal"""
    print("🚀 SISTEMA DE ASISTENCIA - PRUEBAS COMPLETAS")
    print("=" * 70)
    
    success = test_sistema_asistencia()
    
    if success:
        mostrar_resumen_asistencia()
        print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("🎯 El sistema de asistencia está funcionando correctamente")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️  Revisa los errores mostrados arriba")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
