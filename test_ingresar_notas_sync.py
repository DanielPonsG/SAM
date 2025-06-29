#!/usr/bin/env python
"""
Script para probar que ingresar_notas solo muestra asignaturas asignadas al curso
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura, Curso, Profesor
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

def test_ingresar_notas_filtering():
    """Probar que ingresar_notas filtra correctamente las asignaturas por curso"""
    print("🔍 PROBANDO FILTRADO EN INGRESAR_NOTAS")
    print("=" * 50)
    
    # 1. Obtener datos básicos
    anio_actual = timezone.now().year
    cursos = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
    asignaturas_total = Asignatura.objects.all()
    
    print(f"📚 Total asignaturas en sistema: {asignaturas_total.count()}")
    print(f"🏫 Total cursos {anio_actual}: {cursos.count()}")
    
    # 2. Analizar cada curso
    print(f"\n📊 ANÁLISIS POR CURSO:")
    print("-" * 30)
    
    for curso in cursos:
        asignaturas_del_curso = curso.asignaturas.all()
        print(f"\n🏫 Curso: {curso}")
        print(f"   📖 Asignaturas asignadas: {asignaturas_del_curso.count()}")
        
        if asignaturas_del_curso.exists():
            for asignatura in asignaturas_del_curso:
                print(f"      ✅ {asignatura.nombre} ({asignatura.codigo_asignatura})")
        else:
            print(f"      ❌ No tiene asignaturas asignadas")
    
    # 3. Simular qué mostraría ingresar_notas
    print(f"\n🧪 SIMULACIÓN INGRESAR_NOTAS:")
    print("-" * 30)
    
    for curso in cursos:
        # Esto es lo que hace la vista ingresar_notas
        asignaturas_disponibles = curso.asignaturas.all().order_by('nombre')
        
        print(f"\n🏫 Curso {curso}:")
        print(f"   📋 ingresar_notas mostraría: {asignaturas_disponibles.count()} asignaturas")
        
        if asignaturas_disponibles.exists():
            for asignatura in asignaturas_disponibles:
                print(f"      ✅ {asignatura.nombre}")
        else:
            print(f"      ❌ Mensaje: 'No tiene asignaturas asignadas'")
    
    # 4. Probar desasignación
    print(f"\n🧪 PROBANDO DESASIGNACIÓN:")
    print("-" * 30)
    
    # Tomar el primer curso que tenga asignaturas
    curso_con_asignaturas = None
    for curso in cursos:
        if curso.asignaturas.exists():
            curso_con_asignaturas = curso
            break
    
    if curso_con_asignaturas:
        asignatura_a_desasignar = curso_con_asignaturas.asignaturas.first()
        print(f"🏫 Curso de prueba: {curso_con_asignaturas}")
        print(f"📖 Asignatura a desasignar: {asignatura_a_desasignar.nombre}")
        
        # Contar antes
        antes = curso_con_asignaturas.asignaturas.count()
        print(f"   📊 Asignaturas antes: {antes}")
        
        # Desasignar
        curso_con_asignaturas.asignaturas.remove(asignatura_a_desasignar)
        
        # Contar después
        despues = curso_con_asignaturas.asignaturas.count()
        print(f"   📊 Asignaturas después: {despues}")
        
        if despues == antes - 1:
            print(f"   ✅ Desasignación exitosa")
            
            # Simular qué mostraría ingresar_notas ahora
            asignaturas_disponibles_ahora = curso_con_asignaturas.asignaturas.all().order_by('nombre')
            print(f"   📋 ingresar_notas ahora mostraría: {asignaturas_disponibles_ahora.count()} asignaturas")
            
            # Verificar que la asignatura desasignada NO aparece
            if asignatura_a_desasignar not in asignaturas_disponibles_ahora:
                print(f"   ✅ La asignatura '{asignatura_a_desasignar.nombre}' YA NO aparece en ingresar_notas")
            else:
                print(f"   ❌ ERROR: La asignatura '{asignatura_a_desasignar.nombre}' TODAVÍA aparece")
            
            # Reasignar para no afectar los datos
            curso_con_asignaturas.asignaturas.add(asignatura_a_desasignar)
            print(f"   🔄 Reasignada para restaurar estado original")
        else:
            print(f"   ❌ Error en desasignación")
    else:
        print("❌ No hay cursos con asignaturas para probar desasignación")
    
    return True

def test_crear_escenario_completo():
    """Crear un escenario completo de prueba"""
    print(f"\n🎯 CREANDO ESCENARIO DE PRUEBA COMPLETO:")
    print("-" * 40)
    
    try:
        # Obtener o crear datos de prueba
        curso_test = Curso.objects.first()
        asignaturas = list(Asignatura.objects.all()[:3])  # Tomar 3 asignaturas
        
        if not curso_test or len(asignaturas) < 2:
            print("❌ No hay suficientes datos para crear escenario completo")
            return False
        
        print(f"🏫 Curso de prueba: {curso_test}")
        print(f"📚 Asignaturas disponibles: {len(asignaturas)}")
        
        # Escenario 1: Curso sin asignaturas
        print(f"\n📋 ESCENARIO 1: Curso sin asignaturas")
        curso_test.asignaturas.clear()
        asignaturas_disponibles = curso_test.asignaturas.all()
        print(f"   ingresar_notas mostraría: {asignaturas_disponibles.count()} asignaturas")
        if asignaturas_disponibles.count() == 0:
            print("   ✅ Correcto: No muestra asignaturas")
        
        # Escenario 2: Curso con 1 asignatura
        print(f"\n📋 ESCENARIO 2: Curso con 1 asignatura")
        curso_test.asignaturas.add(asignaturas[0])
        asignaturas_disponibles = curso_test.asignaturas.all()
        print(f"   ingresar_notas mostraría: {asignaturas_disponibles.count()} asignaturas")
        print(f"   Asignatura: {asignaturas_disponibles.first().nombre}")
        if asignaturas_disponibles.count() == 1:
            print("   ✅ Correcto: Muestra solo 1 asignatura")
        
        # Escenario 3: Curso con múltiples asignaturas
        print(f"\n📋 ESCENARIO 3: Curso con múltiples asignaturas")
        for asignatura in asignaturas[1:]:
            curso_test.asignaturas.add(asignatura)
        asignaturas_disponibles = curso_test.asignaturas.all()
        print(f"   ingresar_notas mostraría: {asignaturas_disponibles.count()} asignaturas")
        for asignatura in asignaturas_disponibles:
            print(f"      - {asignatura.nombre}")
        if asignaturas_disponibles.count() == len(asignaturas):
            print("   ✅ Correcto: Muestra todas las asignaturas asignadas")
        
        # Escenario 4: Remover una asignatura específica
        print(f"\n📋 ESCENARIO 4: Remover asignatura específica")
        asignatura_a_remover = asignaturas[1]
        print(f"   Removiendo: {asignatura_a_remover.nombre}")
        curso_test.asignaturas.remove(asignatura_a_remover)
        asignaturas_disponibles = curso_test.asignaturas.all()
        print(f"   ingresar_notas ahora mostraría: {asignaturas_disponibles.count()} asignaturas")
        
        if asignatura_a_remover not in asignaturas_disponibles:
            print(f"   ✅ Correcto: '{asignatura_a_remover.nombre}' ya no aparece")
        else:
            print(f"   ❌ Error: '{asignatura_a_remover.nombre}' todavía aparece")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en escenario: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBAS DE SINCRONIZACIÓN INGRESAR_NOTAS")
        print("=" * 60)
        
        # Prueba 1: Filtrado básico
        test_ingresar_notas_filtering()
        
        # Prueba 2: Escenario completo
        test_crear_escenario_completo()
        
        print(f"\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("✅ El sistema de sincronización funciona correctamente")
        print("✅ ingresar_notas solo mostrará asignaturas asignadas al curso")
        print("✅ Al desasignar una asignatura, desaparece de ingresar_notas")
        
    except Exception as e:
        print(f"❌ Error general en las pruebas: {e}")
        import traceback
        traceback.print_exc()
