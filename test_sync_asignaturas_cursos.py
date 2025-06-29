#!/usr/bin/env python
"""
Script para probar la sincronización entre asignaturas y cursos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura, Curso, Profesor
from django.utils import timezone

def test_asignatura_curso_sync():
    """Probar la sincronización entre asignaturas y cursos"""
    print("🔍 PROBANDO SINCRONIZACIÓN ASIGNATURA-CURSO")
    print("=" * 50)
    
    # 1. Verificar asignaturas existentes
    asignaturas = Asignatura.objects.all()
    print(f"📚 Total de asignaturas: {asignaturas.count()}")
    
    # 2. Verificar cursos existentes
    anio_actual = timezone.now().year
    cursos = Curso.objects.filter(anio=anio_actual)
    print(f"🏫 Total de cursos {anio_actual}: {cursos.count()}")
    
    # 3. Mostrar estadísticas de asignación
    asignaturas_con_cursos = 0
    asignaturas_sin_cursos = 0
    
    print("\n📊 ESTADÍSTICAS DE ASIGNACIÓN:")
    print("-" * 30)
    
    for asignatura in asignaturas:
        cursos_asignados = asignatura.get_cursos_asignados()
        if cursos_asignados.exists():
            asignaturas_con_cursos += 1
            print(f"✅ {asignatura.nombre} → {cursos_asignados.count()} curso(s)")
        else:
            asignaturas_sin_cursos += 1
            print(f"❌ {asignatura.nombre} → Sin cursos")
    
    print(f"\n📈 RESUMEN:")
    print(f"   Con cursos: {asignaturas_con_cursos}")
    print(f"   Sin cursos: {asignaturas_sin_cursos}")
    
    # 4. Probar métodos del modelo
    print(f"\n🧪 PROBANDO MÉTODOS DEL MODELO:")
    print("-" * 30)
    
    if asignaturas.exists():
        asignatura_test = asignaturas.first()
        print(f"📖 Asignatura de prueba: {asignatura_test.nombre}")
        print(f"   get_cursos_nombres(): {asignatura_test.get_cursos_nombres()}")
        print(f"   tiene_cursos(): {asignatura_test.tiene_cursos()}")
        print(f"   get_info_completa(): {asignatura_test.get_info_completa()}")
    
    return {
        'total_asignaturas': asignaturas.count(),
        'con_cursos': asignaturas_con_cursos,
        'sin_cursos': asignaturas_sin_cursos,
        'total_cursos': cursos.count()
    }

def test_crear_asignacion():
    """Probar crear una asignación de prueba"""
    print(f"\n🧪 PROBANDO ASIGNACIÓN DE PRUEBA:")
    print("-" * 30)
    
    # Buscar una asignatura y un curso
    asignatura = Asignatura.objects.first()
    curso = Curso.objects.first()
    
    if not asignatura or not curso:
        print("❌ No hay asignaturas o cursos para probar")
        return False
    
    print(f"📖 Asignatura: {asignatura.nombre}")
    print(f"🏫 Curso: {curso}")
    
    # Verificar si ya está asignada
    if asignatura in curso.asignaturas.all():
        print("ℹ️  Ya está asignada")
        return True
    
    # Asignar
    try:
        curso.asignaturas.add(asignatura)
        print("✅ Asignación exitosa")
        
        # Verificar
        if asignatura in curso.asignaturas.all():
            print("✅ Verificación exitosa - Aparece en curso.asignaturas.all()")
        
        if curso in asignatura.cursos.all():
            print("✅ Verificación exitosa - Aparece en asignatura.cursos.all()")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al asignar: {e}")
        return False

if __name__ == "__main__":
    try:
        stats = test_asignatura_curso_sync()
        test_crear_asignacion()
        
        print(f"\n🎉 PRUEBA COMPLETADA")
        print(f"📊 Estadísticas finales: {stats}")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
