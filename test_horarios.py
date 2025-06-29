"""
Script de prueba para el sistema de horarios de cursos

Este script crea datos de prueba para demostrar el funcionamiento
del sistema de gestión de horarios.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, Profesor, HorarioCurso
from datetime import time

def crear_datos_prueba():
    """Crear datos de prueba para el sistema de horarios"""
    
    print("🔧 Creando datos de prueba para el sistema de horarios...")
    
    # Verificar si ya existe un curso de prueba
    curso_prueba = Curso.objects.filter(nivel='1M', paralelo='A').first()
    if not curso_prueba:
        print("❌ No se encontró un curso para hacer pruebas.")
        print("Por favor, cree al menos un curso desde la interfaz web.")
        return
    
    print(f"✅ Usando curso: {curso_prueba}")
    
    # Crear asignaturas de ejemplo si no existen
    asignaturas_ejemplo = [
        ('Matemáticas', 'MAT001'),
        ('Lengua y Literatura', 'LEN001'),
        ('Historia', 'HIS001'),
        ('Ciencias Naturales', 'CIE001'),
        ('Educación Física', 'EDF001'),
    ]
    
    for nombre, codigo in asignaturas_ejemplo:
        asignatura, created = Asignatura.objects.get_or_create(
            codigo_asignatura=codigo,
            defaults={'nombre': nombre, 'descripcion': f'Asignatura de {nombre}'}
        )
        if created:
            print(f"✅ Creada asignatura: {nombre}")
        
        # Asignar asignatura al curso si no está asignada
        if asignatura not in curso_prueba.asignaturas.all():
            curso_prueba.asignaturas.add(asignatura)
            print(f"✅ Asignatura {nombre} asignada al curso {curso_prueba}")
    
    # Crear profesores de ejemplo si no existen
    profesores_ejemplo = [
        ('Juan', 'Pérez', 'PROF001', 'Matemáticas'),
        ('María', 'González', 'PROF002', 'Lengua y Literatura'),
        ('Carlos', 'Rodríguez', 'PROF003', 'Historia'),
        ('Ana', 'Martínez', 'PROF004', 'Ciencias'),
        ('Luis', 'López', 'PROF005', 'Educación Física'),
    ]
    
    for nombre, apellido, codigo, especialidad in profesores_ejemplo:
        profesor, created = Profesor.objects.get_or_create(
            codigo_profesor=codigo,
            defaults={
                'primer_nombre': nombre,
                'apellido_paterno': apellido,
                'especialidad': especialidad,
                'numero_documento': f'12345{codigo[-3:]}',
                'email': f'{nombre.lower()}.{apellido.lower()}@ejemplo.com',
                'fecha_nacimiento': '1980-01-01',
                'genero': 'M' if nombre in ['Juan', 'Carlos', 'Luis'] else 'F'
            }
        )
        if created:
            print(f"✅ Creado profesor: {nombre} {apellido}")
    
    # Crear horarios de ejemplo
    print("\n📅 Creando horarios de ejemplo...")
    
    # Limpiar horarios existentes del curso
    HorarioCurso.objects.filter(curso=curso_prueba).delete()
    
    # Horarios de ejemplo
    horarios_ejemplo = [
        # Lunes
        ('LU', time(8, 0), time(8, 45), 'clase', 'MAT001', 'PROF001'),
        ('LU', time(8, 45), time(9, 30), 'clase', 'LEN001', 'PROF002'),
        ('LU', time(9, 30), time(9, 45), 'recreo', None, None),
        ('LU', time(9, 45), time(10, 30), 'clase', 'HIS001', 'PROF003'),
        ('LU', time(10, 30), time(11, 15), 'clase', 'CIE001', 'PROF004'),
        ('LU', time(11, 15), time(11, 30), 'recreo', None, None),
        ('LU', time(11, 30), time(12, 15), 'clase', 'EDF001', 'PROF005'),
        ('LU', time(12, 15), time(13, 30), 'almuerzo', None, None),
        ('LU', time(13, 30), time(14, 15), 'clase', 'MAT001', 'PROF001'),
        
        # Martes
        ('MA', time(8, 0), time(8, 45), 'clase', 'LEN001', 'PROF002'),
        ('MA', time(8, 45), time(9, 30), 'clase', 'MAT001', 'PROF001'),
        ('MA', time(9, 30), time(9, 45), 'recreo', None, None),
        ('MA', time(9, 45), time(10, 30), 'clase', 'CIE001', 'PROF004'),
        ('MA', time(10, 30), time(11, 15), 'clase', 'HIS001', 'PROF003'),
        ('MA', time(11, 15), time(11, 30), 'recreo', None, None),
        ('MA', time(11, 30), time(12, 15), 'clase', 'LEN001', 'PROF002'),
        ('MA', time(12, 15), time(13, 30), 'almuerzo', None, None),
        ('MA', time(13, 30), time(14, 15), 'clase', 'EDF001', 'PROF005'),
    ]
    
    for dia, hora_inicio, hora_fin, tipo_periodo, codigo_asignatura, codigo_profesor in horarios_ejemplo:
        # Obtener asignatura y profesor si corresponde
        asignatura = None
        profesor = None
        
        if codigo_asignatura:
            asignatura = Asignatura.objects.get(codigo_asignatura=codigo_asignatura)
        
        if codigo_profesor:
            profesor = Profesor.objects.get(codigo_profesor=codigo_profesor)
        
        # Crear horario
        horario = HorarioCurso.objects.create(
            curso=curso_prueba,
            asignatura=asignatura,
            profesor=profesor,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_periodo=tipo_periodo,
            activo=True
        )
        
        print(f"✅ Creado horario: {dia} {hora_inicio}-{hora_fin} - {tipo_periodo}")
    
    print(f"\n🎉 ¡Sistema de horarios configurado correctamente!")
    print(f"📊 Horarios creados para el curso: {curso_prueba}")
    print(f"🔗 URL para gestionar horarios: http://127.0.0.1:8000/cursos/{curso_prueba.id}/horarios/")
    print(f"🔗 URL para listar cursos: http://127.0.0.1:8000/cursos/")

def mostrar_resumen():
    """Mostrar resumen del sistema"""
    print("\n📊 RESUMEN DEL SISTEMA DE HORARIOS:")
    print("="*50)
    
    total_cursos = Curso.objects.count()
    total_asignaturas = Asignatura.objects.count()
    total_profesores = Profesor.objects.count()
    total_horarios = HorarioCurso.objects.filter(activo=True).count()
    
    print(f"📚 Cursos registrados: {total_cursos}")
    print(f"📖 Asignaturas registradas: {total_asignaturas}")
    print(f"👨‍🏫 Profesores registrados: {total_profesores}")
    print(f"⏰ Horarios activos: {total_horarios}")
    
    # Mostrar conflictos
    conflictos = []
    for horario in HorarioCurso.objects.filter(activo=True, tipo_periodo='clase'):
        if horario.profesor:
            conflictos_profesor = HorarioCurso.objects.filter(
                profesor=horario.profesor,
                dia=horario.dia,
                hora_inicio=horario.hora_inicio,
                activo=True
            ).exclude(id=horario.id)
            
            if conflictos_profesor.exists():
                conflictos.append(horario)
    
    if conflictos:
        print(f"⚠️  Conflictos detectados: {len(conflictos)}")
    else:
        print("✅ No se detectaron conflictos de horarios")
    
    print("\n🔧 CARACTERÍSTICAS IMPLEMENTADAS:")
    print("- ✅ Gestión completa de horarios por curso")
    print("- ✅ Prevención de conflictos de horarios")
    print("- ✅ Asignación de profesores con validación")
    print("- ✅ Períodos de recreo y almuerzo")
    print("- ✅ Interfaz web moderna y responsive")
    print("- ✅ Operaciones AJAX para edición en tiempo real")
    print("- ✅ Detección automática de conflictos")
    print("- ✅ Filtrado de profesores por asignatura")

if __name__ == "__main__":
    try:
        crear_datos_prueba()
        mostrar_resumen()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrese de que el servidor esté ejecutándose y tenga al menos un curso creado.")
