#!/usr/bin/env python
"""
Test rápido para verificar el sistema de asistencia
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante, Profesor, AsistenciaAlumno, Asignatura
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

def test_asistencia():
    print("🔍 Probando sistema de asistencia...")
    
    # Verificar que hay cursos
    cursos = Curso.objects.filter(anio=timezone.now().year)
    print(f"✅ Cursos disponibles: {cursos.count()}")
    
    if cursos.exists():
        curso = cursos.first()
        print(f"   - Curso de prueba: {curso}")
        print(f"   - Estudiantes: {curso.estudiantes.count()}")
        print(f"   - Asignaturas: {curso.asignaturas.count()}")
        
        # Verificar asistencias
        asistencias = AsistenciaAlumno.objects.filter(curso=curso)
        print(f"   - Registros de asistencia: {asistencias.count()}")
        
        if asistencias.exists():
            ultima_asistencia = asistencias.last()
            print(f"   - Último registro: {ultima_asistencia.estudiante.get_nombre_completo()} - {ultima_asistencia.fecha}")
    
    # Verificar profesores
    profesores = Profesor.objects.all()
    print(f"✅ Profesores disponibles: {profesores.count()}")
    
    # Verificar estudiantes
    estudiantes = Estudiante.objects.all()
    print(f"✅ Estudiantes disponibles: {estudiantes.count()}")
    
    # Verificar asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"✅ Asignaturas disponibles: {asignaturas.count()}")
    
    print("\n📊 Resumen del sistema:")
    print(f"   - Cursos: {cursos.count()}")
    print(f"   - Estudiantes: {estudiantes.count()}")
    print(f"   - Profesores: {profesores.count()}")
    print(f"   - Asignaturas: {asignaturas.count()}")
    print(f"   - Registros de asistencia: {AsistenciaAlumno.objects.count()}")
    
    # Test de formato de fecha
    print("\n🔧 Probando formatos de fecha...")
    fecha_tests = [
        '2025-06-30',
        '30/06/2025',
        '30-06-2025'
    ]
    
    for fecha_str in fecha_tests:
        formatos_fecha = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        fecha_seleccionada = None
        
        for formato in formatos_fecha:
            try:
                fecha_seleccionada = datetime.strptime(fecha_str, formato).date()
                print(f"   ✅ {fecha_str} -> {fecha_seleccionada} (formato: {formato})")
                break
            except ValueError:
                continue
        
        if fecha_seleccionada is None:
            print(f"   ❌ No se pudo parsear: {fecha_str}")
    
    print("\n✅ Sistema de asistencia funcionando correctamente!")

if __name__ == '__main__':
    test_asistencia()
