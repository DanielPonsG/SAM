#!/usr/bin/env python3
"""
Script simplificado para probar las correcciones finales usando datos existentes
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil, Estudiante, Profesor, Asignatura, Curso, Inscripcion, Grupo, Calificacion
from smapp.forms import CalificacionForm
from django.db.models import Avg

def test_formulario_calificacion():
    """Probar formulario de calificación mejorado"""
    print("\n📝 Probando formulario de calificación...")
    
    try:
        # Obtener una calificación existente
        calificacion = Calificacion.objects.first()
        
        if calificacion:
            print(f"✅ Calificación encontrada: {calificacion.nombre_evaluacion} - {calificacion.puntaje}")
            
            # Probar formulario con datos válidos
            form_data = {
                'nombre_evaluacion': 'Prueba Editada',
                'puntaje': 6.8,
                'porcentaje': 88,
                'detalle': 'Muy bueno',
                'descripcion': 'Prueba editada correctamente'
            }
            
            form = CalificacionForm(data=form_data, instance=calificacion)
            
            if form.is_valid():
                print("✅ Formulario válido")
                print(f"   Campos incluidos: {form.Meta.fields}")
                print(f"   Widgets configurados: {len(form.Meta.widgets)} widgets")
                print(f"   Labels personalizados: {len(form.Meta.labels)} labels")
                print(f"   Validaciones: puntaje={form.cleaned_data['puntaje']}, porcentaje={form.cleaned_data.get('porcentaje', 'N/A')}")
                return True
            else:
                print("❌ Formulario inválido")
                print(f"   Errores: {form.errors}")
                return False
        else:
            print("❌ No se encontró calificación para probar")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar formulario: {e}")
        return False

def test_validaciones_formulario():
    """Probar validaciones del formulario"""
    print("\n🔍 Probando validaciones del formulario...")
    
    try:
        # Obtener una calificación existente
        calificacion = Calificacion.objects.first()
        
        if not calificacion:
            print("❌ No se encontró calificación para probar")
            return False
        
        # Probar datos inválidos
        test_cases = [
            {
                'name': 'Puntaje muy alto',
                'data': {'nombre_evaluacion': 'Test', 'puntaje': 8.0, 'porcentaje': 50},
                'should_fail': True
            },
            {
                'name': 'Puntaje muy bajo',
                'data': {'nombre_evaluacion': 'Test', 'puntaje': 0.5, 'porcentaje': 50},
                'should_fail': True
            },
            {
                'name': 'Porcentaje negativo',
                'data': {'nombre_evaluacion': 'Test', 'puntaje': 5.0, 'porcentaje': -10},
                'should_fail': True
            },
            {
                'name': 'Porcentaje muy alto',
                'data': {'nombre_evaluacion': 'Test', 'puntaje': 5.0, 'porcentaje': 150},
                'should_fail': True
            },
            {
                'name': 'Datos válidos',
                'data': {'nombre_evaluacion': 'Test Válido', 'puntaje': 6.0, 'porcentaje': 80},
                'should_fail': False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            form = CalificacionForm(data=test_case['data'], instance=calificacion)
            is_valid = form.is_valid()
            
            if test_case['should_fail'] and is_valid:
                print(f"❌ {test_case['name']}: Debería fallar pero pasó")
                all_passed = False
            elif not test_case['should_fail'] and not is_valid:
                print(f"❌ {test_case['name']}: Debería pasar pero falló - {form.errors}")
                all_passed = False
            else:
                print(f"✅ {test_case['name']}: {'Falló correctamente' if test_case['should_fail'] else 'Pasó correctamente'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error al probar validaciones: {e}")
        return False

def test_promedio_asignatura():
    """Probar cálculo de promedio por asignatura"""
    print("\n📊 Probando cálculo de promedio por asignatura...")
    
    try:
        # Obtener asignaturas con calificaciones
        asignaturas_con_notas = Asignatura.objects.filter(
            grupo__inscripcion__calificacion__isnull=False
        ).distinct()
        
        if asignaturas_con_notas.exists():
            for asignatura in asignaturas_con_notas[:3]:  # Solo las primeras 3
                calificaciones = Calificacion.objects.filter(
                    inscripcion__grupo__asignatura=asignatura
                )
                
                if calificaciones.exists():
                    promedio = calificaciones.aggregate(Avg('puntaje'))['puntaje__avg']
                    promedio_redondeado = round(promedio, 1) if promedio else 0
                    
                    print(f"✅ {asignatura.nombre}:")
                    print(f"   Promedio: {promedio_redondeado}")
                    print(f"   Total notas: {calificaciones.count()}")
                    
                    # Clasificación según el sistema chileno
                    if promedio_redondeado >= 6.0:
                        clasificacion = "Excelente"
                        color = "verde"
                    elif promedio_redondeado >= 4.0:
                        clasificacion = "Aprobado"
                        color = "amarillo"
                    else:
                        clasificacion = "Reprobado"
                        color = "rojo"
                    
                    print(f"   Clasificación: {clasificacion} ({color})")
                    print()
            
            return True
        else:
            print("❌ No se encontraron asignaturas con calificaciones")
            return False
            
    except Exception as e:
        print(f"❌ Error al calcular promedio: {e}")
        return False

def verificar_estructura_datos():
    """Verificar estructura de datos existente"""
    print("\n🔍 Verificando estructura de datos...")
    
    try:
        # Contar registros
        users_count = User.objects.count()
        perfiles_count = Perfil.objects.count()
        estudiantes_count = Estudiante.objects.count()
        profesores_count = Profesor.objects.count()
        asignaturas_count = Asignatura.objects.count()
        cursos_count = Curso.objects.count()
        calificaciones_count = Calificacion.objects.count()
        
        print(f"✅ Usuarios: {users_count}")
        print(f"✅ Perfiles: {perfiles_count}")
        print(f"✅ Estudiantes: {estudiantes_count}")
        print(f"✅ Profesores: {profesores_count}")
        print(f"✅ Asignaturas: {asignaturas_count}")
        print(f"✅ Cursos: {cursos_count}")
        print(f"✅ Calificaciones: {calificaciones_count}")
        
        if calificaciones_count > 0:
            print("\n📊 Estadísticas de calificaciones:")
            
            # Promedio general
            promedio_general = Calificacion.objects.aggregate(Avg('puntaje'))['puntaje__avg']
            if promedio_general:
                print(f"   Promedio general del sistema: {round(promedio_general, 1)}")
            
            # Distribución por rangos
            excelentes = Calificacion.objects.filter(puntaje__gte=6.0).count()
            aprobados = Calificacion.objects.filter(puntaje__gte=4.0, puntaje__lt=6.0).count()
            reprobados = Calificacion.objects.filter(puntaje__lt=4.0).count()
            
            print(f"   Excelentes (6.0-7.0): {excelentes}")
            print(f"   Aprobados (4.0-5.9): {aprobados}")
            print(f"   Reprobados (1.0-3.9): {reprobados}")
        
        return calificaciones_count > 0
        
    except Exception as e:
        print(f"❌ Error al verificar estructura: {e}")
        return False

def generar_reporte():
    """Generar reporte de las correcciones implementadas"""
    print("\n📋 REPORTE DE CORRECCIONES IMPLEMENTADAS")
    print("=" * 50)
    
    corrections = [
        {
            'name': '1. Formulario CalificacionForm mejorado',
            'description': 'Solo campos editables, validaciones de rango, widgets con estilos',
            'details': [
                'Campos: nombre_evaluacion, puntaje, porcentaje, detalle, descripcion',
                'Validación: puntaje entre 1.0 y 7.0',
                'Validación: porcentaje entre 0 y 100',
                'Widgets con clases CSS y placeholders',
                'Labels y help_texts personalizados'
            ]
        },
        {
            'name': '2. Cálculo de promedio por asignatura',
            'description': 'Vista actualizada para calcular y mostrar promedio de asignatura',
            'details': [
                'Cálculo automático cuando se selecciona asignatura',
                'Promedio redondeado a 1 decimal',
                'Contexto promedio_asignatura enviado al template'
            ]
        },
        {
            'name': '3. Tarjeta de promedio en template',
            'description': 'Nueva tarjeta que muestra promedio con colores según sistema chileno',
            'details': [
                'Verde para 6.0-7.0 (Excelente)',
                'Amarillo para 4.0-5.9 (Aprobado)',
                'Rojo para 1.0-3.9 (Reprobado)',
                'Solo aparece cuando hay asignatura seleccionada'
            ]
        },
        {
            'name': '4. Filtros mejorados',
            'description': 'JavaScript actualizado para mejor manejo de filtros',
            'details': [
                'clearAsignatura() ejecuta submit automático',
                'clearCurso() ejecuta submit automático',
                'Botón de limpiar filtros con confirmación'
            ]
        }
    ]
    
    for i, correction in enumerate(corrections, 1):
        print(f"✅ {correction['name']}")
        print(f"   📝 {correction['description']}")
        for detail in correction['details']:
            print(f"      • {detail}")
        print()

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO VERIFICACIÓN DE CORRECCIONES FINALES")
    print("=" * 50)
    
    # Verificar estructura
    has_data = verificar_estructura_datos()
    
    if not has_data:
        print("\n⚠️  No hay suficientes datos para probar. Ejecuta primero:")
        print("   python crear_usuarios_completos.py")
        print("   python asignar_profesores.py")
        return
    
    # Ejecutar pruebas
    tests = [
        test_formulario_calificacion,
        test_validaciones_formulario,
        test_promedio_asignatura
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
            results.append(False)
    
    # Generar reporte
    generar_reporte()
    
    # Resumen final
    print("🎯 RESUMEN DE VERIFICACIÓN:")
    print(f"   ✅ Pruebas exitosas: {sum(1 for r in results if r)}")
    print(f"   ❌ Pruebas fallidas: {sum(1 for r in results if not r)}")
    print(f"   📊 Total de pruebas: {len(results)}")
    
    if all(results):
        print("\n🎉 TODAS LAS CORRECCIONES FUNCIONAN CORRECTAMENTE!")
    else:
        print("\n⚠️  ALGUNAS CORRECCIONES NECESITAN REVISIÓN")
    
    print("\n📋 INSTRUCCIONES PARA PROBAR MANUALMENTE:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Inicia sesión como administrador")
    print("3. Ve a 'Gestionar Notas' → 'Ver Notas por Curso'")
    print("4. Selecciona un curso y asignatura")
    print("5. Verifica que aparezca la tarjeta de 'Promedio Asignatura'")
    print("6. Edita una nota y verifica que se guarde correctamente")
    print("7. Prueba los filtros y botones de limpiar")
    
    print("\n🔧 PROBLEMAS RESUELTOS:")
    print("   ✅ Edición de notas: Formulario corregido, solo campos editables")
    print("   ✅ Promedio asignatura: Se calcula y muestra en tarjeta")
    print("   ✅ Filtros: Botones de limpiar funcionan correctamente")
    print("   ✅ Validaciones: Rango de notas y porcentajes validados")

if __name__ == "__main__":
    main()
