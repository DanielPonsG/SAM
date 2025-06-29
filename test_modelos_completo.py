import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import *
from django.core.exceptions import ValidationError
from datetime import date, time

def test_modelos():
    print("=== PRUEBAS DE MODELOS DJANGO ===\n")
    
    # 1. Probar métodos de Persona/Estudiante
    print("1. Probando métodos de Estudiante:")
    try:
        estudiante = Estudiante.objects.first()
        if estudiante:
            print(f"   - Nombre completo: {estudiante.get_nombre_completo()}")
            print(f"   - Edad: {estudiante.edad} años")
            print(f"   - Curso actual: {estudiante.get_curso_actual()}")
            print(f"   - String del modelo: {str(estudiante)}")
        else:
            print("   - No hay estudiantes en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 2. Probar métodos de Profesor
    print("\n2. Probando métodos de Profesor:")
    try:
        profesor = Profesor.objects.first()
        if profesor:
            print(f"   - Nombre completo: {profesor.get_nombre_completo()}")
            print(f"   - Especialidad: {profesor.especialidad}")
            print(f"   - Cursos como jefe: {list(profesor.get_cursos_jefatura())}")
            print(f"   - Asignaturas responsable: {list(profesor.get_asignaturas_responsable())}")
        else:
            print("   - No hay profesores en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 3. Probar métodos de Curso
    print("\n3. Probando métodos de Curso:")
    try:
        curso = Curso.objects.first()
        if curso:
            print(f"   - Nombre: {curso.nombre}")
            print(f"   - Nombre completo: {curso.nombre_completo}")
            print(f"   - Total estudiantes: {curso.get_total_estudiantes()}")
            print(f"   - Orden nivel: {curso.orden_nivel}")
            
            # Probar horarios
            horarios = curso.get_horarios_por_dia()
            print(f"   - Total horarios: {horarios.count()}")
            
        else:
            print("   - No hay cursos en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 4. Probar métodos de Asignatura
    print("\n4. Probando métodos de Asignatura:")
    try:
        asignatura = Asignatura.objects.first()
        if asignatura:
            print(f"   - Nombre: {asignatura.nombre}")
            print(f"   - Cursos asignados: {asignatura.get_cursos_asignados().count()}")
            print(f"   - Horarios totales: {asignatura.get_horarios_totales()}")
            print(f"   - Profesor responsable: {asignatura.get_profesor_nombre_completo()}")
        else:
            print("   - No hay asignaturas en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 5. Probar métodos de HorarioCurso
    print("\n5. Probando métodos de HorarioCurso:")
    try:
        horario = HorarioCurso.objects.first()
        if horario:
            print(f"   - String del horario: {str(horario)}")
            print(f"   - Duración en minutos: {horario.duracion_minutos}")
            print(f"   - Asignatura nombre: {horario.asignatura_nombre}")
        else:
            print("   - No hay horarios en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 6. Probar métodos de Perfil
    print("\n6. Probando métodos de Perfil:")
    try:
        perfil = Perfil.objects.first()
        if perfil:
            print(f"   - Es director: {perfil.es_director()}")
            print(f"   - Es profesor: {perfil.es_profesor()}")
            print(f"   - Es alumno: {perfil.es_alumno()}")
            print(f"   - Puede gestionar: {perfil.puede_gestionar()}")
            print(f"   - Perfil detalle: {perfil.get_perfil_detalle()}")
        else:
            print("   - No hay perfiles en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    # 7. Probar EventoCalendario
    print("\n7. Probando métodos de EventoCalendario:")
    try:
        evento = EventoCalendario.objects.first()
        if evento:
            print(f"   - Título: {evento.titulo}")
            print(f"   - Es evaluación: {evento.es_evaluacion}")
            print(f"   - Color por tipo: {evento.color_por_tipo}")
        else:
            print("   - No hay eventos en la base de datos")
    except Exception as e:
        print(f"   - Error: {e}")
    
    print("\n=== PRUEBAS COMPLETADAS ===")
    
    # Estadísticas finales
    print(f"\nEstadísticas del sistema:")
    print(f"- Estudiantes: {Estudiante.objects.count()}")
    print(f"- Profesores: {Profesor.objects.count()}")
    print(f"- Cursos: {Curso.objects.count()}")
    print(f"- Asignaturas: {Asignatura.objects.count()}")
    print(f"- Horarios: {HorarioCurso.objects.count()}")
    print(f"- Eventos: {EventoCalendario.objects.count()}")
    print(f"- Perfiles: {Perfil.objects.count()}")

if __name__ == "__main__":
    test_modelos()
