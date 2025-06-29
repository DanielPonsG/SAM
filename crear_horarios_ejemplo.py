#!/usr/bin/env python
"""
Script para crear datos de prueba específicos para probar las validaciones de horarios
a través de la interfaz web.
"""

import os
import sys
import django
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, HorarioCurso, Profesor
from django.contrib.auth.models import User

def crear_horarios_ejemplo():
    """Crear algunos horarios de ejemplo para pruebas"""
    
    print("=== CREANDO HORARIOS DE EJEMPLO PARA PRUEBAS ===\n")
    
    try:
        # Obtener datos
        curso = Curso.objects.filter(nivel__startswith='1').first()
        if not curso:
            print("❌ No se encontró ningún curso")
            return
        
        print(f"📚 Curso seleccionado: {curso.nombre_completo}")
        
        # Limpiar horarios existentes del curso
        HorarioCurso.objects.filter(curso=curso).delete()
        print("🧹 Horarios existentes eliminados")
        
        # Obtener asignaturas
        asignaturas = list(curso.asignaturas.all()[:3])  # Tomar las primeras 3
        profesores = list(Profesor.objects.all()[:3])  # Tomar los primeros 3
        
        if not asignaturas:
            print("❌ El curso no tiene asignaturas asignadas")
            return
        
        if not profesores:
            print("❌ No hay profesores en el sistema")
            return
        
        # Crear algunos horarios de ejemplo sin conflictos
        horarios_ejemplo = [
            {
                'asignatura': asignaturas[0],
                'profesor': profesores[0],
                'dia': 'LU',
                'hora_inicio': time(8, 0),
                'hora_fin': time(9, 0),
                'tipo_periodo': 'clase'
            },
            {
                'asignatura': asignaturas[1],
                'profesor': profesores[1],
                'dia': 'LU',
                'hora_inicio': time(9, 15),  # Con descanso de 15 minutos
                'hora_fin': time(10, 15),
                'tipo_periodo': 'clase'
            },
            {
                'asignatura': asignaturas[2] if len(asignaturas) > 2 else asignaturas[0],
                'profesor': profesores[2] if len(profesores) > 2 else profesores[0],
                'dia': 'MA',
                'hora_inicio': time(8, 0),
                'hora_fin': time(9, 0),
                'tipo_periodo': 'clase'
            }
        ]
        
        print("\n📝 Creando horarios de ejemplo:")
        for i, horario_data in enumerate(horarios_ejemplo, 1):
            try:
                horario = HorarioCurso.objects.create(
                    curso=curso,
                    **horario_data,
                    activo=True
                )
                print(f"  ✅ Horario {i}: {horario}")
            except Exception as e:
                print(f"  ❌ Error creando horario {i}: {e}")
        
        print(f"\n🎯 Horarios creados para curso {curso.nombre_completo}")
        print("Ahora puedes:")
        print("1. Ir a http://127.0.0.1:8000")
        print("2. Hacer login como administrador")
        print("3. Ir a 'Gestionar Horarios'")
        print(f"4. Seleccionar el curso '{curso.nombre_completo}'")
        print("5. Intentar agregar horarios que se solapen para probar las validaciones")
        
        print("\n🧪 ESCENARIOS DE PRUEBA SUGERIDOS:")
        print("- Intentar agregar horario en Lunes 8:00-9:00 (debería rechazarse - duplicado)")
        print("- Intentar agregar horario en Lunes 8:30-9:30 (debería rechazarse - solapamiento)")
        print("- Intentar agregar horario en Lunes 10:30-9:30 (debería rechazarse - hora inicio > hora fin)")
        print("- Agregar horario en Lunes 10:30-11:30 (debería aceptarse - sin conflictos)")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_horarios_ejemplo()
