#!/usr/bin/env python3
"""
Script para asignar profesores a las asignaturas sin profesor
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Profesor, Asignatura
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def asignar_profesores():
    """Asignar profesores a asignaturas que no tienen profesor"""
    logger.info("🔄 Asignando profesores a asignaturas...")
    
    # Obtener asignaturas sin profesor
    asignaturas_sin_profesor = Asignatura.objects.filter(profesor_responsable__isnull=True)
    logger.info(f"📚 Encontradas {asignaturas_sin_profesor.count()} asignaturas sin profesor")
    
    # Obtener profesores disponibles
    profesores = list(Profesor.objects.all())
    if not profesores:
        logger.error("❌ No hay profesores disponibles")
        return
    
    logger.info(f"👨‍🏫 Profesores disponibles: {len(profesores)}")
    
    # Asignar profesores por especialidad/materia
    asignaciones = {
        'MAT001': 'PROF001',  # Matemáticas -> Juan Pérez
        'LEN001': 'PROF002',  # Lenguaje -> María González
        'CIE001': 'PROF003',  # Ciencias -> Carlos Rodríguez
        'HIS001': 'PROF001',  # Historia -> Juan Pérez
        'ART001': 'PROF002',  # Artes -> María González
    }
    
    asignadas = 0
    for asignatura in asignaturas_sin_profesor:
        codigo_profesor = asignaciones.get(asignatura.codigo_asignatura)
        if codigo_profesor:
            try:
                profesor = Profesor.objects.get(codigo_profesor=codigo_profesor)
                asignatura.profesor_responsable = profesor
                asignatura.save()
                logger.info(f"✅ {asignatura.nombre} -> {profesor.primer_nombre} {profesor.apellido_paterno}")
                asignadas += 1
            except Profesor.DoesNotExist:
                logger.warning(f"⚠️ Profesor {codigo_profesor} no encontrado para {asignatura.nombre}")
    
    logger.info(f"✅ Se asignaron {asignadas} profesores a asignaturas")

def main():
    print("=" * 50)
    print("🎯 ASIGNANDO PROFESORES A ASIGNATURAS")
    print("=" * 50)
    
    asignar_profesores()
    
    print("\n" + "=" * 50)
    print("✅ PROCESO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
