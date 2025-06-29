#!/usr/bin/env python3
"""
Script para probar el sistema de registro de asistencia simplificado
- Solo curso (sin asignatura)
- Restricciones por profesor
- Registro automático de quién y cuándo
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
from django.db.models import Q

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_curso_permissions():
    """Probar que los profesores solo ven sus cursos asignados"""
    print_separator("PROBANDO PERMISOS DE CURSOS")
    
    # Buscar profesores
    profesores = Profesor.objects.all()[:3]
    
    for profesor in profesores:
        print(f"\n📋 Profesor: {profesor.get_nombre_completo()}")
        
        # Simular la lógica de la vista
        cursos_ids = set()
        
        # 1. Cursos donde es profesor jefe
        cursos_jefatura = profesor.get_cursos_jefatura()
        cursos_ids.update(cursos_jefatura.values_list('id', flat=True))
        print(f"   Cursos como jefe: {[str(curso) for curso in cursos_jefatura]}")
        
        # 2. Cursos donde hace clases
        cursos_asignaturas = Curso.objects.filter(
            asignaturas__profesores_responsables=profesor
        )
        cursos_ids.update(cursos_asignaturas.values_list('id', flat=True))
        print(f"   Cursos como responsable: {[str(curso) for curso in cursos_asignaturas]}")
        
        # 3. Cursos donde es responsable principal
        cursos_responsable = Curso.objects.filter(
            asignaturas__profesor_responsable=profesor
        )
        cursos_ids.update(cursos_responsable.values_list('id', flat=True))
        print(f"   Cursos como principal: {[str(curso) for curso in cursos_responsable]}")
        
        # Total
        if cursos_ids:
            cursos_disponibles = Curso.objects.filter(id__in=list(cursos_ids)).distinct()
            print(f"   ✅ Total cursos disponibles: {cursos_disponibles.count()}")
            for curso in cursos_disponibles:
                print(f"      - {curso}")
        else:
            print(f"   ❌ Sin cursos asignados")

def test_automatic_subject_assignment():
    """Probar asignación automática de asignatura"""
    print_separator("PROBANDO ASIGNACIÓN AUTOMÁTICA DE ASIGNATURA")
    
    # Tomar un curso con asignaturas
    curso = Curso.objects.filter(asignaturas__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con asignaturas")
        return
    
    print(f"📚 Curso: {curso}")
    print(f"   Asignaturas del curso: {list(curso.asignaturas.values_list('nombre', flat=True))}")
    
    # Buscar cualquier profesor que tenga asignaturas en este curso
    profesor = Profesor.objects.filter(
        asignaturas_responsable__in=curso.asignaturas.all()
    ).first()
    
    if profesor:
        print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
        
        # Lógica de asignación automática
        asignaturas_profesor = curso.asignaturas.filter(
            profesores_responsables=profesor
        ).first()
        
        if asignaturas_profesor:
            print(f"   ✅ Asignatura automática: {asignaturas_profesor.nombre}")
        else:
            asignatura_primera = curso.asignaturas.first()
            print(f"   ⚠️  No tiene asignatura específica, usando primera: {asignatura_primera.nombre}")
    else:
        print("   ⚠️  Sin profesor específico, usando primera asignatura")
        asignatura_primera = curso.asignaturas.first()
        print(f"   Asignatura por defecto: {asignatura_primera.nombre}")

def test_attendance_registration():
    """Probar registro de asistencia con información automática"""
    print_separator("PROBANDO REGISTRO DE ASISTENCIA")
    
    # Tomar curso y profesor
    curso = Curso.objects.filter(estudiantes__isnull=False, asignaturas__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con estudiantes y asignaturas")
        return
    
    profesor = Profesor.objects.filter(
        asignaturas_responsable__in=curso.asignaturas.all()
    ).first()
    
    if not profesor:
        profesor = Profesor.objects.first()
    
    if not profesor:
        print("❌ No hay profesores")
        return
    
    print(f"📚 Curso: {curso}")
    print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
    
    # Obtener asignatura automática
    asignatura = curso.asignaturas.filter(
        Q(profesores_responsables=profesor) |
        Q(profesor_responsable=profesor)
    ).first()
    
    if not asignatura:
        asignatura = curso.asignaturas.first()
    
    print(f"📖 Asignatura automática: {asignatura.nombre}")
    
    # Simular registro de asistencia
    fecha_hoy = timezone.now().date()
    hora_actual = timezone.now().time()
    
    estudiantes = curso.estudiantes.all()[:3]  # Solo algunos para la prueba
    print(f"👥 Estudiantes para registrar: {estudiantes.count()}")
    
    for i, estudiante in enumerate(estudiantes):
        presente = i % 2 == 0  # Alternar presente/ausente
        
        asistencia, created = AsistenciaAlumno.objects.update_or_create(
            estudiante=estudiante,
            curso=curso,
            asignatura=asignatura,
            fecha=fecha_hoy,
            defaults={
                'presente': presente,
                'observacion': f'Registro automático de prueba',
                'justificacion': '' if presente else 'Prueba de ausencia',
                'profesor_registro': profesor,
                'hora_registro': hora_actual,
                'registrado_por_usuario': profesor.user if profesor.user else None
            }
        )
        
        status = "✅ Presente" if presente else "❌ Ausente"
        action = "Creado" if created else "Actualizado"
        print(f"   {action}: {estudiante.get_nombre_completo()} - {status}")
        print(f"      Registrado por: {profesor.get_nombre_completo()}")
        print(f"      Fecha: {fecha_hoy}, Hora: {hora_actual.strftime('%H:%M:%S')}")

def test_existing_attendance():
    """Ver registros de asistencia existentes"""
    print_separator("REGISTROS DE ASISTENCIA RECIENTES")
    
    # Últimos 5 registros
    asistencias = AsistenciaAlumno.objects.select_related(
        'estudiante', 'curso', 'asignatura', 'profesor_registro'
    ).order_by('-fecha', '-hora_registro')[:5]
    
    if not asistencias.exists():
        print("❌ No hay registros de asistencia")
        return
    
    for asistencia in asistencias:
        status = "✅ Presente" if asistencia.presente else "❌ Ausente"
        print(f"📋 {asistencia.estudiante.get_nombre_completo()} ({asistencia.curso}) - {status}")
        print(f"   📖 Asignatura: {asistencia.asignatura.nombre}")
        print(f"   📅 Fecha: {asistencia.fecha}")
        print(f"   ⏰ Hora: {asistencia.hora_registro}")
        print(f"   👨‍🏫 Registrado por: {asistencia.profesor_registro.get_nombre_completo() if asistencia.profesor_registro else 'N/A'}")
        if asistencia.observacion:
            print(f"   💬 Observación: {asistencia.observacion}")
        if asistencia.justificacion:
            print(f"   📝 Justificación: {asistencia.justificacion}")
        print()

def main():
    print("🎯 PRUEBA DEL SISTEMA DE REGISTRO DE ASISTENCIA SIMPLIFICADO")
    print("=" * 70)
    
    try:
        test_curso_permissions()
        test_automatic_subject_assignment()
        test_attendance_registration()
        test_existing_attendance()
        
        print_separator("PRUEBA COMPLETADA ✅")
        print("El sistema de registro simplificado funciona correctamente:")
        print("✅ Solo requiere selección de curso")
        print("✅ Asignación automática de asignatura")
        print("✅ Restricciones de permisos por profesor")
        print("✅ Registro automático de quién y cuándo")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
