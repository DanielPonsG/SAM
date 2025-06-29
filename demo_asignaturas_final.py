#!/usr/bin/env python
"""
Script final para demostrar y validar la funcionalidad completa de gestión de asignaturas
"""
import os
import sys
import django
from datetime import datetime, time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Asignatura, Profesor, Curso, HorarioCurso
from django.db import transaction

def crear_datos_demo():
    """Crear datos de demostración para asignaturas"""
    
    print("🔧 CREANDO DATOS DE DEMOSTRACIÓN PARA ASIGNATURAS")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            
            # 1. Crear asignaturas básicas si no existen
            asignaturas_demo = [
                {
                    'nombre': 'Matemáticas',
                    'codigo_asignatura': 'MAT-01',
                    'descripcion': 'Asignatura de matemáticas básicas y aplicadas'
                },
                {
                    'nombre': 'Lenguaje y Comunicación',
                    'codigo_asignatura': 'LEN-01',
                    'descripcion': 'Desarrollo de habilidades de comunicación oral y escrita'
                },
                {
                    'nombre': 'Ciencias Naturales',
                    'codigo_asignatura': 'CNA-01',
                    'descripcion': 'Estudio de física, química y biología'
                },
                {
                    'nombre': 'Historia y Geografía',
                    'codigo_asignatura': 'HIS-01',
                    'descripcion': 'Historia universal y de Chile, geografía'
                },
                {
                    'nombre': 'Educación Física',
                    'codigo_asignatura': 'EDF-01',
                    'descripcion': 'Desarrollo físico y deportivo'
                }
            ]
            
            print("\n📚 Creando asignaturas de demostración...")
            asignaturas_creadas = []
            
            for asig_data in asignaturas_demo:
                asignatura, created = Asignatura.objects.get_or_create(
                    codigo_asignatura=asig_data['codigo_asignatura'],
                    defaults={
                        'nombre': asig_data['nombre'],
                        'descripcion': asig_data['descripcion']
                    }
                )
                
                if created:
                    print(f"   ✅ Creada: {asignatura.nombre} ({asignatura.codigo_asignatura})")
                else:
                    print(f"   📋 Ya existe: {asignatura.nombre} ({asignatura.codigo_asignatura})")
                
                asignaturas_creadas.append(asignatura)
            
            # 2. Asignar profesores a las asignaturas
            print("\n👨‍🏫 Asignando profesores a asignaturas...")
            profesores = list(Profesor.objects.all())
            
            if profesores:
                for i, asignatura in enumerate(asignaturas_creadas):
                    if not asignatura.profesor_responsable:
                        profesor = profesores[i % len(profesores)]
                        asignatura.profesor_responsable = profesor
                        asignatura.save()
                        print(f"   ✅ {asignatura.nombre} asignada a {profesor.primer_nombre} {profesor.apellido_paterno}")
                    else:
                        print(f"   📋 {asignatura.nombre} ya tiene profesor: {asignatura.profesor_responsable}")
            else:
                print("   ⚠️  No hay profesores disponibles")
            
            # 3. Crear algunos horarios de ejemplo
            print("\n⏰ Creando horarios de ejemplo...")
            cursos = list(Curso.objects.all()[:3])  # Tomar solo los primeros 3 cursos
            
            if cursos and asignaturas_creadas:
                horarios_ejemplo = [
                    {
                        'asignatura': asignaturas_creadas[0],  # Matemáticas
                        'curso': cursos[0],
                        'dia': 'LU',
                        'hora_inicio': time(8, 0),
                        'hora_fin': time(9, 30)
                    },
                    {
                        'asignatura': asignaturas_creadas[1],  # Lenguaje
                        'curso': cursos[0],
                        'dia': 'MA',
                        'hora_inicio': time(8, 0),
                        'hora_fin': time(9, 30)
                    },
                    {
                        'asignatura': asignaturas_creadas[0],  # Matemáticas
                        'curso': cursos[1],
                        'dia': 'LU',
                        'hora_inicio': time(10, 0),
                        'hora_fin': time(11, 30)
                    }
                ]
                
                for horario_data in horarios_ejemplo:
                    horario, created = HorarioCurso.objects.get_or_create(
                        curso=horario_data['curso'],
                        asignatura=horario_data['asignatura'],
                        dia=horario_data['dia'],
                        hora_inicio=horario_data['hora_inicio'],
                        defaults={
                            'hora_fin': horario_data['hora_fin']
                        }
                    )
                    
                    if created:
                        print(f"   ✅ Horario creado: {horario.asignatura.nombre} - {horario.curso.nombre_completo} - {horario.get_dia_display()} {horario.hora_inicio}")
                    else:
                        print(f"   📋 Horario ya existe: {horario.asignatura.nombre} - {horario.curso.nombre_completo} - {horario.get_dia_display()}")
            
            print("\n" + "=" * 60)
            print("✅ DATOS DE DEMOSTRACIÓN CREADOS EXITOSAMENTE")
            print("=" * 60)
            
        return True
        
    except Exception as e:
        print(f"❌ Error al crear datos de demostración: {str(e)}")
        return False

def mostrar_resumen_sistema():
    """Mostrar un resumen del estado actual del sistema"""
    
    print("\n📊 RESUMEN DEL SISTEMA DE GESTIÓN DE ASIGNATURAS")
    print("=" * 60)
    
    # Asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"\n📚 ASIGNATURAS ({asignaturas.count()}):")
    for asignatura in asignaturas:
        profesor = asignatura.profesor_responsable
        horarios_count = HorarioCurso.objects.filter(asignatura=asignatura).count()
        
        print(f"   • {asignatura.codigo_asignatura} - {asignatura.nombre}")
        print(f"     Profesor: {profesor.primer_nombre + ' ' + profesor.apellido_paterno if profesor else 'Sin asignar'}")
        print(f"     Horarios: {horarios_count}")
        print()
    
    # Profesores
    profesores = Profesor.objects.all()
    print(f"👨‍🏫 PROFESORES ({profesores.count()}):")
    for profesor in profesores:
        asignaturas_responsable = Asignatura.objects.filter(profesor_responsable=profesor)
        print(f"   • {profesor.primer_nombre} {profesor.apellido_paterno}")
        print(f"     Especialidad: {profesor.especialidad}")
        print(f"     Asignaturas: {asignaturas_responsable.count()}")
        for asig in asignaturas_responsable:
            print(f"       - {asig.nombre}")
        print()
    
    # Cursos
    cursos = Curso.objects.all()
    print(f"🎓 CURSOS ({cursos.count()}):")
    for curso in cursos[:5]:  # Mostrar solo los primeros 5
        horarios_count = HorarioCurso.objects.filter(curso=curso).count()
        print(f"   • {curso.nombre_completo} - Horarios: {horarios_count}")
    
    if cursos.count() > 5:
        print(f"   ... y {cursos.count() - 5} cursos más")
    
    # Estadísticas
    print(f"\n📈 ESTADÍSTICAS:")
    asignaturas_con_profesor = Asignatura.objects.filter(profesor_responsable__isnull=False).count()
    asignaturas_sin_profesor = asignaturas.count() - asignaturas_con_profesor
    total_horarios = HorarioCurso.objects.count()
    
    print(f"   • Asignaturas con profesor: {asignaturas_con_profesor}")
    print(f"   • Asignaturas sin profesor: {asignaturas_sin_profesor}")
    print(f"   • Total de horarios programados: {total_horarios}")
    
    print("\n" + "=" * 60)
    print("🌐 ENLACES IMPORTANTES:")
    print("   • Listar asignaturas: http://127.0.0.1:8000/asignaturas/")
    print("   • Agregar asignatura: http://127.0.0.1:8000/asignaturas/agregar/")
    print("   • Panel admin: http://127.0.0.1:8000/admin/")
    print("=" * 60)

def main():
    """Función principal"""
    
    print("🎯 SISTEMA DE GESTIÓN DE ASIGNATURAS - VALIDACIÓN FINAL")
    print("=" * 60)
    
    # Verificar usuarios
    admin_users = User.objects.filter(is_superuser=True)
    if not admin_users.exists():
        print("❌ No hay usuarios administradores en el sistema")
        print("   Ejecuta: python manage.py createsuperuser")
        return False
    
    print(f"✅ Usuarios administradores: {admin_users.count()}")
    
    # Crear datos de demostración
    if crear_datos_demo():
        # Mostrar resumen
        mostrar_resumen_sistema()
        
        print("\n🚀 EL SISTEMA ESTÁ LISTO PARA USAR")
        print("\nInstrucciones:")
        print("1. Ve a http://127.0.0.1:8000/login/ e inicia sesión como admin")
        print("2. Navega a http://127.0.0.1:8000/asignaturas/ para gestionar asignaturas")
        print("3. Puedes crear, editar, eliminar asignaturas y asignar profesores")
        print("4. Los horarios se pueden gestionar desde cada asignatura")
        
        return True
    else:
        print("❌ Error al configurar datos de demostración")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        sys.exit(1)
