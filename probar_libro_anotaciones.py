#!/usr/bin/env python
"""
Script para probar rápidamente el libro de anotaciones
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Estudiante, Profesor, Anotacion, calcular_puntaje_comportamiento

def mostrar_estadisticas_anotaciones():
    """Muestra estadísticas del libro de anotaciones"""
    print("📊 ESTADÍSTICAS DEL LIBRO DE ANOTACIONES")
    print("=" * 50)
    
    # Estadísticas generales
    total_anotaciones = Anotacion.objects.count()
    positivas = Anotacion.objects.filter(tipo='positiva').count()
    negativas = Anotacion.objects.filter(tipo='negativa').count()
    neutras = Anotacion.objects.filter(tipo='neutra').count()
    graves = Anotacion.objects.filter(es_grave=True).count()
    
    print(f"Total de anotaciones: {total_anotaciones}")
    print(f"  • Positivas: {positivas}")
    print(f"  • Negativas: {negativas}")
    print(f"  • Neutras: {neutras}")
    print(f"  • Graves: {graves}")
    print()
    
    # Top 5 estudiantes con mejor comportamiento
    print("🏆 TOP 5 ESTUDIANTES CON MEJOR COMPORTAMIENTO:")
    estudiantes = Estudiante.objects.all()
    estudiantes_puntuacion = []
    
    for estudiante in estudiantes:
        stats = calcular_puntaje_comportamiento(estudiante)
        estudiantes_puntuacion.append((estudiante, stats))
    
    # Ordenar por puntaje descendente
    estudiantes_puntuacion.sort(key=lambda x: x[1]['puntaje_total'], reverse=True)
    
    for i, (estudiante, stats) in enumerate(estudiantes_puntuacion[:5], 1):
        print(f"{i}. {estudiante.get_nombre_completo()}: {stats['puntaje_total']} puntos ({stats['nivel']})")
    
    print()
    
    # Estudiantes que requieren atención
    print("⚠️  ESTUDIANTES QUE REQUIEREN ATENCIÓN:")
    estudiantes_atencion = []
    
    for estudiante, stats in estudiantes_puntuacion:
        if stats['puntaje_total'] < 0 or stats['graves'] > 0:
            estudiantes_atencion.append((estudiante, stats))
    
    if estudiantes_atencion:
        for estudiante, stats in estudiantes_atencion:
            print(f"  • {estudiante.get_nombre_completo()}: {stats['puntaje_total']} puntos")
            if stats['graves'] > 0:
                print(f"    ⚠️  {stats['graves']} anotaciones graves")
    else:
        print("  ✅ No hay estudiantes que requieran atención especial")
    
    print()
    
    # Anotaciones por categoría
    print("📈 ANOTACIONES POR CATEGORÍA:")
    from collections import Counter
    
    categorias = Anotacion.objects.values_list('categoria', flat=True)
    counter_categorias = Counter(categorias)
    
    for categoria, count in counter_categorias.most_common():
        categoria_display = dict(Anotacion.CATEGORIAS).get(categoria, categoria)
        print(f"  • {categoria_display}: {count}")
    
    print()
    
    # Profesores más activos
    print("👨‍🏫 PROFESORES MÁS ACTIVOS EN ANOTACIONES:")
    from collections import Counter
    
    profesores_anotaciones = Anotacion.objects.values_list('profesor_autor__primer_nombre', 'profesor_autor__apellido_paterno')
    counter_profesores = Counter([f"{nombre} {apellido}" for nombre, apellido in profesores_anotaciones])
    
    for profesor, count in counter_profesores.most_common(5):
        print(f"  • {profesor}: {count} anotaciones")

def mostrar_detalle_estudiante(codigo_estudiante):
    """Muestra el detalle de comportamiento de un estudiante específico"""
    try:
        estudiante = Estudiante.objects.get(codigo_estudiante=codigo_estudiante)
        print(f"📋 DETALLE DE COMPORTAMIENTO: {estudiante.get_nombre_completo()}")
        print("=" * 60)
        
        stats = calcular_puntaje_comportamiento(estudiante)
        
        print(f"Puntaje Total: {stats['puntaje_total']} puntos")
        print(f"Nivel de Comportamiento: {stats['nivel']}")
        print(f"Total de Anotaciones: {stats['total_anotaciones']}")
        print(f"  • Positivas: {stats['positivas']}")
        print(f"  • Negativas: {stats['negativas']}")
        print(f"  • Neutras: {stats['neutras']}")
        print(f"  • Graves: {stats['graves']}")
        print()
        
        # Mostrar últimas anotaciones
        print("📚 ÚLTIMAS ANOTACIONES:")
        anotaciones = Anotacion.objects.filter(estudiante=estudiante).order_by('-fecha_creacion')[:10]
        
        for anotacion in anotaciones:
            tipo_emoji = "✅" if anotacion.tipo == 'positiva' else "❌" if anotacion.tipo == 'negativa' else "ℹ️"
            grave_txt = " ⚠️ GRAVE" if anotacion.es_grave else ""
            print(f"  {tipo_emoji} {anotacion.fecha_creacion.strftime('%d/%m/%Y')}: {anotacion.titulo} ({anotacion.puntos} pts){grave_txt}")
            print(f"     📝 {anotacion.descripcion[:100]}...")
            print(f"     👨‍🏫 {anotacion.profesor_autor.get_nombre_completo()}")
            print()
        
    except Estudiante.DoesNotExist:
        print(f"❌ No se encontró un estudiante con código: {codigo_estudiante}")
        print("📝 Estudiantes disponibles:")
        for est in Estudiante.objects.all()[:10]:
            print(f"  • {est.codigo_estudiante}: {est.get_nombre_completo()}")

def main():
    print("🎓 SISTEMA DE LIBRO DE ANOTACIONES - PRUEBA RÁPIDA")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        codigo_estudiante = sys.argv[1]
        mostrar_detalle_estudiante(codigo_estudiante)
    else:
        mostrar_estadisticas_anotaciones()
    
    print()
    print("🌐 Accede al sistema completo en: http://127.0.0.1:8000/")
    print("📚 Libro de anotaciones: http://127.0.0.1:8000/anotaciones/")
    print()
    print("💡 Para ver detalle de un estudiante: python probar_libro_anotaciones.py EST001")

if __name__ == '__main__':
    main()
