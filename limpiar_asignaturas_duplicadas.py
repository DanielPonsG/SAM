#!/usr/bin/env python
"""
Script para limpiar y corregir asignaturas duplicadas y mejorar la coherencia de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sma.settings')
django.setup()

from smapp.models import Curso, Asignatura, Profesor
from django.utils import timezone

def main():
    print("=== LIMPIEZA Y CORRECCIÓN DE ASIGNATURAS DUPLICADAS ===")
    print()
    
    anio_actual = timezone.now().year
    
    # Identificar asignaturas duplicadas por nombre
    print("🔍 Identificando asignaturas duplicadas...")
    print("-" * 50)
    
    asignaturas_por_nombre = {}
    for asignatura in Asignatura.objects.all():
        nombre_normalizado = asignatura.nombre.strip().lower()
        if nombre_normalizado not in asignaturas_por_nombre:
            asignaturas_por_nombre[nombre_normalizado] = []
        asignaturas_por_nombre[nombre_normalizado].append(asignatura)
    
    duplicadas = {nombre: asignaturas for nombre, asignaturas in asignaturas_por_nombre.items() if len(asignaturas) > 1}
    
    if not duplicadas:
        print("✅ No se encontraron asignaturas duplicadas por nombre")
    else:
        print(f"⚠️  Se encontraron {len(duplicadas)} grupos de asignaturas duplicadas:")
        
        for nombre, asignaturas_grupo in duplicadas.items():
            print(f"\n📖 Asignatura: {nombre.title()}")
            print(f"   Duplicados encontrados: {len(asignaturas_grupo)}")
            
            # Decidir cuál mantener y cuáles consolidar
            # Preferir la que tenga más cursos asignados, luego la que tenga profesor
            asignatura_principal = None
            asignaturas_a_eliminar = []
            
            for asignatura in asignaturas_grupo:
                cursos_count = asignatura.cursos.filter(anio=anio_actual).count()
                tiene_profesor = asignatura.profesor_responsable is not None
                
                print(f"   - {asignatura.codigo_asignatura}: {cursos_count} cursos, {'CON' if tiene_profesor else 'SIN'} profesor")
                
                if asignatura_principal is None:
                    asignatura_principal = asignatura
                else:
                    # Comparar para ver cuál es mejor candidato para ser principal
                    cursos_principal = asignatura_principal.cursos.filter(anio=anio_actual).count()
                    tiene_profesor_principal = asignatura_principal.profesor_responsable is not None
                    
                    # La principal debería ser la que tenga más cursos o profesor
                    if (cursos_count > cursos_principal or 
                        (cursos_count == cursos_principal and tiene_profesor and not tiene_profesor_principal)):
                        asignaturas_a_eliminar.append(asignatura_principal)
                        asignatura_principal = asignatura
                    else:
                        asignaturas_a_eliminar.append(asignatura)
            
            print(f"   ✅ Mantener: {asignatura_principal.codigo_asignatura}")
            print(f"   ❌ Consolidar: {[a.codigo_asignatura for a in asignaturas_a_eliminar]}")
            
            # Consolidar datos
            print(f"   🔄 Consolidando datos...")
            
            for asignatura_duplicada in asignaturas_a_eliminar:
                # Transferir cursos
                cursos_duplicados = asignatura_duplicada.cursos.all()
                for curso in cursos_duplicados:
                    # Solo agregar si no está ya asignada
                    if not asignatura_principal.cursos.filter(id=curso.id).exists():
                        asignatura_principal.cursos.add(curso)
                        print(f"      - Curso {curso} transferido")
                
                # Si la asignatura principal no tiene profesor pero la duplicada sí
                if not asignatura_principal.profesor_responsable and asignatura_duplicada.profesor_responsable:
                    asignatura_principal.profesor_responsable = asignatura_duplicada.profesor_responsable
                    asignatura_principal.save()
                    print(f"      - Profesor {asignatura_duplicada.profesor_responsable} transferido")
                
                # Si la asignatura principal no tiene descripción pero la duplicada sí
                if not asignatura_principal.descripcion and asignatura_duplicada.descripcion:
                    asignatura_principal.descripcion = asignatura_duplicada.descripcion
                    asignatura_principal.save()
                    print(f"      - Descripción transferida")
            
            # Eliminar las asignaturas duplicadas
            for asignatura_duplicada in asignaturas_a_eliminar:
                print(f"      - Eliminando {asignatura_duplicada.codigo_asignatura}")
                asignatura_duplicada.delete()
            
            print(f"   ✅ Consolidación completada")
    
    print()
    print("🧹 LIMPIEZA ADICIONAL:")
    print("-" * 30)
    
    # Eliminar asignaturas sin cursos ni profesor (posibles huérfanas)
    asignaturas_huerfanas = Asignatura.objects.filter(
        cursos__isnull=True,
        profesor_responsable__isnull=True
    ).exclude(descripcion__isnull=False)  # Mantener si tienen descripción
    
    if asignaturas_huerfanas.exists():
        print(f"⚠️  Encontradas {asignaturas_huerfanas.count()} asignaturas huérfanas (sin cursos ni profesor):")
        for asignatura in asignaturas_huerfanas:
            print(f"   - {asignatura.nombre} ({asignatura.codigo_asignatura})")
        
        respuesta = input("\n¿Deseas eliminar estas asignaturas huérfanas? (s/N): ").lower().strip()
        if respuesta == 's':
            count = asignaturas_huerfanas.count()
            asignaturas_huerfanas.delete()
            print(f"✅ Eliminadas {count} asignaturas huérfanas")
        else:
            print("⏭️  Asignaturas huérfanas conservadas")
    else:
        print("✅ No se encontraron asignaturas huérfanas")
    
    print()
    print("📊 ESTADÍSTICAS FINALES:")
    print("-" * 30)
    
    # Recalcular estadísticas después de la limpieza
    asignaturas_finales = Asignatura.objects.all()
    total_asignaturas = asignaturas_finales.count()
    asignaturas_con_profesor = asignaturas_finales.filter(profesor_responsable__isnull=False).count()
    asignaturas_con_cursos = asignaturas_finales.filter(cursos__anio=anio_actual).distinct().count()
    asignaturas_sin_cursos = total_asignaturas - asignaturas_con_cursos
    
    print(f"📖 Total asignaturas: {total_asignaturas}")
    print(f"👨‍🏫 Con profesor: {asignaturas_con_profesor}")
    print(f"📚 Asignadas a cursos ({anio_actual}): {asignaturas_con_cursos}")
    print(f"⚠️  Sin cursos: {asignaturas_sin_cursos}")
    
    # Estadísticas de cursos
    cursos = Curso.objects.filter(anio=anio_actual)
    total_asignaciones = sum(curso.asignaturas.count() for curso in cursos)
    
    print(f"🔄 Total asignaciones curso-asignatura: {total_asignaciones}")
    
    print()
    print("✅ LIMPIEZA COMPLETADA - Los datos ahora deberían ser coherentes")
    print("   Recomendación: Revisar las vistas web para confirmar la coherencia")

if __name__ == '__main__':
    main()
