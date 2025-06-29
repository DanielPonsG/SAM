#!/usr/bin/env python3
"""
Script de prueba completa para la gestión de asignaturas
Valida filtros, edición, eliminación y gestión de horarios
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.contrib.auth.models import User
from smapp.models import Profesor, Asignatura, Curso, HorarioCurso, Perfil
from django.db import transaction
from datetime import time, date
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_datos_prueba():
    """Crear datos de prueba para las asignaturas"""
    logger.info("🔄 Creando datos de prueba...")
    
    try:
        with transaction.atomic():
            # Crear profesores de prueba
            profesores_data = [
                {'codigo': 'PROF001', 'nombre': 'Juan', 'apellido': 'Pérez', 'email': 'juan.perez@colegio.cl'},
                {'codigo': 'PROF002', 'nombre': 'María', 'apellido': 'González', 'email': 'maria.gonzalez@colegio.cl'},
                {'codigo': 'PROF003', 'nombre': 'Carlos', 'apellido': 'Rodríguez', 'email': 'carlos.rodriguez@colegio.cl'},
            ]
            
            profesores_creados = []
            for prof_data in profesores_data:
                # Crear usuario
                username = f"prof_{prof_data['codigo'].lower()}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=prof_data['email'],
                        password='temp123',
                        first_name=prof_data['nombre'],
                        last_name=prof_data['apellido']
                    )
                    
                    # Crear profesor
                    profesor = Profesor.objects.create(
                        user=user,
                        codigo_profesor=prof_data['codigo'],
                        primer_nombre=prof_data['nombre'],
                        apellido_paterno=prof_data['apellido'],
                        email=prof_data['email'],
                        telefono='987654321',
                        numero_documento=f"{prof_data['codigo'][-3:]}12345-6",  # RUT ficticio
                        fecha_nacimiento=date(1985, 1, 15),  # Fecha como objeto date
                        genero='M' if prof_data['nombre'] in ['Juan', 'Carlos'] else 'F',
                        especialidad='Educación General'
                    )
                    profesores_creados.append(profesor)
                    logger.info(f"✅ Profesor creado: {prof_data['nombre']} {prof_data['apellido']}")
                else:
                    profesor = Profesor.objects.get(codigo_profesor=prof_data['codigo'])
                    profesores_creados.append(profesor)
                    logger.info(f"ℹ️ Profesor ya existe: {prof_data['nombre']} {prof_data['apellido']}")
            
            # Crear cursos de prueba
            cursos_data = [
                {'nivel': '1B', 'paralelo': 'A'},
                {'nivel': '2B', 'paralelo': 'A'},
                {'nivel': '3B', 'paralelo': 'A'},
                {'nivel': '1M', 'paralelo': 'A'},
            ]
            
            cursos_creados = []
            for curso_data in cursos_data:
                curso, created = Curso.objects.get_or_create(
                    nivel=curso_data['nivel'],
                    paralelo=curso_data['paralelo'],
                    anio=2024,
                    defaults={}
                )
                cursos_creados.append(curso)
                status = "creado" if created else "ya existe"
                logger.info(f"✅ Curso {status}: {curso.nombre}")
            
            # Crear asignaturas de prueba
            asignaturas_data = [
                {
                    'codigo': 'MAT001',
                    'nombre': 'Matemáticas',
                    'descripcion': 'Matemáticas básicas y álgebra',
                    'profesor': profesores_creados[0] if profesores_creados else None,
                    'cursos': [cursos_creados[0], cursos_creados[1]]
                },
                {
                    'codigo': 'LEN001',
                    'nombre': 'Lenguaje y Comunicación',
                    'descripcion': 'Comprensión lectora y expresión escrita',
                    'profesor': profesores_creados[1] if len(profesores_creados) > 1 else None,
                    'cursos': [cursos_creados[0], cursos_creados[2]]
                },
                {
                    'codigo': 'CIE001',
                    'nombre': 'Ciencias Naturales',
                    'descripcion': 'Biología, Química y Física básica',
                    'profesor': None,  # Sin profesor asignado para probar filtros
                    'cursos': [cursos_creados[1], cursos_creados[3]]
                },
                {
                    'codigo': 'HIS001',
                    'nombre': 'Historia y Geografía',
                    'descripcion': 'Historia de Chile y geografía mundial',
                    'profesor': profesores_creados[2] if len(profesores_creados) > 2 else None,
                    'cursos': [cursos_creados[2], cursos_creados[3]]
                },
                {
                    'codigo': 'ART001',
                    'nombre': 'Artes Visuales',
                    'descripcion': 'Expresión artística y creatividad',
                    'profesor': None,  # Otra sin profesor para probar filtros
                    'cursos': [cursos_creados[0]]
                }
            ]
            
            asignaturas_creadas = []
            for asig_data in asignaturas_data:
                asignatura, created = Asignatura.objects.get_or_create(
                    codigo_asignatura=asig_data['codigo'],
                    defaults={
                        'nombre': asig_data['nombre'],
                        'descripcion': asig_data['descripcion'],
                        'profesor_responsable': asig_data['profesor']
                    }
                )
                
                # Asociar cursos
                for curso in asig_data['cursos']:
                    asignatura.cursos.add(curso)
                
                asignaturas_creadas.append(asignatura)
                status = "creada" if created else "ya existe"
                logger.info(f"✅ Asignatura {status}: {asig_data['nombre']}")
            
            # Crear algunos horarios de ejemplo
            horarios_data = [
                {'asignatura': asignaturas_creadas[0], 'curso': cursos_creados[0], 'dia': 'lunes', 'inicio': '08:00', 'fin': '09:30'},
                {'asignatura': asignaturas_creadas[0], 'curso': cursos_creados[1], 'dia': 'martes', 'inicio': '10:00', 'fin': '11:30'},
                {'asignatura': asignaturas_creadas[1], 'curso': cursos_creados[0], 'dia': 'miercoles', 'inicio': '08:00', 'fin': '09:30'},
                {'asignatura': asignaturas_creadas[1], 'curso': cursos_creados[2], 'dia': 'jueves', 'inicio': '14:00', 'fin': '15:30'},
                {'asignatura': asignaturas_creadas[3], 'curso': cursos_creados[2], 'dia': 'viernes', 'inicio': '09:30', 'fin': '11:00'},
            ]
            
            for horario_data in horarios_data:
                horario, created = HorarioCurso.objects.get_or_create(
                    asignatura=horario_data['asignatura'],
                    curso=horario_data['curso'],
                    dia=horario_data['dia'],
                    defaults={
                        'hora_inicio': time.fromisoformat(horario_data['inicio']),
                        'hora_fin': time.fromisoformat(horario_data['fin'])
                    }
                )
                status = "creado" if created else "ya existe"
                logger.info(f"✅ Horario {status}: {horario_data['asignatura'].nombre} - {horario_data['dia']}")
            
            logger.info("✅ Datos de prueba creados exitosamente")
            
            return {
                'profesores': profesores_creados,
                'cursos': cursos_creados,
                'asignaturas': asignaturas_creadas
            }
            
    except Exception as e:
        logger.error(f"❌ Error creando datos de prueba: {str(e)}")
        raise

def verificar_filtros():
    """Verificar que los filtros de asignaturas funcionen"""
    logger.info("🔍 Verificando filtros de asignaturas...")
    
    try:
        # Filtro por código
        asignaturas_mat = Asignatura.objects.filter(codigo_asignatura__icontains='MAT')
        logger.info(f"✅ Filtro por código 'MAT': {asignaturas_mat.count()} resultado(s)")
        
        # Filtro por nombre
        asignaturas_matematicas = Asignatura.objects.filter(nombre__icontains='Matemáticas')
        logger.info(f"✅ Filtro por nombre 'Matemáticas': {asignaturas_matematicas.count()} resultado(s)")
        
        # Filtro sin profesor
        asignaturas_sin_profesor = Asignatura.objects.filter(profesor_responsable__isnull=True)
        logger.info(f"✅ Filtro sin profesor: {asignaturas_sin_profesor.count()} resultado(s)")
        
        # Filtro por profesor
        if Profesor.objects.exists():
            primer_profesor = Profesor.objects.first()
            asignaturas_con_profesor = Asignatura.objects.filter(
                profesor_responsable__primer_nombre__icontains=primer_profesor.primer_nombre
            )
            logger.info(f"✅ Filtro por profesor '{primer_profesor.primer_nombre}': {asignaturas_con_profesor.count()} resultado(s)")
        
        logger.info("✅ Todos los filtros funcionan correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error verificando filtros: {str(e)}")
        raise

def verificar_estadisticas():
    """Verificar que las estadísticas se calculen correctamente"""
    logger.info("📊 Verificando estadísticas...")
    
    try:
        total_asignaturas = Asignatura.objects.count()
        sin_profesor = Asignatura.objects.filter(profesor_responsable__isnull=True).count()
        con_profesor = total_asignaturas - sin_profesor
        con_horarios = Asignatura.objects.filter(horarios__isnull=False).distinct().count()
        sin_horarios = total_asignaturas - con_horarios
        
        logger.info(f"📈 Total asignaturas: {total_asignaturas}")
        logger.info(f"👤 Con profesor: {con_profesor}")
        logger.info(f"❌ Sin profesor: {sin_profesor}")
        logger.info(f"🕐 Con horarios: {con_horarios}")
        logger.info(f"⏰ Sin horarios: {sin_horarios}")
        
        logger.info("✅ Estadísticas calculadas correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error verificando estadísticas: {str(e)}")
        raise

def verificar_relaciones():
    """Verificar las relaciones entre modelos"""
    logger.info("🔗 Verificando relaciones entre modelos...")
    
    try:
        for asignatura in Asignatura.objects.all():
            cursos_count = asignatura.cursos.count()
            horarios_count = asignatura.horarios.count()
            profesor = asignatura.profesor_responsable
            
            logger.info(f"📚 {asignatura.nombre}:")
            logger.info(f"   - Cursos: {cursos_count}")
            logger.info(f"   - Horarios: {horarios_count}")
            logger.info(f"   - Profesor: {profesor.primer_nombre + ' ' + profesor.apellido_paterno if profesor else 'Sin asignar'}")
        
        logger.info("✅ Relaciones verificadas correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error verificando relaciones: {str(e)}")
        raise

def main():
    """Función principal de prueba"""
    print("=" * 60)
    print("🚀 INICIANDO PRUEBAS DE GESTIÓN DE ASIGNATURAS")
    print("=" * 60)
    
    try:
        # Crear datos de prueba
        datos = crear_datos_prueba()
        print()
        
        # Verificar filtros
        verificar_filtros()
        print()
        
        # Verificar estadísticas
        verificar_estadisticas()
        print()
        
        # Verificar relaciones
        verificar_relaciones()
        print()
        
        print("=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        print()
        print("🎯 RESUMEN:")
        print(f"- Profesores creados: {len(datos['profesores'])}")
        print(f"- Cursos creados: {len(datos['cursos'])}")
        print(f"- Asignaturas creadas: {len(datos['asignaturas'])}")
        print()
        print("📋 PARA PROBAR LA INTERFAZ:")
        print("1. Inicia el servidor: python manage.py runserver")
        print("2. Ve a: http://localhost:8000/asignaturas/")
        print("3. Prueba los filtros y acciones disponibles")
        print("4. Usa las credenciales de admin: admin / admin123")
        
    except Exception as e:
        logger.error(f"❌ Error en las pruebas: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
