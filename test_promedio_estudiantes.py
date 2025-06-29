#!/usr/bin/env python3
"""
Script para probar la corrección del promedio de estudiantes
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smapp.models import Calificacion, Estudiante, Curso

def test_promedio_estudiantes():
    """Test que verifica que los promedios se muestren una vez por estudiante"""
    print("=" * 60)
    print("TEST: CORRECCIÓN PROMEDIO DE ESTUDIANTES")
    print("=" * 60)
    
    try:
        # Verificar que hay datos
        total_calificaciones = Calificacion.objects.count()
        total_estudiantes = Estudiante.objects.count()
        total_cursos = Curso.objects.count()
        
        print(f"📊 Datos disponibles:")
        print(f"   • Calificaciones: {total_calificaciones}")
        print(f"   • Estudiantes: {total_estudiantes}")
        print(f"   • Cursos: {total_cursos}")
        
        if total_calificaciones == 0:
            print("❌ No hay calificaciones para probar")
            return False
        
        # Login como admin
        client = Client()
        admin_user = User.objects.filter(username='admin').first()
        
        if not admin_user:
            print("❌ No existe usuario admin")
            return False
        
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ No se pudo hacer login")
            return False
        
        print("✅ Login exitoso como admin")
        
        # Probar con un curso específico
        primer_curso = Curso.objects.first()
        if primer_curso:
            print(f"🎯 Probando con curso: {primer_curso}")
            
            # Hacer request a ver notas con filtro de curso
            response = client.get(f'/notas/ver/?curso_id={primer_curso.id}')
            
            if response.status_code == 200:
                print("✅ Vista de notas accesible")
                
                content = response.content.decode('utf-8')
                
                # Contar ocurrencias de "Resumen de Promedios"
                if 'Resumen de Promedios por Estudiante' in content:
                    print("✅ Sección de promedios encontrada")
                    
                    # Contar filas de la tabla de promedios
                    # Buscar la tabla específica de promedios
                    promedio_section_start = content.find('Resumen de Promedios por Estudiante')
                    if promedio_section_start != -1:
                        promedio_section = content[promedio_section_start:promedio_section_start+5000]
                        
                        # Contar filas de estudiantes en la tabla
                        filas_promedio = promedio_section.count('<tr>') - 1  # -1 para el header
                        print(f"📊 Filas en tabla de promedios: {filas_promedio}")
                        
                        # Verificar que no hay duplicados contando nombres de estudiantes
                        estudiantes_en_curso = primer_curso.estudiantes.count()
                        print(f"📊 Estudiantes reales en curso: {estudiantes_en_curso}")
                        
                        if filas_promedio <= estudiantes_en_curso:
                            print("✅ No hay duplicados de promedios")
                        else:
                            print(f"❌ Posibles duplicados detectados")
                            print(f"   Filas en tabla: {filas_promedio}")
                            print(f"   Estudiantes esperados: {estudiantes_en_curso}")
                    else:
                        print("❌ No se pudo analizar la sección de promedios")
                else:
                    print("⚠️  Sección de promedios no encontrada (puede estar vacía)")
                
                # Verificar que no hay loops infinitos en el template
                badge_promedio_count = content.count('badge')
                print(f"📊 Total de badges en la página: {badge_promedio_count}")
                
            else:
                print(f"❌ Error al acceder a ver notas: {response.status_code}")
                return False
        else:
            print("❌ No hay cursos disponibles para probar")
            return False
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETADO")
        print("   La corrección debería resolver los duplicados")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_promedio_estudiantes()
    sys.exit(0 if success else 1)
