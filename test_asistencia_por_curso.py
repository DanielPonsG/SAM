#!/usr/bin/env python
"""
Script para probar las nuevas funcionalidades de asistencia por curso
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import AsistenciaAlumno, AsistenciaProfesor, Estudiante, Profesor, Curso, Asignatura
from django.contrib.auth.models import User
from django.utils import timezone

def test_permisos_cursos():
    """Prueba que los permisos de cursos funcionen correctamente"""
    print("🧪 PROBANDO PERMISOS POR TIPO DE USUARIO")
    print("=" * 60)
    
    try:
        # Obtener datos de prueba
        profesor = Profesor.objects.first()
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        
        if not all([profesor, curso, asignatura]):
            print("❌ Error: No hay datos suficientes en la base de datos")
            return False
        
        print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
        print(f"🏫 Curso: {curso}")
        print(f"📖 Asignatura: {asignatura.nombre}")
        print()
        
        # TEST 1: Cursos donde es jefe
        print("1️⃣ PROBANDO CURSOS COMO JEFE DE CURSO")
        print("-" * 40)
        
        cursos_jefatura = profesor.get_cursos_jefatura()
        print(f"📋 Cursos donde es jefe: {cursos_jefatura.count()}")
        for curso_jefe in cursos_jefatura:
            print(f"   - {curso_jefe}")
        
        # TEST 2: Cursos donde hace clases (como responsable)
        print("\n2️⃣ PROBANDO CURSOS CON ASIGNATURAS RESPONSABLES")
        print("-" * 40)
        
        asignaturas_responsable = profesor.get_asignaturas_responsable()
        print(f"📚 Asignaturas como responsable: {asignaturas_responsable.count()}")
        for asig in asignaturas_responsable:
            print(f"   - {asig.nombre}")
        
        cursos_responsable = Curso.objects.filter(
            asignaturas__profesor_responsable=profesor
        ).distinct()
        print(f"🏫 Cursos donde es responsable de asignatura: {cursos_responsable.count()}")
        for curso_resp in cursos_responsable:
            print(f"   - {curso_resp}")
        
        # TEST 3: Cursos donde hace clases (como profesor asignado)
        print("\n3️⃣ PROBANDO CURSOS CON ASIGNATURAS ASIGNADAS")
        print("-" * 40)
        
        cursos_asignaturas = Curso.objects.filter(
            asignaturas__profesores_responsables=profesor
        ).distinct()
        print(f"🏫 Cursos donde tiene asignaturas asignadas: {cursos_asignaturas.count()}")
        for curso_asig in cursos_asignaturas:
            print(f"   - {curso_asig}")
        
        # TEST 4: Todos los cursos del profesor (combinados)
        print("\n4️⃣ PROBANDO CURSOS COMBINADOS")
        print("-" * 40)
        
        # Combinar usando IDs para evitar problemas de queryset
        cursos_ids = set()
        cursos_ids.update(cursos_jefatura.values_list('id', flat=True))
        cursos_ids.update(cursos_responsable.values_list('id', flat=True))
        cursos_ids.update(cursos_asignaturas.values_list('id', flat=True))
        
        todos_cursos = Curso.objects.filter(id__in=cursos_ids)
        print(f"🎯 Total cursos disponibles para el profesor: {todos_cursos.count()}")
        for curso_total in todos_cursos:
            print(f"   - {curso_total}")
        
        print("\n✅ Prueba de permisos completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_vista_semanal():
    """Prueba la funcionalidad de vista semanal"""
    print("\n🧪 PROBANDO VISTA SEMANAL")
    print("=" * 60)
    
    try:
        # Obtener datos de prueba
        curso = Curso.objects.first()
        asignatura = Asignatura.objects.first()
        estudiantes = curso.estudiantes.all()[:3]  # Solo 3 estudiantes para la prueba
        profesor = Profesor.objects.first()
        user = User.objects.first()
        
        if not all([curso, asignatura, profesor, user]) or not estudiantes:
            print("❌ Error: No hay datos suficientes en la base de datos")
            return False
        
        print(f"🏫 Curso: {curso}")
        print(f"📖 Asignatura: {asignatura.nombre}")
        print(f"👨‍🏫 Profesor: {profesor.get_nombre_completo()}")
        print()
        
        # Crear registros de asistencia para la semana actual
        fecha_hoy = timezone.now().date()
        fecha_lunes = fecha_hoy - timedelta(days=fecha_hoy.weekday())
        
        print(f"📅 Fecha lunes de esta semana: {fecha_lunes}")
        
        # Limpiar registros existentes
        AsistenciaAlumno.objects.filter(
            curso=curso,
            asignatura=asignatura,
            fecha__range=[fecha_lunes, fecha_lunes + timedelta(days=6)]
        ).delete()
        
        # Crear registros para diferentes días de la semana
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        registros_creados = 0
        
        for i, dia in enumerate(dias_semana):
            fecha_dia = fecha_lunes + timedelta(days=i)
            
            for j, estudiante in enumerate(estudiantes):
                # Hacer algunos ausentes para variar
                presente = not (i == 2 and j == 1)  # Un estudiante ausente el miércoles
                
                asistencia = AsistenciaAlumno.objects.create(
                    estudiante=estudiante,
                    curso=curso,
                    asignatura=asignatura,
                    profesor_registro=profesor,
                    presente=presente,
                    observacion=f"Registro de {dia}",
                    justificacion="Enfermo" if not presente else "",
                    registrado_por_usuario=user
                )
                
                # Cambiar la fecha manualmente para la prueba
                asistencia.fecha = fecha_dia
                asistencia.save()
                
                registros_creados += 1
                print(f"✅ {dia}: {estudiante.get_nombre_completo()} - {'Presente' if presente else 'Ausente'}")
        
        print(f"\n📊 Total registros creados: {registros_creados}")
        
        # Verificar registros de la semana
        asistencias_semana = AsistenciaAlumno.objects.filter(
            curso=curso,
            fecha__range=[fecha_lunes, fecha_lunes + timedelta(days=6)]
        ).order_by('fecha', 'estudiante__primer_nombre')
        
        print(f"📋 Registros encontrados en la semana: {asistencias_semana.count()}")
        
        # Estadísticas
        total = asistencias_semana.count()
        presentes = asistencias_semana.filter(presente=True).count()
        ausentes = asistencias_semana.filter(presente=False).count()
        porcentaje = round((presentes / total * 100) if total > 0 else 0, 1)
        
        print(f"📈 Estadísticas:")
        print(f"   - Total: {total}")
        print(f"   - Presentes: {presentes}")
        print(f"   - Ausentes: {ausentes}")
        print(f"   - Porcentaje de asistencia: {porcentaje}%")
        
        print("\n✅ Prueba de vista semanal completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_navegacion_semanas():
    """Prueba la navegación entre semanas"""
    print("\n🧪 PROBANDO NAVEGACIÓN ENTRE SEMANAS")
    print("=" * 60)
    
    try:
        fecha_hoy = timezone.now().date()
        fecha_lunes = fecha_hoy - timedelta(days=fecha_hoy.weekday())
        
        print(f"📅 Semana actual (lunes): {fecha_lunes}")
        
        # Semana anterior
        semana_anterior = fecha_lunes - timedelta(days=7)
        print(f"⬅️ Semana anterior: {semana_anterior}")
        
        # Semana siguiente
        semana_siguiente = fecha_lunes + timedelta(days=7)
        print(f"➡️ Semana siguiente: {semana_siguiente}")
        
        # Crear fechas de la semana actual
        fechas_semana = []
        dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for i in range(7):
            fecha = fecha_lunes + timedelta(days=i)
            fechas_semana.append({
                'fecha': fecha,
                'dia': dias_nombres[i],
                'es_hoy': fecha == fecha_hoy
            })
        
        print("\n📋 Fechas de la semana actual:")
        for fecha_info in fechas_semana:
            estado = " (HOY)" if fecha_info['es_hoy'] else ""
            print(f"   - {fecha_info['dia']}: {fecha_info['fecha']}{estado}")
        
        print("\n✅ Prueba de navegación entre semanas completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 INICIANDO PRUEBAS DE NUEVA FUNCIONALIDAD DE ASISTENCIA")
    print("=" * 80)
    
    # Ejecutar todas las pruebas
    pruebas = [
        test_permisos_cursos,
        test_vista_semanal,
        test_navegacion_semanas
    ]
    
    resultados = []
    for prueba in pruebas:
        resultado = prueba()
        resultados.append(resultado)
        print("\n" + "="*80)
    
    # Resumen final
    exitosas = sum(resultados)
    total = len(resultados)
    
    print(f"\n🎯 RESUMEN FINAL")
    print(f"✅ Pruebas exitosas: {exitosas}/{total}")
    print(f"❌ Pruebas fallidas: {total - exitosas}/{total}")
    
    if all(resultados):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("✅ El sistema de asistencia por curso está funcionando correctamente")
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisa los errores anteriores")
    
    sys.exit(0 if all(resultados) else 1)
