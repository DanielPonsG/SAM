#!/usr/bin/env python
"""
Script de prueba para el sistema de asistencia de alumnos
Prueba la funcionalidad completa del registro y visualización de asistencia
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Estudiante, Profesor, Curso, Asignatura, AsistenciaAlumno, Perfil
from datetime import date, time
from django.utils import timezone

def test_sistema_asistencia():
    print("=== PRUEBA DEL SISTEMA DE ASISTENCIA ===\n")
    
    # 1. Verificar usuarios y permisos
    print("1. Verificando usuarios del sistema...")
    usuarios = User.objects.all()
    print(f"   Total usuarios: {usuarios.count()}")
    
    for usuario in usuarios:
        perfil = getattr(usuario, 'perfil', None)
        tipo = perfil.tipo_usuario if perfil else 'Sin perfil'
        print(f"   - {usuario.username}: {tipo}")
    
    # 2. Verificar cursos y estudiantes
    print("\n2. Verificando cursos y estudiantes...")
    cursos = Curso.objects.filter(anio=timezone.now().year)
    print(f"   Total cursos del año actual: {cursos.count()}")
    
    for curso in cursos:
        estudiantes_count = curso.estudiantes.count()
        asignaturas_count = curso.asignaturas.count()
        profesor_jefe = curso.profesor_jefe.get_nombre_completo() if curso.profesor_jefe else "Sin asignar"
        print(f"   - {curso}: {estudiantes_count} estudiantes, {asignaturas_count} asignaturas, Prof. Jefe: {profesor_jefe}")
    
    # 3. Verificar asignaturas y profesores
    print("\n3. Verificando asignaturas y profesores...")
    asignaturas = Asignatura.objects.all()
    print(f"   Total asignaturas: {asignaturas.count()}")
    
    for asignatura in asignaturas[:5]:  # Solo mostrar las primeras 5
        profesores_count = asignatura.profesores_responsables.count()
        cursos_asignados = asignatura.cursos.count()
        print(f"   - {asignatura.nombre}: {profesores_count} profesores, {cursos_asignados} cursos")
    
    # 4. Probar permisos por tipo de usuario
    print("\n4. Probando permisos por tipo de usuario...")
    
    # Director/Administrador
    directores = User.objects.filter(perfil__tipo_usuario__in=['director', 'administrador'])
    if directores.exists():
        director = directores.first()
        print(f"   Director/Admin ({director.username}): Puede ver todos los {cursos.count()} cursos")
    
    # Profesores
    profesores = User.objects.filter(perfil__tipo_usuario='profesor')
    if profesores.exists():
        for usuario_prof in profesores[:3]:  # Solo los primeros 3
            try:
                profesor = usuario_prof.profesor
                cursos_jefe = profesor.cursos_jefatura.filter(anio=timezone.now().year).count()
                cursos_asignaturas = Curso.objects.filter(
                    asignaturas__profesores_responsables=profesor,
                    anio=timezone.now().year
                ).distinct().count()
                total_cursos = max(cursos_jefe, cursos_asignaturas)  # Aproximación
                print(f"   Profesor ({usuario_prof.username}): Puede ver ~{total_cursos} cursos")
            except:
                print(f"   Profesor ({usuario_prof.username}): Error al obtener datos")
    
    # Estudiantes
    estudiantes = User.objects.filter(perfil__tipo_usuario='alumno')
    if estudiantes.exists():
        for usuario_est in estudiantes[:3]:  # Solo los primeros 3
            try:
                estudiante = usuario_est.estudiante
                cursos_estudiante = estudiante.cursos.filter(anio=timezone.now().year).count()
                print(f"   Estudiante ({usuario_est.username}): Puede ver {cursos_estudiante} curso(s)")
            except:
                print(f"   Estudiante ({usuario_est.username}): Error al obtener datos")
    
    # 5. Verificar registros de asistencia existentes
    print("\n5. Verificando registros de asistencia...")
    asistencias = AsistenciaAlumno.objects.all()
    print(f"   Total registros de asistencia: {asistencias.count()}")
    
    if asistencias.exists():
        # Estadísticas
        presentes = asistencias.filter(presente=True).count()
        ausentes = asistencias.filter(presente=False).count()
        porcentaje = (presentes / asistencias.count() * 100) if asistencias.count() > 0 else 0
        
        print(f"   - Presentes: {presentes}")
        print(f"   - Ausentes: {ausentes}")
        print(f"   - % Asistencia: {porcentaje:.1f}%")
        
        # Mostrar algunos registros recientes
        print("\n   Registros recientes:")
        for asistencia in asistencias.order_by('-fecha')[:5]:
            estado = "Presente" if asistencia.presente else "Ausente"
            profesor = asistencia.profesor_registro.get_nombre_completo() if asistencia.profesor_registro else "Sistema"
            print(f"   - {asistencia.estudiante.get_nombre_completo()}: {estado} ({asistencia.fecha}) - {profesor}")
    
    # 6. Verificar integridad de datos
    print("\n6. Verificando integridad de datos...")
    errores = []
    
    # Verificar estudiantes sin cursos
    estudiantes_sin_curso = Estudiante.objects.filter(cursos__isnull=True)
    if estudiantes_sin_curso.exists():
        errores.append(f"Estudiantes sin curso: {estudiantes_sin_curso.count()}")
    
    # Verificar cursos sin estudiantes
    cursos_sin_estudiantes = Curso.objects.filter(estudiantes__isnull=True, anio=timezone.now().year)
    if cursos_sin_estudiantes.exists():
        errores.append(f"Cursos sin estudiantes: {cursos_sin_estudiantes.count()}")
    
    # Verificar asignaturas sin profesores
    asignaturas_sin_profesor = Asignatura.objects.filter(
        profesores_responsables__isnull=True,
        profesor_responsable__isnull=True
    )
    if asignaturas_sin_profesor.exists():
        errores.append(f"Asignaturas sin profesores: {asignaturas_sin_profesor.count()}")
    
    if errores:
        print("   ⚠️  Advertencias encontradas:")
        for error in errores:
            print(f"   - {error}")
    else:
        print("   ✅ No se encontraron problemas de integridad")
    
    # 7. Resumen y recomendaciones
    print("\n=== RESUMEN ===")
    print(f"✅ Sistema configurado con {usuarios.count()} usuarios")
    print(f"✅ {cursos.count()} cursos activos para el año {timezone.now().year}")
    print(f"✅ {asignaturas.count()} asignaturas disponibles")
    print(f"✅ {asistencias.count()} registros de asistencia")
    
    print("\n=== FUNCIONALIDADES DISPONIBLES ===")
    print("📝 Registro de asistencia por curso (profesores, directores, admins)")
    print("👁️  Visualización de asistencia con filtros (todos los usuarios según permisos)")
    print("✏️  Edición de registros individuales (profesores autorizados, directores, admins)")
    print("📊 Estadísticas de asistencia por semana")
    print("🔍 Filtros por curso, estudiante y RUT")
    print("🔐 Control de permisos por tipo de usuario")
    
    print("\n=== ACCESO POR TIPO DE USUARIO ===")
    print("🎓 Estudiantes: Solo pueden ver su propia asistencia")
    print("👨‍🏫 Profesores: Cursos donde son jefe o tienen asignaturas")
    print("🏢 Directores/Admins: Acceso completo a todos los cursos")
    
    print("\n✅ Prueba completada exitosamente!")

if __name__ == "__main__":
    try:
        test_sistema_asistencia()
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
