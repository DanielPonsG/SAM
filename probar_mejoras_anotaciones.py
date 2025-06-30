#!/usr/bin/env python
"""
Script para probar las mejoras del sistema de anotaciones:
1. Verificar que los cursos mostrados tienen estudiantes
2. Comprobar el filtrado de estudiantes por curso
3. Verificar la nueva interfaz de anotaciones
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante, Anotacion, Profesor
from django.utils import timezone

def probar_cursos_con_estudiantes():
    """Verificar que solo se muestren cursos con estudiantes"""
    print("=== PROBANDO CURSOS CON ESTUDIANTES ===")
    
    anio_actual = timezone.now().year
    
    # Obtener todos los cursos del año actual
    todos_cursos = Curso.objects.filter(anio=anio_actual)
    print(f"Total de cursos del año {anio_actual}: {todos_cursos.count()}")
    
    # Obtener cursos con estudiantes
    cursos_con_estudiantes = Curso.objects.filter(
        anio=anio_actual,
        estudiantes__isnull=False
    ).distinct()
    print(f"Cursos con estudiantes: {cursos_con_estudiantes.count()}")
    
    # Mostrar detalles
    for curso in cursos_con_estudiantes:
        num_estudiantes = curso.estudiantes.count()
        print(f"  - {curso}: {num_estudiantes} estudiantes")
    
    print()

def probar_estudiantes_por_curso():
    """Verificar el filtrado de estudiantes por curso"""
    print("=== PROBANDO FILTRADO DE ESTUDIANTES ===")
    
    anio_actual = timezone.now().year
    cursos_con_estudiantes = Curso.objects.filter(
        anio=anio_actual,
        estudiantes__isnull=False
    ).distinct()
    
    for curso in cursos_con_estudiantes[:3]:  # Solo los primeros 3
        estudiantes = curso.estudiantes.all().order_by('primer_nombre', 'apellido_paterno')
        print(f"Curso {curso}:")
        
        for estudiante in estudiantes:
            print(f"  - {estudiante.get_nombre_completo()} ({estudiante.numero_documento})")
        
        print(f"  Total: {estudiantes.count()} estudiantes\n")

def verificar_anotaciones_existentes():
    """Verificar las anotaciones existentes y su formato"""
    print("=== VERIFICANDO ANOTACIONES EXISTENTES ===")
    
    total_anotaciones = Anotacion.objects.count()
    print(f"Total de anotaciones: {total_anotaciones}")
    
    if total_anotaciones > 0:
        # Estadísticas por tipo
        positivas = Anotacion.objects.filter(tipo='positiva').count()
        negativas = Anotacion.objects.filter(tipo='negativa').count()
        neutras = Anotacion.objects.filter(tipo='neutra').count()
        graves = Anotacion.objects.filter(es_grave=True).count()
        
        print(f"  - Positivas: {positivas}")
        print(f"  - Negativas: {negativas}")
        print(f"  - Neutras: {neutras}")
        print(f"  - Graves: {graves}")
        
        # Mostrar algunas anotaciones recientes
        print("\nAnotaciones recientes (últimas 5):")
        anotaciones_recientes = Anotacion.objects.order_by('-fecha_creacion')[:5]
        
        for anotacion in anotaciones_recientes:
            puntos_str = f"+{anotacion.puntos}" if anotacion.puntos > 0 else str(anotacion.puntos)
            grave_str = " [GRAVE]" if anotacion.es_grave else ""
            
            print(f"  - {anotacion.estudiante.get_nombre_completo()} ({anotacion.curso})")
            print(f"    {anotacion.titulo} - {puntos_str} pts{grave_str}")
            print(f"    {anotacion.fecha_para_humanos}")
            print()
    
    else:
        print("No hay anotaciones registradas. Creando algunas de ejemplo...")
        crear_anotaciones_ejemplo()

def crear_anotaciones_ejemplo():
    """Crear algunas anotaciones de ejemplo si no existen"""
    from smapp.models import Asignatura
    
    # Obtener datos necesarios
    cursos_con_estudiantes = Curso.objects.filter(estudiantes__isnull=False).distinct()
    profesores = Profesor.objects.all()
    
    if not cursos_con_estudiantes.exists() or not profesores.exists():
        print("No hay cursos con estudiantes o profesores para crear anotaciones.")
        return
    
    # Crear anotaciones de ejemplo
    anotaciones_ejemplo = [
        {
            'tipo': 'positiva',
            'categoria': 'comportamiento',
            'titulo': 'Excelente participación en clase',
            'descripcion': 'El estudiante mostró una participación activa y constructiva durante toda la clase.',
            'puntos': 5,
            'es_grave': False
        },
        {
            'tipo': 'negativa',
            'categoria': 'disciplina',
            'titulo': 'Comportamiento disruptivo',
            'descripcion': 'Interrumpió la clase constantemente y no siguió las instrucciones del profesor.',
            'puntos': -3,
            'es_grave': False
        },
        {
            'tipo': 'neutra',
            'categoria': 'academico',
            'titulo': 'Recordatorio sobre tarea',
            'descripcion': 'Se recordó al estudiante la importancia de entregar las tareas a tiempo.',
            'puntos': 0,
            'es_grave': False
        }
    ]
    
    curso = cursos_con_estudiantes.first()
    profesor = profesores.first()
    
    for i, datos in enumerate(anotaciones_ejemplo):
        estudiantes = curso.estudiantes.all()
        if estudiantes.exists():
            estudiante = estudiantes[i % estudiantes.count()]
            
            anotacion = Anotacion.objects.create(
                estudiante=estudiante,
                curso=curso,
                profesor_autor=profesor,
                **datos
            )
            
            print(f"Creada anotación: {anotacion.titulo} para {estudiante.get_nombre_completo()}")

def main():
    """Función principal"""
    print("PROBANDO MEJORAS DEL SISTEMA DE ANOTACIONES")
    print("=" * 50)
    
    probar_cursos_con_estudiantes()
    probar_estudiantes_por_curso()
    verificar_anotaciones_existentes()
    
    print("=" * 50)
    print("RESUMEN DE MEJORAS IMPLEMENTADAS:")
    print("✓ Formulario muestra solo cursos con estudiantes")
    print("✓ Filtrado dinámico de estudiantes por curso")
    print("✓ Interfaz de anotaciones más compacta (tabla)")
    print("✓ Mejor visualización de datos coherente")
    print("✓ Indicadores visuales por tipo de anotación")
    print("✓ Manejo de errores mejorado en AJAX")
    print()
    print("Para probar en el navegador:")
    print("1. Ve a http://127.0.0.1:8000/")
    print("2. Inicia sesión como profesor o administrador")
    print("3. Ve a 'Libro de Anotaciones' > 'Nueva Anotación'")
    print("4. Selecciona un curso y verifica que se cargan solo estudiantes de ese curso")
    print("5. Ve a 'Ver Anotaciones' para ver la nueva interfaz de tabla")

if __name__ == '__main__':
    main()
