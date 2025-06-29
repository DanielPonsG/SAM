#!/usr/bin/env python3
"""
Script simplificado para probar que se ha solucionado el error de template VariableDoesNotExist
relacionado con [observacion] en registrar_asistencia_alumno.html
"""

import os
import sys
import django
from django.template import Template, Context
from django.template.loader import get_template
from django.template.context_processors import request
from django.http import HttpRequest

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Estudiante, Profesor, AsistenciaAlumno, Asignatura
from django.utils import timezone

def test_template_syntax():
    """Prueba que el template no tenga errores de sintaxis"""
    print("🧪 INICIANDO PRUEBA DE CORRECCIÓN DE SINTAXIS DE TEMPLATE")
    print("=" * 60)
    
    try:
        # 1. Cargar el template
        template = get_template('registrar_asistencia_alumno.html')
        print("✅ Template cargado exitosamente")
        
        # 2. Crear datos de contexto simulados
        curso = Curso.objects.first()
        if not curso:
            print("⚠️  No hay cursos, creando datos simulados...")
            # Crear contexto básico sin datos reales
            context = {
                'form': None,
                'mostrar_lista': False,
                'messages': [],
            }
        else:
            # Simular contexto cuando se muestra la lista de estudiantes
            estudiantes = curso.estudiantes.all()[:3]
            asistencias_existentes = {}
            
            # Simular algunas asistencias existentes para probar el acceso a observacion
            if estudiantes:
                for i, estudiante in enumerate(estudiantes):
                    if i % 2 == 0:  # Solo algunos estudiantes con asistencias previas
                        # Crear objeto simulado de asistencia
                        class AsistenciaSimulada:
                            def __init__(self):
                                self.presente = True
                                self.observacion = f"Observación {i+1}"
                                self.justificacion = f"Justificación {i+1}"
                                self.hora_registro = timezone.now()
                        
                        asistencias_existentes[estudiante.id] = AsistenciaSimulada()
            
            asignatura = Asignatura.objects.first()
            
            context = {
                'form': None,
                'mostrar_lista': True,
                'curso_seleccionado': curso,
                'asignatura_seleccionada': asignatura,
                'fecha_seleccionada': timezone.now().date(),
                'hora_seleccionada': timezone.now().time(),
                'profesor_actual': Profesor.objects.first(),
                'estudiantes': estudiantes,
                'asistencias_existentes': asistencias_existentes,
                'messages': [],
            }
        
        print("✅ Contexto de prueba creado")
        
        # 3. Intentar renderizar el template
        try:
            rendered = template.render(context)
            print("✅ Template renderizado exitosamente")
            
            # 4. Verificar que no hay errores específicos en el contenido
            if 'VariableDoesNotExist' in rendered:
                print("❌ ERROR: Todavía hay errores VariableDoesNotExist")
                return False
                
            if 'Failed lookup for key [observacion]' in rendered:
                print("❌ ERROR: El error específico de [observacion] sigue presente")
                return False
                
            print("✅ No se encontraron errores VariableDoesNotExist en el template")
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ Error renderizando template: {error_str}")
            
            if 'VariableDoesNotExist' in error_str or 'observacion' in error_str:
                print("❌ ERROR ESPECÍFICO: El error de template [observacion] sigue presente")
                return False
            
            return False
        
        print("\n" + "=" * 60)
        print("🎉 PRUEBA DE CORRECCIÓN DE TEMPLATE COMPLETADA EXITOSAMENTE")
        print("✅ El template registrar_asistencia_alumno.html no tiene errores de sintaxis")
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return False

def main():
    """Función principal"""
    try:
        success = test_template_syntax()
        if success:
            print("\n🎯 RESULTADO: Template corregido exitosamente")
            return 0
        else:
            print("\n❌ RESULTADO: Aún hay errores en el template")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
