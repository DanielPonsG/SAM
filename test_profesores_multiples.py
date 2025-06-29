#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de múltiples profesores por asignatura
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura, Profesor
from django.db import transaction

def test_profesores_multiples():
    """Test para verificar la funcionalidad de múltiples profesores"""
    
    print("=== TESTING MÚLTIPLES PROFESORES POR ASIGNATURA ===\n")
    
    # 1. Crear algunos profesores de prueba si no existen
    profesores_data = [
        {
            'codigo_profesor': 'PROF001',
            'primer_nombre': 'María',
            'apellido_paterno': 'González',
            'email': 'maria.gonzalez@test.com',
            'numero_documento': '12345678-9',
            'fecha_nacimiento': '1985-03-15',
            'genero': 'F',
            'especialidad': 'Matemáticas'
        },
        {
            'codigo_profesor': 'PROF002',
            'primer_nombre': 'Carlos',
            'apellido_paterno': 'Rodriguez',
            'email': 'carlos.rodriguez@test.com',
            'numero_documento': '98765432-1',
            'fecha_nacimiento': '1980-07-22',
            'genero': 'M',
            'especialidad': 'Física'
        },
        {
            'codigo_profesor': 'PROF003',
            'primer_nombre': 'Ana',
            'apellido_paterno': 'Martínez',
            'email': 'ana.martinez@test.com',
            'numero_documento': '11223344-5',
            'fecha_nacimiento': '1990-11-08',
            'genero': 'F',
            'especialidad': 'Química'
        }
    ]
    
    profesores = []
    for data in profesores_data:
        profesor, created = Profesor.objects.get_or_create(
            codigo_profesor=data['codigo_profesor'],
            defaults=data
        )
        profesores.append(profesor)
        print(f"Profesor: {profesor.primer_nombre} {profesor.apellido_paterno} {'(creado)' if created else '(existente)'}")
    
    # 2. Crear una asignatura de prueba
    asignatura_data = {
        'codigo_asignatura': 'MAT-TEST',
        'nombre': 'Matemáticas Avanzadas Test',
        'descripcion': 'Asignatura de prueba para múltiples profesores'
    }
    
    asignatura, created = Asignatura.objects.get_or_create(
        codigo_asignatura=asignatura_data['codigo_asignatura'],
        defaults=asignatura_data
    )
    print(f"Asignatura: {asignatura.nombre} {'(creada)' if created else '(existente)'}")
    
    # 3. Limpiar profesores existentes de la asignatura
    asignatura.profesores_responsables.clear()
    asignatura.profesor_responsable = None
    asignatura.save()
    
    print(f"\nInicial - Profesores en {asignatura.nombre}: {asignatura.get_profesores_nombres()}")
    print(f"¿Tiene profesores?: {asignatura.tiene_profesores()}")
    
    # 4. Agregar múltiples profesores
    print("\n--- AGREGANDO PROFESORES ---")
    for i, profesor in enumerate(profesores[:2], 1):  # Solo agregar los primeros 2
        asignatura.agregar_profesor(profesor)
        print(f"{i}. Agregado: {profesor.primer_nombre} {profesor.apellido_paterno}")
        print(f"   Profesores actuales: {asignatura.get_profesores_nombres()}")
    
    # 5. Verificar el método get_todos_los_profesores
    print(f"\n--- VERIFICANDO MÉTODOS ---")
    todos_profesores = asignatura.get_todos_los_profesores()
    print(f"get_todos_los_profesores(): {[f'{p.primer_nombre} {p.apellido_paterno}' for p in todos_profesores]}")
    print(f"get_profesores_display(): {[f'{p.primer_nombre} {p.apellido_paterno}' for p in asignatura.get_profesores_display()]}")
    print(f"get_profesores_nombres(): {asignatura.get_profesores_nombres()}")
    print(f"tiene_profesores(): {asignatura.tiene_profesores()}")
    
    # 6. Agregar un profesor al campo antiguo para probar compatibilidad
    print(f"\n--- PROBANDO COMPATIBILIDAD CON CAMPO ANTIGUO ---")
    asignatura.profesor_responsable = profesores[2]  # El tercer profesor
    asignatura.save()
    
    todos_profesores = asignatura.get_todos_los_profesores()
    print(f"Después de agregar al campo antiguo:")
    print(f"get_todos_los_profesores(): {[f'{p.primer_nombre} {p.apellido_paterno}' for p in todos_profesores]}")
    print(f"get_profesores_nombres(): {asignatura.get_profesores_nombres()}")
    
    # 7. Remover un profesor
    print(f"\n--- REMOVIENDO PROFESOR ---")
    profesor_a_remover = profesores[0]
    print(f"Removiendo: {profesor_a_remover.primer_nombre} {profesor_a_remover.apellido_paterno}")
    asignatura.remover_profesor(profesor_a_remover)
    
    todos_profesores = asignatura.get_todos_los_profesores()
    print(f"Después de remover:")
    print(f"get_todos_los_profesores(): {[f'{p.primer_nombre} {p.apellido_paterno}' for p in todos_profesores]}")
    print(f"get_profesores_nombres(): {asignatura.get_profesores_nombres()}")
    
    # 8. Verificar relaciones inversas
    print(f"\n--- VERIFICANDO RELACIONES INVERSAS ---")
    for profesor in profesores:
        asignaturas_profesor = profesor.asignaturas.all()
        print(f"{profesor.primer_nombre} {profesor.apellido_paterno}: {asignaturas_profesor.count()} asignatura(s)")
        if asignaturas_profesor.exists():
            print(f"  - {', '.join([a.nombre for a in asignaturas_profesor])}")
    
    print(f"\n=== PRUEBA COMPLETADA EXITOSAMENTE ===")
    
    # Limpiar datos de prueba (opcional)
    respuesta = input("\n¿Deseas limpiar los datos de prueba? (y/n): ")
    if respuesta.lower() == 'y':
        print("Limpiando datos de prueba...")
        asignatura.delete()
        for profesor in profesores:
            if profesor.codigo_profesor.startswith('PROF00'):
                profesor.delete()
        print("Datos de prueba eliminados.")

if __name__ == '__main__':
    try:
        test_profesores_multiples()
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
