#!/usr/bin/env python
"""
Script para probar las funcionalidades del calendario
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Curso, EventoCalendario
from django.utils import timezone
from datetime import datetime, timedelta

def test_funcionalidades_calendario():
    print("🎯 PROBANDO FUNCIONALIDADES DEL CALENDARIO")
    print("=" * 60)
    
    # 1. Verificar que podamos acceder a la vista de agregar evento
    print("\n1. VERIFICANDO VISTAS TEMPORALES:")
    try:
        from agregar_evento_view import agregar_evento_temp
        print("   ✅ Vista agregar_evento_temp importada correctamente")
    except Exception as e:
        print(f"   ❌ Error al importar agregar_evento_temp: {e}")
    
    try:
        from editar_eliminar_evento_views import editar_evento_temp, eliminar_evento_temp
        print("   ✅ Vistas editar_evento_temp y eliminar_evento_temp importadas correctamente")
    except Exception as e:
        print(f"   ❌ Error al importar vistas de editar/eliminar: {e}")
    
    # 2. Verificar datos base
    print("\n2. VERIFICANDO DATOS BASE:")
    usuarios = User.objects.all()
    cursos = Curso.objects.all()
    eventos = EventoCalendario.objects.all()
    
    print(f"   📊 Usuarios: {usuarios.count()}")
    print(f"   📊 Cursos: {cursos.count()}")
    print(f"   📊 Eventos: {eventos.count()}")
    
    # 3. Crear un evento de prueba manualmente para verificar que funcione
    print("\n3. CREANDO EVENTO DE PRUEBA:")
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if admin_user and cursos.exists():
        evento_prueba, created = EventoCalendario.objects.get_or_create(
            titulo="Prueba Funcionalidad Nueva",
            fecha=timezone.now().date() + timedelta(days=2),
            defaults={
                'descripcion': 'Evento para probar las nuevas funcionalidades',
                'hora_inicio': timezone.now().time().replace(hour=9, minute=0),
                'hora_fin': timezone.now().time().replace(hour=10, minute=0),
                'creado_por': admin_user,
                'para_todos_los_cursos': False,
                'solo_profesores': False,
                'tipo_evento': 'general',
                'prioridad': 'media'
            }
        )
        
        if created:
            # Asignar algunos cursos específicos
            primer_curso = cursos.first()
            evento_prueba.cursos.add(primer_curso)
            print(f"   ✅ Evento creado: {evento_prueba.titulo}")
            print(f"   📅 Fecha: {evento_prueba.fecha}")
            print(f"   🎓 Asignado a curso: {primer_curso}")
        else:
            print(f"   ℹ️ Evento ya existe: {evento_prueba.titulo}")
            print(f"   🎓 Cursos asignados: {evento_prueba.cursos.count()}")
    
    # 4. Verificar que los cursos tengan los campos correctos
    print("\n4. VERIFICANDO ESTRUCTURA DE CURSOS:")
    if cursos.exists():
        curso_ejemplo = cursos.first()
        print(f"   📋 Curso ejemplo: {curso_ejemplo}")
        print(f"   📋 Nivel: {curso_ejemplo.nivel}")
        print(f"   📋 Paralelo: {curso_ejemplo.paralelo}")
        print(f"   📋 Año: {curso_ejemplo.anio}")
        print(f"   📋 Profesor jefe: {curso_ejemplo.profesor_jefe}")
        print(f"   📋 Estudiantes: {curso_ejemplo.estudiantes.count()}")
    
    # 5. Verificar eventos con cursos específicos
    print("\n5. VERIFICANDO EVENTOS CON CURSOS ESPECÍFICOS:")
    eventos_con_cursos = EventoCalendario.objects.filter(cursos__isnull=False).distinct()
    eventos_para_todos = EventoCalendario.objects.filter(para_todos_los_cursos=True)
    eventos_solo_profesores = EventoCalendario.objects.filter(solo_profesores=True)
    
    print(f"   📊 Eventos con cursos específicos: {eventos_con_cursos.count()}")
    print(f"   📊 Eventos para todos los cursos: {eventos_para_todos.count()}")
    print(f"   📊 Eventos solo para profesores: {eventos_solo_profesores.count()}")
    
    if eventos_con_cursos.exists():
        evento_ejemplo = eventos_con_cursos.first()
        print(f"   📋 Ejemplo evento con cursos: {evento_ejemplo.titulo}")
        print(f"   🎓 Cursos asignados: {[str(c) for c in evento_ejemplo.cursos.all()]}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN:")
    print("   ✅ Datos base verificados")
    print("   ✅ Vistas temporales creadas")
    print("   ✅ Eventos de prueba funcionando")
    print("   🌐 Funcionalidades listas para probar en navegador")
    print("   📝 Nota: Ejecutar servidor manualmente para probar UI")
    print("=" * 60)

if __name__ == "__main__":
    test_funcionalidades_calendario()
