#!/usr/bin/env python
"""
Script para probar las validaciones de horarios y verificar que funcionan correctamente.
Este script simula diferentes escenarios de conflictos de horarios.
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

def test_validaciones_horario():
    """Función principal para probar las validaciones de horarios"""
    
    print("=== INICIO DE PRUEBAS DE VALIDACIONES DE HORARIO ===\n")
    
    # Obtener o crear datos de prueba
    try:
        curso = Curso.objects.filter(nivel__startswith='1').first()
        if not curso:
            print("❌ No se encontró ningún curso para las pruebas")
            return
        
        asignatura = curso.asignaturas.first()
        if not asignatura:
            print("❌ El curso no tiene asignaturas asignadas")
            return
        
        profesor = Profesor.objects.first()
        
        print(f"📚 Curso de prueba: {curso.nombre_completo}")
        print(f"📖 Asignatura: {asignatura.nombre}")
        print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo() if profesor else 'Sin profesor'}")
        print("-" * 50)
        
        # Test 1: Crear horario normal
        print("Test 1: Crear horario normal")
        try:
            horario1 = HorarioCurso.objects.create(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='LU',
                hora_inicio=time(8, 0),
                hora_fin=time(9, 0),
                tipo_periodo='clase',
                activo=True
            )
            print("✅ Horario creado exitosamente:", horario1)
        except Exception as e:
            print(f"❌ Error creando horario: {e}")
        
        # Test 2: Intentar crear horario duplicado exacto
        print("\nTest 2: Intentar crear horario duplicado exacto")
        try:
            horario_duplicado = HorarioCurso.objects.create(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='LU',
                hora_inicio=time(8, 0),
                hora_fin=time(9, 0),
                tipo_periodo='clase',
                activo=True
            )
            print("❌ Se permitió crear horario duplicado (ERROR)")
        except Exception as e:
            print(f"✅ Horario duplicado rechazado correctamente: {e}")
        
        # Test 3: Intentar crear horario con solapamiento
        print("\nTest 3: Intentar crear horario con solapamiento")
        try:
            horario_solapado = HorarioCurso.objects.create(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='LU',
                hora_inicio=time(8, 30),
                hora_fin=time(9, 30),
                tipo_periodo='clase',
                activo=True
            )
            print("❌ Se permitió crear horario solapado (debería validarse en el backend)")
        except Exception as e:
            print(f"✅ Horario solapado rechazado: {e}")
        
        # Test 4: Crear horario válido en diferente día
        print("\nTest 4: Crear horario válido en diferente día")
        try:
            horario2 = HorarioCurso.objects.create(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='MA',
                hora_inicio=time(8, 0),
                hora_fin=time(9, 0),
                tipo_periodo='clase',
                activo=True
            )
            print("✅ Horario en día diferente creado exitosamente:", horario2)
        except Exception as e:
            print(f"❌ Error creando horario en día diferente: {e}")
        
        # Test 5: Crear horario válido en misma día pero diferente hora
        print("\nTest 5: Crear horario válido en mismo día pero diferente hora")
        try:
            horario3 = HorarioCurso.objects.create(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='LU',
                hora_inicio=time(10, 0),
                hora_fin=time(11, 0),
                tipo_periodo='clase',
                activo=True
            )
            print("✅ Horario en misma día/diferente hora creado exitosamente:", horario3)
        except Exception as e:
            print(f"❌ Error creando horario en misma día/diferente hora: {e}")
        
        # Test 6: Validación de hora inicio > hora fin
        print("\nTest 6: Validación de hora inicio > hora fin")
        try:
            horario_invalido = HorarioCurso(
                curso=curso,
                asignatura=asignatura,
                profesor=profesor,
                dia='MI',
                hora_inicio=time(10, 0),
                hora_fin=time(9, 0),  # Hora fin menor que hora inicio
                tipo_periodo='clase',
                activo=True
            )
            horario_invalido.full_clean()  # Ejecutar validación
            horario_invalido.save()
            print("❌ Se permitió crear horario con hora inicio > hora fin (ERROR)")
        except Exception as e:
            print(f"✅ Horario con horas inválidas rechazado correctamente: {e}")
        
        print("\n" + "=" * 60)
        print("RESUMEN DE HORARIOS CREADOS:")
        horarios = HorarioCurso.objects.filter(curso=curso, activo=True).order_by('dia', 'hora_inicio')
        for horario in horarios:
            print(f"  - {horario}")
        
        print(f"\nTotal horarios activos para {curso.nombre_completo}: {horarios.count()}")
        
        # Limpiar datos de prueba
        print("\n🧹 Limpiando datos de prueba...")
        HorarioCurso.objects.filter(curso=curso).delete()
        print("✅ Datos de prueba eliminados")
        
    except Exception as e:
        print(f"❌ Error general en las pruebas: {e}")
        import traceback
        traceback.print_exc()

def listar_cursos_disponibles():
    """Lista los cursos disponibles para las pruebas"""
    print("CURSOS DISPONIBLES PARA PRUEBAS:")
    cursos = Curso.objects.all()[:5]  # Mostrar solo los primeros 5
    
    if not cursos:
        print("  No hay cursos en la base de datos")
        return
        
    for curso in cursos:
        asignaturas_count = curso.asignaturas.count()
        print(f"  - {curso.nombre_completo} ({asignaturas_count} asignaturas)")
        if asignaturas_count > 0:
            print(f"    Asignaturas: {', '.join([a.nombre for a in curso.asignaturas.all()[:3]])}")

if __name__ == "__main__":
    print("Script de prueba de validaciones de horario")
    print("=" * 50)
    
    # Listar cursos disponibles
    listar_cursos_disponibles()
    print()
    
    # Ejecutar pruebas
    test_validaciones_horario()
    
    print("\n=== FIN DE PRUEBAS ===")
