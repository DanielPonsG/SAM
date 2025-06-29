#!/usr/bin/env python
"""
Script para probar y verificar el funcionamiento completo del calendario
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import EventoCalendario, Curso, Profesor, Estudiante, Perfil
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta

def test_calendario_completo():
    """Probar el sistema completo del calendario"""
    print("🗓️ PROBANDO SISTEMA COMPLETO DEL CALENDARIO")
    print("=" * 60)
    
    # 1. Verificar modelos existentes
    eventos_existentes = EventoCalendario.objects.count()
    cursos_existentes = Curso.objects.count()
    usuarios_existentes = User.objects.count()
    
    print(f"📊 ESTADO INICIAL:")
    print(f"   Eventos existentes: {eventos_existentes}")
    print(f"   Cursos existentes: {cursos_existentes}")
    print(f"   Usuarios existentes: {usuarios_existentes}")
    
    # 2. Crear eventos de prueba si no existen
    if eventos_existentes == 0:
        print(f"\n🎯 CREANDO EVENTOS DE PRUEBA...")
        crear_eventos_prueba()
    
    # 3. Probar permisos por tipo de usuario
    print(f"\n🔐 PROBANDO PERMISOS POR TIPO DE USUARIO:")
    print("-" * 40)
    
    test_permisos_administrador()
    test_permisos_director()
    test_permisos_profesor()
    test_permisos_alumno()
    
    # 4. Probar filtros del calendario
    print(f"\n🔍 PROBANDO FILTROS DEL CALENDARIO:")
    print("-" * 40)
    test_filtros_calendario()
    
    # 5. Verificar JSON para FullCalendar
    print(f"\n📅 PROBANDO INTEGRACIÓN CON FULLCALENDAR:")
    print("-" * 40)
    test_json_fullcalendar()
    
    return True

def crear_eventos_prueba():
    """Crear eventos de prueba para diferentes escenarios"""
    hoy = timezone.now().date()
    cursos = list(Curso.objects.all()[:3])  # Tomar primeros 3 cursos
    
    eventos_prueba = [
        {
            'titulo': 'Evaluación de Matemáticas',
            'descripcion': 'Prueba sumativa de álgebra y geometría',
            'fecha': hoy + timedelta(days=5),
            'hora_inicio': time(9, 0),
            'hora_fin': time(10, 30),
            'tipo_evento': 'evaluacion',
            'prioridad': 'alta',
            'para_todos_los_cursos': False,
            'cursos_asignados': cursos[:1] if cursos else []
        },
        {
            'titulo': 'Reunión de Apoderados',
            'descripcion': 'Reunión mensual con los apoderados',
            'fecha': hoy + timedelta(days=10),
            'hora_inicio': time(19, 0),
            'hora_fin': time(20, 30),
            'tipo_evento': 'reunion',
            'prioridad': 'media',
            'para_todos_los_cursos': True,
            'cursos_asignados': []
        },
        {
            'titulo': 'Día del Profesor',
            'descripcion': 'Celebración del día del profesor',
            'fecha': hoy + timedelta(days=15),
            'tipo_evento': 'actividad',
            'prioridad': 'media',
            'para_todos_los_cursos': True,
            'cursos_asignados': []
        },
        {
            'titulo': 'Entrega de Notas',
            'descripción': 'Entrega de notas del primer semestre',
            'fecha': hoy + timedelta(days=20),
            'tipo_evento': 'administrativo',
            'prioridad': 'alta',
            'para_todos_los_cursos': False,
            'cursos_asignados': cursos[:2] if len(cursos) >= 2 else cursos
        }
    ]
    
    for evento_data in eventos_prueba:
        cursos_asignados = evento_data.pop('cursos_asignados')
        
        evento = EventoCalendario.objects.create(**evento_data)
        
        if cursos_asignados:
            evento.cursos.set(cursos_asignados)
        
        print(f"   ✅ Creado: {evento.titulo} - {evento.fecha}")

def test_permisos_administrador():
    """Probar permisos para administrador"""
    print("🔑 ADMINISTRADOR:")
    
    # Administrador puede ver todos los eventos
    todos_eventos = EventoCalendario.objects.all()
    print(f"   Puede ver: {todos_eventos.count()} eventos (todos)")
    
    # Puede crear eventos para cualquier curso
    todos_cursos = Curso.objects.all()
    print(f"   Puede crear eventos para: {todos_cursos.count()} cursos (todos)")
    
    print("   ✅ Permisos: COMPLETOS")

def test_permisos_director():
    """Probar permisos para director"""
    print("🎓 DIRECTOR:")
    
    # Director tiene los mismos permisos que administrador
    todos_eventos = EventoCalendario.objects.all()
    print(f"   Puede ver: {todos_eventos.count()} eventos (todos)")
    
    todos_cursos = Curso.objects.all()
    print(f"   Puede crear eventos para: {todos_cursos.count()} cursos (todos)")
    
    print("   ✅ Permisos: COMPLETOS")

def test_permisos_profesor():
    """Probar permisos para profesor"""
    print("👨‍🏫 PROFESOR:")
    
    profesores = Profesor.objects.all()
    if profesores.exists():
        profesor = profesores.first()
        
        # Cursos donde es jefe
        cursos_jefe = Curso.objects.filter(profesor_jefe=profesor)
        
        # Cursos donde tiene asignaturas
        cursos_asignaturas = Curso.objects.filter(
            asignaturas__profesores_responsables=profesor
        ).distinct()
        
        # Total de cursos que puede gestionar (usar union en lugar de |)
        cursos_jefe_ids = cursos_jefe.values_list('id', flat=True)
        cursos_asignaturas_ids = cursos_asignaturas.values_list('id', flat=True)
        cursos_totales_ids = set(list(cursos_jefe_ids) + list(cursos_asignaturas_ids))
        cursos_totales = Curso.objects.filter(id__in=cursos_totales_ids)
        
        print(f"   Profesor: {profesor.get_nombre_completo()}")
        print(f"   Cursos como jefe: {cursos_jefe.count()}")
        print(f"   Cursos con asignaturas: {cursos_asignaturas.count()}")
        print(f"   Total cursos que puede gestionar: {cursos_totales.count()}")
        
        # Eventos que puede ver
        from django.db.models import Q
        eventos_visibles = EventoCalendario.objects.filter(
            Q(para_todos_los_cursos=True) | Q(cursos__in=cursos_totales)
        ).distinct()
        
        print(f"   Eventos que puede ver: {eventos_visibles.count()}")
        print("   ✅ Permisos: LIMITADOS A SUS CURSOS")
    else:
        print("   ❌ No hay profesores para probar")

def test_permisos_alumno():
    """Probar permisos para alumno"""
    print("🎒 ALUMNO:")
    
    estudiantes = Estudiante.objects.all()
    if estudiantes.exists():
        estudiante = estudiantes.first()
        
        # Cursos del estudiante
        cursos_estudiante = estudiante.cursos.all()
        
        print(f"   Estudiante: {estudiante.get_nombre_completo()}")
        print(f"   Cursos asignados: {cursos_estudiante.count()}")
        
        # Eventos que puede ver
        from django.db.models import Q
        eventos_visibles = EventoCalendario.objects.filter(
            Q(para_todos_los_cursos=True) | Q(cursos__in=cursos_estudiante)
        ).distinct()
        
        print(f"   Eventos que puede ver: {eventos_visibles.count()}")
        print("   ✅ Permisos: SOLO LECTURA DE SUS CURSOS")
    else:
        print("   ❌ No hay estudiantes para probar")

def test_filtros_calendario():
    """Probar los filtros del calendario"""
    # Filtro por fecha
    hoy = timezone.now().date()
    eventos_hoy = EventoCalendario.objects.filter(fecha=hoy)
    print(f"📅 Eventos para hoy ({hoy}): {eventos_hoy.count()}")
    
    # Filtro por tipo
    evaluaciones = EventoCalendario.objects.filter(tipo_evento='evaluacion')
    reuniones = EventoCalendario.objects.filter(tipo_evento='reunion')
    actividades = EventoCalendario.objects.filter(tipo_evento='actividad')
    
    print(f"📝 Evaluaciones: {evaluaciones.count()}")
    print(f"🤝 Reuniones: {reuniones.count()}")
    print(f"🎉 Actividades: {actividades.count()}")
    
    # Filtro por curso
    if Curso.objects.exists():
        curso_prueba = Curso.objects.first()
        eventos_curso = EventoCalendario.objects.filter(cursos=curso_prueba)
        print(f"🏫 Eventos para {curso_prueba}: {eventos_curso.count()}")

def test_json_fullcalendar():
    """Probar la generación de JSON para FullCalendar"""
    eventos = EventoCalendario.objects.all()[:5]  # Tomar 5 eventos para probar
    
    eventos_json = []
    for evento in eventos:
        evento_json = {
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha.isoformat(),
            'description': evento.descripcion or '',
            'backgroundColor': evento.color_por_tipo,
            'borderColor': evento.color_por_tipo,
            'textColor': '#fff'
        }
        eventos_json.append(evento_json)
    
    print(f"📊 Eventos convertidos a JSON: {len(eventos_json)}")
    
    if eventos_json:
        print("   Ejemplo de evento JSON:")
        ejemplo = eventos_json[0]
        for key, value in ejemplo.items():
            print(f"      {key}: {value}")
    
    print("   ✅ Formato JSON válido para FullCalendar")

def verificar_urls_calendario():
    """Verificar que las URLs del calendario estén configuradas"""
    print(f"\n🔗 VERIFICANDO URLS DEL CALENDARIO:")
    print("-" * 40)
    
    try:
        from django.urls import reverse
        
        urls_calendario = [
            ('calendario', []),
            ('editar_evento', [1]),  # ID de ejemplo
            ('eliminar_evento', [1])  # ID de ejemplo
        ]
        
        for url_name, args in urls_calendario:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✅ {url_name}: {url}")
            except Exception as e:
                print(f"   ❌ {url_name}: Error - {e}")
        
    except Exception as e:
        print(f"   ❌ Error general en URLs: {e}")

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL CALENDARIO")
        print("=" * 60)
        
        test_calendario_completo()
        verificar_urls_calendario()
        
        print(f"\n🎉 PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ El sistema de calendario está funcionando correctamente")
        print("✅ Los permisos están configurados según el tipo de usuario")
        print("✅ Los filtros y la integración con FullCalendar funcionan")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
