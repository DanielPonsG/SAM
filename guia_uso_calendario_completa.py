#!/usr/bin/env python3
"""
🎯 GUÍA COMPLETA DE USO DEL CALENDARIO
=====================================

Este script muestra todas las funcionalidades implementadas en el calendario
y cómo usarlas correctamente según el tipo de usuario.

FUNCIONALIDADES PRINCIPALES:
✅ Crear eventos para todos los cursos
✅ Crear eventos solo para profesores
✅ Crear eventos para cursos específicos
✅ Validación de horas (hora inicio < hora fin)
✅ Validación de campos obligatorios
✅ Filtrado de eventos por permisos de usuario
✅ Interfaz visual moderna con FullCalendar
✅ Modal interactivo para creación de eventos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import EventoCalendario, Curso, Profesor, Estudiante
from datetime import datetime, date, timedelta

def mostrar_guia_uso():
    """Muestra la guía completa de uso del calendario"""
    
    print("🎯 SISTEMA DE CALENDARIO ESCOLAR - GUÍA COMPLETA")
    print("=" * 60)
    print()
    
    print("📋 TIPOS DE USUARIOS Y PERMISOS:")
    print("-" * 40)
    print("👤 ADMINISTRADOR/DIRECTOR:")
    print("   • ✅ Ver todos los eventos")
    print("   • ✅ Crear eventos para cualquier audiencia")
    print("   • ✅ Editar/eliminar cualquier evento")
    print("   • ✅ Filtrar por curso")
    print()
    
    print("👨‍🏫 PROFESOR:")
    print("   • ✅ Ver eventos de sus cursos asignados")
    print("   • ✅ Ver eventos generales")
    print("   • ✅ Ver eventos solo para profesores")
    print("   • ✅ Crear eventos para sus cursos")
    print("   • ❌ No ve eventos de otros cursos")
    print()
    
    print("👨‍🎓 ESTUDIANTE:")
    print("   • ✅ Ver eventos de sus cursos")
    print("   • ✅ Ver eventos generales")
    print("   • ❌ No crear eventos")
    print("   • ❌ No ver eventos solo para profesores")
    print()
    
    print("🎨 FUNCIONALIDADES DE LA INTERFAZ:")
    print("-" * 40)
    print("📅 CALENDARIO PRINCIPAL:")
    print("   • Vista mensual, semanal y diaria")
    print("   • Eventos con colores según tipo")
    print("   • Click en fecha para crear evento")
    print("   • Hover en eventos para detalles")
    print()
    
    print("➕ CREAR EVENTOS:")
    print("   • Modal interactivo con validación")
    print("   • Campos: título*, fecha*, horas, tipo, prioridad, descripción")
    print("   • Tres opciones de audiencia:")
    print("     - 🌍 Todos los cursos")
    print("     - 👨‍🏫 Solo profesores")
    print("     - 🎯 Cursos específicos (selección múltiple)")
    print()
    
    print("✅ VALIDACIONES IMPLEMENTADAS:")
    print("   • Título obligatorio")
    print("   • Fecha obligatoria")
    print("   • Hora inicio < hora fin")
    print("   • Al menos un curso si selecciona 'específicos'")
    print("   • Permisos de usuario")
    print()
    
    print("🎨 TIPOS DE EVENTOS Y COLORES:")
    print("-" * 40)
    
    # Obtener tipos de eventos del modelo
    tipos_eventos = EventoCalendario.TIPO_EVENTO_CHOICES
    for codigo, nombre in tipos_eventos:
        evento_temp = EventoCalendario(tipo_evento=codigo)
        color = evento_temp.color_por_tipo
        print(f"   • {nombre}: {color}")
    
    print()
    
    print("🚀 CÓMO USAR EL SISTEMA:")
    print("-" * 40)
    print("1. 📝 ACCEDER AL CALENDARIO:")
    print("   - Ir a: http://127.0.0.1:8000/calendario/")
    print("   - Iniciar sesión con credenciales válidas")
    print()
    
    print("2. 👀 VISUALIZAR EVENTOS:")
    print("   - El calendario muestra eventos según tus permisos")
    print("   - Usar filtros por fecha y curso (admin/director)")
    print("   - Cambiar vista: mes/semana/día")
    print()
    
    print("3. ➕ CREAR EVENTO:")
    print("   - Click en 'Nuevo Evento' o en una fecha")
    print("   - Completar formulario modal")
    print("   - Seleccionar audiencia adecuada")
    print("   - Validar que las horas sean correctas")
    print("   - Click en 'Crear Evento'")
    print()
    
    print("4. ✏️ EDITAR/ELIMINAR:")
    print("   - Click en evento en la lista")
    print("   - Usar botones de acción")
    print("   - Solo usuarios con permisos")
    print()
    
    print("💡 CONSEJOS DE USO:")
    print("-" * 40)
    print("• 🎯 Usa 'Todos los cursos' para eventos generales")
    print("• 👨‍🏫 Usa 'Solo profesores' para reuniones/capacitaciones")
    print("• 🎯 Usa 'Cursos específicos' para evaluaciones/actividades")
    print("• ⏰ Incluye horas para mejor organización")
    print("• 📝 Usa descripciones claras y detalladas")
    print("• 🏷️ Selecciona el tipo de evento correcto")
    print("• 🚨 Usa prioridad 'alta' para eventos importantes")
    print()
    
    print("🔧 ACCESOS DIRECTOS:")
    print("-" * 40)
    print("• Calendario principal: /calendario/")
    print("• Crear evento: /calendario/ (modal)")
    print("• Agregar evento: /agregar_evento/ (página completa)")
    print()
    
    # Mostrar estadísticas actuales
    eventos_count = EventoCalendario.objects.count()
    eventos_futuros = EventoCalendario.objects.filter(fecha__gte=date.today()).count()
    eventos_todos = EventoCalendario.objects.filter(para_todos_los_cursos=True).count()
    eventos_profesores = EventoCalendario.objects.filter(solo_profesores=True).count()
    eventos_especificos = EventoCalendario.objects.filter(para_todos_los_cursos=False, solo_profesores=False).count()
    
    print("📊 ESTADÍSTICAS ACTUALES:")
    print("-" * 40)
    print(f"• Total de eventos: {eventos_count}")
    print(f"• Eventos futuros: {eventos_futuros}")
    print(f"• Eventos para todos: {eventos_todos}")
    print(f"• Solo profesores: {eventos_profesores}")
    print(f"• Cursos específicos: {eventos_especificos}")
    print()
    
    print("🎉 ¡EL CALENDARIO ESTÁ LISTO PARA USAR!")
    print("=" * 60)
    print()
    print("Para probar en el navegador:")
    print("1. Ir a: http://127.0.0.1:8000/login/")
    print("2. Usuario: admin | Contraseña: admin123")
    print("3. Navegar a: http://127.0.0.1:8000/calendario/")
    print("4. ¡Crear y gestionar eventos! 🚀")

def mostrar_ejemplos_eventos():
    """Muestra ejemplos de eventos que se pueden crear"""
    
    print("\n📝 EJEMPLOS DE EVENTOS POR TIPO:")
    print("=" * 50)
    
    ejemplos = [
        {
            'tipo': 'Todos los cursos',
            'icono': '🌍',
            'ejemplos': [
                'Inicio del año escolar',
                'Simulacro de evacuación',
                'Día del estudiante',
                'Reunión general de apoderados',
                'Vacunación escolar',
                'Feria del libro'
            ]
        },
        {
            'tipo': 'Solo profesores',
            'icono': '👨‍🏫',
            'ejemplos': [
                'Consejo de profesores',
                'Capacitación docente',
                'Reunión de coordinación',
                'Evaluación institucional',
                'Planificación curricular',
                'Jornada pedagógica'
            ]
        },
        {
            'tipo': 'Cursos específicos',
            'icono': '🎯',
            'ejemplos': [
                'Prueba de matemáticas (1° Básico A)',
                'Laboratorio de ciencias (8° Básico)',
                'Taller de arte (3° y 4° Básico)',
                'Evaluación de historia (2° Medio)',
                'Excursión pedagógica (6° Básico)',
                'Ensayo PSU (4° Medio)'
            ]
        }
    ]
    
    for categoria in ejemplos:
        print(f"\n{categoria['icono']} {categoria['tipo'].upper()}:")
        print("-" * 30)
        for i, ejemplo in enumerate(categoria['ejemplos'], 1):
            print(f"   {i}. {ejemplo}")
    
    print("\n" + "=" * 50)
    print("💡 TIP: Estos son solo ejemplos. ¡Crea los eventos que necesites!")

if __name__ == "__main__":
    mostrar_guia_uso()
    mostrar_ejemplos_eventos()
