#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Profesor, Curso, Asignatura, HorarioCurso, Perfil
from django.utils import timezone

def crear_datos_prueba():
    print("🔧 CREANDO DATOS DE PRUEBA PARA EL SISTEMA SMA")
    print("=" * 60)
    
    # Crear profesores de ejemplo si no existen
    print("\n👨‍🏫 Creando profesores...")
    profesores_data = [
        {
            'codigo_profesor': 'PROF001',
            'primer_nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'email': 'juan.perez@sma.edu',
            'especialidad': 'Matemáticas'
        },
        {
            'codigo_profesor': 'PROF002',
            'primer_nombre': 'María',
            'apellido_paterno': 'González',
            'email': 'maria.gonzalez@sma.edu',
            'especialidad': 'Lenguaje'
        },
        {
            'codigo_profesor': 'PROF003',
            'primer_nombre': 'Carlos',
            'apellido_paterno': 'Rodríguez',
            'email': 'carlos.rodriguez@sma.edu',
            'especialidad': 'Ciencias'
        }
    ]
    
    profesores_creados = []
    for prof_data in profesores_data:
        try:
            # Verificar si ya existe
            profesor = Profesor.objects.get(codigo_profesor=prof_data['codigo_profesor'])
            print(f"  ✓ Profesor {profesor.primer_nombre} {profesor.apellido_paterno} ya existe")
            profesores_creados.append(profesor)
        except Profesor.DoesNotExist:
            # Crear usuario
            username = f"prof_{prof_data['codigo_profesor'].lower()}"
            try:
                user = User.objects.create_user(
                    username=username,
                    email=prof_data['email'],
                    password='profesor123',
                    first_name=prof_data['primer_nombre'],
                    last_name=prof_data['apellido_paterno']
                )
                
                # Crear perfil
                perfil = Perfil.objects.create(
                    user=user,
                    tipo_usuario='profesor'
                )
                
                # Crear profesor
                profesor = Profesor.objects.create(
                    user=user,
                    codigo_profesor=prof_data['codigo_profesor'],
                    primer_nombre=prof_data['primer_nombre'],
                    apellido_paterno=prof_data['apellido_paterno'],
                    email=prof_data['email'],
                    especialidad=prof_data['especialidad'],
                    numero_documento=f"123456{prof_data['codigo_profesor'][-3:]}",
                    fecha_nacimiento='1980-01-01',
                    genero='M' if prof_data['primer_nombre'] == 'Carlos' else 'F',
                    telefono='+56912345678',
                    direccion='Santiago, Chile'
                )
                
                profesores_creados.append(profesor)
                print(f"  ✓ Creado: {profesor.primer_nombre} {profesor.apellido_paterno}")
                
            except Exception as e:
                print(f"  ❌ Error creando profesor {prof_data['primer_nombre']}: {e}")
    
    # Crear cursos de ejemplo
    print("\n🎓 Creando cursos...")
    cursos_data = [
        {'nivel': '1M', 'paralelo': 'A'},
        {'nivel': '1M', 'paralelo': 'B'},
        {'nivel': '2M', 'paralelo': 'A'},
        {'nivel': '3B', 'paralelo': 'A'},
        {'nivel': '4B', 'paralelo': 'A'},
    ]
    
    cursos_creados = []
    for curso_data in cursos_data:
        try:
            # Verificar si ya existe
            curso = Curso.objects.get(
                nivel=curso_data['nivel'],
                paralelo=curso_data['paralelo'],
                anio=timezone.now().year
            )
            print(f"  ✓ Curso {curso.nombre_completo} ya existe")
            cursos_creados.append(curso)
        except Curso.DoesNotExist:
            try:
                curso = Curso.objects.create(
                    nivel=curso_data['nivel'],
                    paralelo=curso_data['paralelo'],
                    anio=timezone.now().year,
                    profesor_jefe=profesores_creados[0] if profesores_creados else None
                )
                cursos_creados.append(curso)
                print(f"  ✓ Creado: {curso.nombre_completo}")
            except Exception as e:
                print(f"  ❌ Error creando curso {curso_data}: {e}")
    
    # Crear asignaturas de ejemplo
    print("\n📚 Creando asignaturas...")
    asignaturas_data = [
        {
            'codigo_asignatura': 'MAT001',
            'nombre': 'Matemáticas I',
            'descripcion': 'Álgebra y aritmética básica',
            'profesor_responsable': profesores_creados[0] if profesores_creados else None
        },
        {
            'codigo_asignatura': 'LEN001',
            'nombre': 'Lenguaje y Comunicación',
            'descripcion': 'Comprensión lectora y expresión escrita',
            'profesor_responsable': profesores_creados[1] if len(profesores_creados) > 1 else None
        },
        {
            'codigo_asignatura': 'CIE001',
            'nombre': 'Ciencias Naturales',
            'descripcion': 'Biología, Física y Química básica',
            'profesor_responsable': profesores_creados[2] if len(profesores_creados) > 2 else None
        },
        {
            'codigo_asignatura': 'HIS001',
            'nombre': 'Historia y Geografía',
            'descripcion': 'Historia universal y geografía',
            'profesor_responsable': None
        }
    ]
    
    asignaturas_creadas = []
    for asig_data in asignaturas_data:
        try:
            # Verificar si ya existe
            asignatura = Asignatura.objects.get(codigo_asignatura=asig_data['codigo_asignatura'])
            print(f"  ✓ Asignatura {asignatura.nombre} ya existe")
            asignaturas_creadas.append(asignatura)
        except Asignatura.DoesNotExist:
            try:
                asignatura = Asignatura.objects.create(
                    codigo_asignatura=asig_data['codigo_asignatura'],
                    nombre=asig_data['nombre'],
                    descripcion=asig_data['descripcion'],
                    profesor_responsable=asig_data['profesor_responsable']
                )
                
                # Asociar con algunos cursos
                if cursos_creados:
                    asignatura.cursos.set(cursos_creados[:2])  # Asociar con los primeros 2 cursos
                
                asignaturas_creadas.append(asignatura)
                print(f"  ✓ Creada: {asignatura.nombre}")
            except Exception as e:
                print(f"  ❌ Error creando asignatura {asig_data['nombre']}: {e}")
    
    print("\n" + "="*60)
    print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
    print(f"👨‍🏫 Profesores: {len(profesores_creados)}")
    print(f"🎓 Cursos: {len(cursos_creados)}")
    print(f"📚 Asignaturas: {len(asignaturas_creadas)}")
    
    print("\n🔗 ENLACES ÚTILES:")
    print("   📊 Lista de Asignaturas: http://127.0.0.1:8000/asignaturas/")
    print("   👨‍🏫 Lista de Profesores: http://127.0.0.1:8000/profesores/")
    print("   🎓 Lista de Cursos: http://127.0.0.1:8000/cursos/")
    print("   📅 Calendario: http://127.0.0.1:8000/calendario/")

if __name__ == '__main__':
    crear_datos_prueba()
