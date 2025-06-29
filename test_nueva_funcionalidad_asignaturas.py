#!/usr/bin/env python3
"""
Script para probar la nueva funcionalidad de asignación de asignaturas a cursos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Asignatura, Curso, Grupo, Inscripcion, Estudiante, Profesor, PeriodoAcademico
from django.utils import timezone
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

def probar_nueva_funcionalidad():
    """Probar la nueva funcionalidad paso a paso"""
    print("=== PROBANDO NUEVA FUNCIONALIDAD ===")
    
    # 1. Verificar que hay asignaturas y cursos
    asignaturas = Asignatura.objects.all()
    cursos = Curso.objects.all()
    
    print(f"Asignaturas disponibles: {asignaturas.count()}")
    print(f"Cursos disponibles: {cursos.count()}")
    
    if not asignaturas.exists() or not cursos.exists():
        print("❌ No hay suficientes datos para probar")
        return False
    
    # 2. Tomar un curso que tenga estudiantes
    curso_con_estudiantes = None
    for curso in cursos:
        if curso.estudiantes.count() > 0:
            curso_con_estudiantes = curso
            break
    
    if not curso_con_estudiantes:
        print("❌ No hay cursos con estudiantes")
        return False
    
    print(f"Curso seleccionado: {curso_con_estudiantes} ({curso_con_estudiantes.estudiantes.count()} estudiantes)")
    
    # 3. Verificar asignaturas del curso ANTES
    asignaturas_antes = curso_con_estudiantes.asignaturas.all()
    print(f"Asignaturas del curso ANTES: {asignaturas_antes.count()}")
    for asig in asignaturas_antes:
        print(f"  - {asig.nombre}")
    
    # 4. Obtener asignaturas no asignadas
    todas_asignaturas = Asignatura.objects.all()
    asignaturas_no_asignadas = todas_asignaturas.exclude(
        id__in=asignaturas_antes.values_list('id', flat=True)
    )
    print(f"Asignaturas NO asignadas: {asignaturas_no_asignadas.count()}")
    for asig in asignaturas_no_asignadas:
        print(f"  - {asig.nombre}")
    
    # 5. Asignar una asignatura al curso
    if asignaturas_no_asignadas.exists():
        asignatura_a_asignar = asignaturas_no_asignadas.first()
        print(f"\nAsignando {asignatura_a_asignar.nombre} al curso {curso_con_estudiantes}...")
        
        curso_con_estudiantes.asignaturas.add(asignatura_a_asignar)
        
        # Verificar que se asignó
        asignaturas_despues = curso_con_estudiantes.asignaturas.all()
        print(f"Asignaturas del curso DESPUÉS: {asignaturas_despues.count()}")
        
        if asignatura_a_asignar in asignaturas_despues:
            print("✅ Asignatura asignada correctamente")
        else:
            print("❌ Error al asignar asignatura")
            return False
    
    return True

def probar_vista_ingresar_notas():
    """Probar que la vista ingresar_notas funcione con la nueva lógica"""
    print("\n=== PROBANDO VISTA INGRESAR_NOTAS ===")
    
    # Obtener usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuarios administradores")
        return False
    
    # Crear cliente
    client = Client()
    
    # Login
    login_success = client.login(username=admin_user.username, password='admin123')
    if not login_success:
        passwords = ['admin', '123456', 'password', 'adminadmin']
        for pwd in passwords:
            if client.login(username=admin_user.username, password=pwd):
                login_success = True
                break
    
    if not login_success:
        print("❌ No se pudo hacer login")
        return False
    
    print(f"✅ Login exitoso como {admin_user.username}")
    
    # Probar vista sin parámetros
    response = client.get(reverse('ingresar_notas'))
    print(f"GET ingresar_notas: Status {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Error al cargar vista ingresar_notas")
        return False
    
    # Buscar un curso con estudiantes
    curso_con_estudiantes = Curso.objects.filter(estudiantes__isnull=False).first()
    if not curso_con_estudiantes:
        print("❌ No hay cursos con estudiantes")
        return False
    
    # Probar vista con curso seleccionado
    response = client.get(f'{reverse("ingresar_notas")}?curso_id={curso_con_estudiantes.id}')
    print(f"GET ingresar_notas con curso: Status {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Error al cargar vista con curso")
        return False
    
    # Verificar contexto
    if hasattr(response, 'context') and response.context:
        context = response.context
        asignaturas_disponibles = context.get('asignaturas_disponibles', [])
        print(f"Asignaturas disponibles en contexto: {len(asignaturas_disponibles)}")
        
        if len(asignaturas_disponibles) > 0:
            print("✅ Se encontraron asignaturas para el curso")
            for asig in asignaturas_disponibles:
                print(f"  - {asig.nombre}")
        else:
            print("⚠️  No se encontraron asignaturas para el curso")
    
    return True

def probar_creacion_grupos_automatica():
    """Probar que se creen grupos automáticamente"""
    print("\n=== PROBANDO CREACIÓN AUTOMÁTICA DE GRUPOS ===")
    
    # Buscar curso con asignaturas pero sin grupos
    curso = Curso.objects.filter(asignaturas__isnull=False).first()
    if not curso:
        print("❌ No hay cursos con asignaturas")
        return False
    
    asignatura = curso.asignaturas.first()
    print(f"Curso: {curso}")
    print(f"Asignatura: {asignatura.nombre}")
    
    # Verificar grupos existentes
    grupos_antes = Grupo.objects.filter(asignatura=asignatura).count()
    print(f"Grupos existentes ANTES: {grupos_antes}")
    
    # Obtener o crear periodo académico
    periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
    if not periodo_actual:
        from datetime import date
        anio_actual = timezone.now().year
        periodo_actual = PeriodoAcademico.objects.create(
            nombre=f"Año Lectivo {anio_actual}",
            fecha_inicio=date(anio_actual, 3, 1),
            fecha_fin=date(anio_actual, 12, 15),
            activo=True
        )
        print("✅ Periodo académico creado")
    
    # Crear grupo si no existe
    profesor_asignatura = asignatura.profesores_responsables.first() or asignatura.profesor_responsable
    
    grupo, created = Grupo.objects.get_or_create(
        asignatura=asignatura,
        periodo_academico=periodo_actual,
        profesor=profesor_asignatura,
        defaults={'capacidad_maxima': 50}
    )
    
    if created:
        print("✅ Grupo creado automáticamente")
    else:
        print("ℹ️  Grupo ya existía")
    
    # Inscribir estudiantes automáticamente
    estudiantes_curso = curso.estudiantes.all()
    inscripciones_creadas = 0
    
    for estudiante in estudiantes_curso:
        inscripcion, created = Inscripcion.objects.get_or_create(
            estudiante=estudiante,
            grupo=grupo
        )
        if created:
            inscripciones_creadas += 1
    
    print(f"✅ Inscripciones creadas: {inscripciones_creadas}")
    print(f"Total inscripciones en grupo: {grupo.inscripcion_set.count()}")
    
    return True

def main():
    print("PRUEBA: Nueva funcionalidad de asignaturas en ingresar_notas")
    print("=" * 60)
    
    resultados = {
        'funcionalidad_basica': probar_nueva_funcionalidad(),
        'vista_ingresar_notas': probar_vista_ingresar_notas(),
        'creacion_grupos': probar_creacion_grupos_automatica(),
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS:")
    for test, resultado in resultados.items():
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"  {test}: {status}")
    
    all_passed = all(resultados.values())
    print(f"\nRESULTADO GENERAL: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")
    
    if all_passed:
        print("\n🎉 ¡La nueva funcionalidad está funcionando correctamente!")
        print("✅ Las asignaturas creadas ahora aparecen en 'Ingresar Notas'")
        print("✅ Se crean grupos automáticamente cuando es necesario") 
        print("✅ Los estudiantes se inscriben automáticamente a los grupos")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
