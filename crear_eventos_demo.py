#!/usr/bin/env python
"""
Script para crear eventos de prueba específicos para cada tipo de usuario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, Curso, Profesor, Estudiante
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta

def crear_eventos_completos():
    """Crear eventos específicos para demostrar todas las funcionalidades"""
    print("🎯 CREANDO EVENTOS COMPLETOS PARA DEMOSTRACIÓN")
    print("=" * 55)
    
    # Limpiar eventos anteriores
    EventoCalendario.objects.all().delete()
    print("🗑️ Eventos anteriores eliminados")
    
    hoy = timezone.now().date()
    cursos = list(Curso.objects.all())
    
    if not cursos:
        print("❌ No hay cursos disponibles")
        return
    
    # 1. Eventos para TODOS LOS CURSOS (visibles para todos)
    eventos_globales = [
        {
            'titulo': '🎉 Día del Estudiante',
            'descripcion': 'Celebración especial para todos los estudiantes del colegio con actividades recreativas',
            'fecha': hoy + timedelta(days=3),
            'hora_inicio': time(9, 0),
            'hora_fin': time(15, 0),
            'tipo_evento': 'actividad',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '👨‍👩‍👧‍👦 Reunión General de Apoderados',
            'descripcion': 'Reunión informativa sobre el progreso académico y actividades del segundo semestre',
            'fecha': hoy + timedelta(days=7),
            'hora_inicio': time(19, 0),
            'hora_fin': time(20, 30),
            'tipo_evento': 'reunion',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '📚 Feria del Libro',
            'descripcion': 'Feria anual del libro con presentaciones de autores y venta de libros',
            'fecha': hoy + timedelta(days=12),
            'hora_inicio': time(10, 0),
            'hora_fin': time(16, 0),
            'tipo_evento': 'actividad',
            'prioridad': 'media',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '🏥 Vacunación Escolar',
            'descripcion': 'Programa de vacunación del Ministerio de Salud',
            'fecha': hoy + timedelta(days=15),
            'hora_inicio': time(9, 0),
            'hora_fin': time(12, 0),
            'tipo_evento': 'administrativo',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        }
    ]
    
    print("\n📢 EVENTOS GLOBALES (todos los cursos):")
    for evento_data in eventos_globales:
        evento = EventoCalendario.objects.create(**evento_data)
        print(f"   ✅ {evento.titulo} - {evento.fecha}")
    
    # 2. Eventos específicos por CURSO
    eventos_por_curso = [
        # Para 1° Básico A
        {
            'titulo': '📐 Evaluación de Matemáticas',
            'descripcion': 'Prueba sumativa: Números hasta el 100, sumas y restas',
            'fecha': hoy + timedelta(days=5),
            'hora_inicio': time(9, 0),
            'hora_fin': time(10, 0),
            'tipo_evento': 'evaluacion',
            'prioridad': 'alta',
            'para_todos_los_cursos': False,
            'cursos': [cursos[0]] if cursos else []
        },
        {
            'titulo': '📖 Control de Lectura',
            'descripcion': 'Control del libro "El principito" - Capítulos 1 al 5',
            'fecha': hoy + timedelta(days=8),
            'hora_inicio': time(10, 0),
            'hora_fin': time(10, 45),
            'tipo_evento': 'evaluacion',
            'prioridad': 'media',
            'para_todos_los_cursos': False,
            'cursos': [cursos[0]] if cursos else []
        },
        # Para 1° Básico B
        {
            'titulo': '🎨 Taller de Arte',
            'descripcion': 'Creación de murales con técnicas de collage',
            'fecha': hoy + timedelta(days=6),
            'hora_inicio': time(14, 0),
            'hora_fin': time(15, 30),
            'tipo_evento': 'actividad',
            'prioridad': 'media',
            'para_todos_los_cursos': False,
            'cursos': [cursos[1]] if len(cursos) > 1 else []
        },
        # Para 1° Medio A
        {
            'titulo': '🧪 Laboratorio de Química',
            'descripcion': 'Práctica: Reacciones ácido-base con indicadores naturales',
            'fecha': hoy + timedelta(days=4),
            'hora_inicio': time(11, 0),
            'hora_fin': time(12, 30),
            'tipo_evento': 'actividad',
            'prioridad': 'alta',
            'para_todos_los_cursos': False,
            'cursos': [cursos[2]] if len(cursos) > 2 else []
        },
        {
            'titulo': '📊 Evaluación de Historia',
            'descripcion': 'Prueba: Primera Guerra Mundial y sus consecuencias',
            'fecha': hoy + timedelta(days=9),
            'hora_inicio': time(9, 0),
            'hora_fin': time(10, 30),
            'tipo_evento': 'evaluacion',
            'prioridad': 'alta',
            'para_todos_los_cursos': False,
            'cursos': [cursos[2]] if len(cursos) > 2 else []
        }
    ]
    
    print("\n🏫 EVENTOS POR CURSO ESPECÍFICO:")
    for evento_data in eventos_por_curso:
        cursos_asignados = evento_data.pop('cursos', [])
        evento = EventoCalendario.objects.create(**evento_data)
        
        if cursos_asignados:
            evento.cursos.set(cursos_asignados)
            cursos_str = ", ".join([str(c) for c in cursos_asignados])
            print(f"   ✅ {evento.titulo} - {evento.fecha} → {cursos_str}")
        else:
            print(f"   ✅ {evento.titulo} - {evento.fecha} → Sin cursos")
    
    # 3. Eventos administrativos (solo para admin/director)
    eventos_admin = [
        {
            'titulo': '📋 Consejo de Profesores',
            'descripcion': 'Reunión mensual del equipo docente para evaluar el progreso académico',
            'fecha': hoy + timedelta(days=11),
            'hora_inicio': time(16, 0),
            'hora_fin': time(18, 0),
            'tipo_evento': 'reunion',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '💼 Evaluación Institucional',
            'descripcion': 'Proceso de autoevaluación institucional según estándares del MINEDUC',
            'fecha': hoy + timedelta(days=18),
            'tipo_evento': 'administrativo',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '📈 Análisis de Resultados SIMCE',
            'descripcion': 'Reunión para analizar resultados y plan de mejora',
            'fecha': hoy + timedelta(days=22),
            'hora_inicio': time(14, 0),
            'hora_fin': time(17, 0),
            'tipo_evento': 'reunion',
            'prioridad': 'media',
            'para_todos_los_cursos': True,
        }
    ]
    
    print("\n🏛️ EVENTOS ADMINISTRATIVOS:")
    for evento_data in eventos_admin:
        evento = EventoCalendario.objects.create(**evento_data)
        print(f"   ✅ {evento.titulo} - {evento.fecha}")
    
    # 4. Eventos especiales con diferentes prioridades
    eventos_especiales = [
        {
            'titulo': '🚨 Simulacro de Evacuación',
            'descripcion': 'Simulacro de evacuación por terremoto - Obligatorio para todos',
            'fecha': hoy + timedelta(days=2),
            'hora_inicio': time(10, 30),
            'hora_fin': time(11, 0),
            'tipo_evento': 'administrativo',
            'prioridad': 'alta',
            'para_todos_los_cursos': True,
        },
        {
            'titulo': '🍎 Desayuno Saludable',
            'descripcion': 'Actividad de promoción de alimentación saludable',
            'fecha': hoy + timedelta(days=14),
            'hora_inicio': time(8, 0),
            'hora_fin': time(9, 0),
            'tipo_evento': 'actividad',
            'prioridad': 'baja',
            'para_todos_los_cursos': True,
        }
    ]
    
    print("\n🌟 EVENTOS ESPECIALES:")
    for evento_data in eventos_especiales:
        evento = EventoCalendario.objects.create(**evento_data)
        print(f"   ✅ {evento.titulo} - {evento.fecha}")
    
    # Mostrar resumen final
    total_eventos = EventoCalendario.objects.count()
    eventos_globales_count = EventoCalendario.objects.filter(para_todos_los_cursos=True).count()
    eventos_especificos_count = EventoCalendario.objects.filter(para_todos_los_cursos=False).count()
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Total eventos creados: {total_eventos}")
    print(f"   Eventos globales: {eventos_globales_count}")
    print(f"   Eventos específicos: {eventos_especificos_count}")
    
    # Mostrar distribución por tipo
    print(f"\n📋 DISTRIBUCIÓN POR TIPO:")
    for tipo, nombre in EventoCalendario.TIPO_EVENTO_CHOICES:
        count = EventoCalendario.objects.filter(tipo_evento=tipo).count()
        if count > 0:
            print(f"   {nombre}: {count}")
    
    return total_eventos

if __name__ == "__main__":
    try:
        eventos_creados = crear_eventos_completos()
        
        print(f"\n🎉 EVENTOS CREADOS EXITOSAMENTE")
        print("✅ El calendario ahora tiene eventos de demostración completos")
        print("✅ Eventos para todos los tipos de usuario")
        print("✅ Diferentes tipos y prioridades de eventos")
        print("\n🌐 Puedes ver el calendario en: http://127.0.0.1:8000/calendario/")
        
    except Exception as e:
        print(f"❌ Error al crear eventos: {e}")
        import traceback
        traceback.print_exc()
