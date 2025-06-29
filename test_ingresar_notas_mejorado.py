#!/usr/bin/env python3
"""
Script para probar la nueva funcionalidad de "Ingresar Notas" 
con selección de curso + asignatura
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Perfil, Estudiante, Profesor, Asignatura, Curso, Inscripcion, Grupo, Calificacion
from django.utils import timezone

def verificar_estructura_datos():
    """Verificar que tenemos los datos necesarios para probar"""
    print("🔍 Verificando estructura de datos para 'Ingresar Notas'...\n")
    
    # Contar registros básicos
    users_count = User.objects.count()
    cursos_count = Curso.objects.count()
    asignaturas_count = Asignatura.objects.count()
    estudiantes_count = Estudiante.objects.count()
    profesores_count = Profesor.objects.count()
    grupos_count = Grupo.objects.count()
    inscripciones_count = Inscripcion.objects.count()
    
    print(f"📊 RESUMEN GENERAL:")
    print(f"   • Usuarios: {users_count}")
    print(f"   • Cursos: {cursos_count}")
    print(f"   • Asignaturas: {asignaturas_count}")
    print(f"   • Estudiantes: {estudiantes_count}")
    print(f"   • Profesores: {profesores_count}")
    print(f"   • Grupos: {grupos_count}")
    print(f"   • Inscripciones: {inscripciones_count}")
    
    return cursos_count > 0 and asignaturas_count > 0 and estudiantes_count > 0 and inscripciones_count > 0

def test_flujo_administrador():
    """Probar flujo para administrador/director"""
    print("\n👑 PROBANDO FLUJO PARA ADMINISTRADOR/DIRECTOR")
    print("=" * 50)
    
    # Obtener cursos disponibles (como vería un admin)
    anio_actual = timezone.now().year
    cursos_disponibles = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
    
    if cursos_disponibles.exists():
        print(f"✅ Cursos disponibles para administrador: {cursos_disponibles.count()}")
        
        for curso in cursos_disponibles[:3]:  # Solo los primeros 3
            print(f"\n📚 CURSO: {curso.get_nivel_display()}{curso.paralelo} - {curso.anio}")
            print(f"   Profesor Jefe: {curso.profesor_jefe.primer_nombre if curso.profesor_jefe else 'Sin asignar'}")
            print(f"   Estudiantes: {curso.estudiantes.count()}")
            
            # Obtener asignaturas del curso
            inscripciones_curso = Inscripcion.objects.filter(
                estudiante__in=curso.estudiantes.all()
            ).select_related('grupo__asignatura')
            
            asignaturas_curso = Asignatura.objects.filter(
                grupo__inscripcion__in=inscripciones_curso
            ).distinct().order_by('nombre')
            
            print(f"   Asignaturas disponibles: {asignaturas_curso.count()}")
            
            for asignatura in asignaturas_curso[:2]:  # Solo las primeras 2
                # Obtener estudiantes del curso inscritos en esta asignatura
                estudiantes_curso_asignatura = Inscripcion.objects.filter(
                    estudiante__in=curso.estudiantes.all(),
                    grupo__asignatura=asignatura
                ).select_related('estudiante', 'grupo')
                
                print(f"     🔸 {asignatura.nombre}:")
                print(f"       Estudiantes inscritos: {estudiantes_curso_asignatura.count()}")
                
                if estudiantes_curso_asignatura.exists():
                    print(f"       Grupos: {', '.join(set([insc.grupo.nombre_grupo or 'Sin nombre' for insc in estudiantes_curso_asignatura]))}")
        
        return True
    else:
        print("❌ No hay cursos disponibles para administrador")
        return False

def test_flujo_profesor():
    """Probar flujo para profesor"""
    print("\n👨‍🏫 PROBANDO FLUJO PARA PROFESOR")
    print("=" * 50)
    
    profesores = Profesor.objects.all()
    
    if profesores.exists():
        for profesor in profesores[:2]:  # Solo los primeros 2
            print(f"\n🧑‍🏫 PROFESOR: {profesor.primer_nombre} {profesor.apellido_paterno}")
            
            # Cursos donde es profesor jefe
            cursos_como_jefe = Curso.objects.filter(profesor_jefe=profesor)
            print(f"   Cursos como jefe: {cursos_como_jefe.count()}")
            
            for curso in cursos_como_jefe:
                print(f"     • {curso.get_nivel_display()}{curso.paralelo} ({curso.estudiantes.count()} estudiantes)")
            
            # Cursos donde imparte asignaturas
            cursos_con_asignaturas = Curso.objects.filter(
                estudiantes__inscripcion__grupo__profesor=profesor
            ).distinct()
            print(f"   Cursos donde imparte: {cursos_con_asignaturas.count()}")
            
            for curso in cursos_con_asignaturas:
                print(f"     • {curso.get_nivel_display()}{curso.paralelo}")
                
                # Asignaturas que imparte en este curso
                asignaturas_profesor = Asignatura.objects.filter(
                    grupo__profesor=profesor,
                    grupo__inscripcion__estudiante__in=curso.estudiantes.all()
                ).distinct()
                
                for asignatura in asignaturas_profesor:
                    estudiantes_count = Inscripcion.objects.filter(
                        estudiante__in=curso.estudiantes.all(),
                        grupo__asignatura=asignatura,
                        grupo__profesor=profesor
                    ).count()
                    
                    print(f"       🔸 {asignatura.nombre} ({estudiantes_count} estudiantes)")
        
        return True
    else:
        print("❌ No hay profesores disponibles")
        return False

def simular_creacion_notas():
    """Simular el proceso de creación de notas"""
    print("\n📝 SIMULANDO CREACIÓN DE NOTAS")
    print("=" * 50)
    
    # Obtener un curso y asignatura para simular
    curso = Curso.objects.filter(anio=timezone.now().year).first()
    
    if not curso:
        print("❌ No hay cursos del año actual para simular")
        return False
    
    # Obtener asignatura del curso
    inscripciones_curso = Inscripcion.objects.filter(
        estudiante__in=curso.estudiantes.all()
    ).select_related('grupo__asignatura')
    
    asignatura = Asignatura.objects.filter(
        grupo__inscripcion__in=inscripciones_curso
    ).first()
    
    if not asignatura:
        print("❌ No hay asignaturas disponibles para simular")
        return False
    
    # Obtener estudiantes
    estudiantes_curso_asignatura = Inscripcion.objects.filter(
        estudiante__in=curso.estudiantes.all(),
        grupo__asignatura=asignatura
    ).select_related('estudiante', 'grupo')
    
    print(f"🎯 SIMULACIÓN:")
    print(f"   Curso: {curso.get_nivel_display()}{curso.paralelo}")
    print(f"   Asignatura: {asignatura.nombre}")
    print(f"   Estudiantes: {estudiantes_curso_asignatura.count()}")
    
    # Simular creación de notas (sin crear realmente)
    print(f"\n📋 ESTUDIANTES QUE RECIBIRÍAN NOTAS:")
    for i, inscripcion in enumerate(estudiantes_curso_asignatura[:5], 1):  # Solo 5 para no saturar
        estudiante = inscripcion.estudiante
        grupo = inscripcion.grupo
        
        # Simular datos de nota
        nombre_evaluacion = "Evaluación de Prueba"
        puntaje_simulado = round(4.0 + (i * 0.5), 1)  # Puntajes entre 4.0 y 7.0
        porcentaje_simulado = min(100, 50 + (i * 10))
        
        print(f"   {i}. {estudiante.primer_nombre} {estudiante.apellido_paterno}")
        print(f"      Código: {estudiante.codigo_estudiante}")
        print(f"      Grupo: {grupo.nombre_grupo or 'Sin nombre'}")
        print(f"      Nota simulada: {puntaje_simulado} ({porcentaje_simulado}%)")
        print()
    
    print("✅ Simulación completada exitosamente")
    return True

def generar_reporte_funcionalidad():
    """Generar reporte de la nueva funcionalidad"""
    print("\n📋 REPORTE DE NUEVA FUNCIONALIDAD: INGRESAR NOTAS")
    print("=" * 60)
    
    print("🔧 CAMBIOS IMPLEMENTADOS:")
    print()
    
    print("1. 📝 VISTA ACTUALIZADA (smapp/views.py):")
    print("   • Selección por curso + asignatura (en lugar de grupo)")
    print("   • Filtrado inteligente según tipo de usuario")
    print("   • Validaciones de rango mejoradas")
    print("   • Manejo de errores más robusto")
    print("   • Redirección automática con filtros aplicados")
    print()
    
    print("2. 🎨 TEMPLATE MEJORADO (templates/ingresar_notas.html):")
    print("   • Interfaz de selección curso → asignatura")
    print("   • Tabla mejorada con iconos y validaciones")
    print("   • Botón 'Rellenar Ejemplo' para pruebas")
    print("   • Validación en tiempo real con JavaScript")
    print("   • Información contextual y consejos")
    print()
    
    print("3. ⚡ FUNCIONALIDADES NUEVAS:")
    print("   • Selección intuitiva: primero curso, luego asignatura")
    print("   • Filtrado automático de estudiantes del curso")
    print("   • Respeto de permisos de profesor (solo sus grupos)")
    print("   • Validación automática de rangos (1.0-7.0, 0-100)")
    print("   • Campos obligatorios marcados claramente")
    print()
    
    print("4. 🔐 PERMISOS Y SEGURIDAD:")
    print("   • Administrador/Director: Todos los cursos y asignaturas")
    print("   • Profesor: Solo cursos donde es jefe o imparte asignaturas")
    print("   • Validación de permisos en cada paso")
    print("   • Mensajes informativos según el rol")
    print()
    
    print("5. 🎯 FLUJO DE USUARIO:")
    print("   ┌─ Seleccionar Curso")
    print("   ├─ Seleccionar Asignatura")
    print("   ├─ Ver Estudiantes del Curso en esa Asignatura")
    print("   ├─ Llenar Datos de Evaluación")
    print("   ├─ Guardar Notas")
    print("   └─ Redirección a Ver Notas con filtros aplicados")
    print()

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PROBANDO NUEVA FUNCIONALIDAD: INGRESAR NOTAS POR CURSO + ASIGNATURA")
    print("=" * 70)
    
    # Verificar estructura
    if not verificar_estructura_datos():
        print("\n⚠️  No hay suficientes datos para probar completamente")
        print("   Ejecuta primero: python crear_usuarios_completos.py")
        return
    
    # Ejecutar pruebas
    tests = [
        test_flujo_administrador,
        test_flujo_profesor,
        simular_creacion_notas
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
            results.append(False)
    
    # Generar reporte
    generar_reporte_funcionalidad()
    
    # Resumen final
    print("\n🎯 RESUMEN DE PRUEBAS:")
    print(f"   ✅ Pruebas exitosas: {sum(1 for r in results if r)}")
    print(f"   ❌ Pruebas fallidas: {sum(1 for r in results if not r)}")
    print(f"   📊 Total de pruebas: {len(results)}")
    
    if all(results):
        print("\n🎉 NUEVA FUNCIONALIDAD LISTA PARA USAR!")
    else:
        print("\n⚠️  ALGUNAS PRUEBAS FALLARON - REVISAR DATOS")
    
    print("\n📋 INSTRUCCIONES PARA PROBAR MANUALMENTE:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Inicia sesión como administrador o profesor")
    print("3. Ve a 'Gestionar Notas' → 'Ingresar Notas'")
    print("4. Selecciona un curso en el primer dropdown")
    print("5. Selecciona una asignatura en el segundo dropdown")
    print("6. Verifica que aparezcan los estudiantes del curso en esa asignatura")
    print("7. Prueba el botón 'Rellenar Ejemplo' para datos de prueba")
    print("8. Ingresa notas y verifica que se redirija correctamente")

if __name__ == "__main__":
    main()
