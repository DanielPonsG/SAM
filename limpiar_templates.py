#!/usr/bin/env python3
"""
Script para limpiar templates innecesarios del proyecto SMA.
Este script identifica y elimina templates duplicados, obsoletos o no utilizados,
manteniendo solo los que están realmente referenciados en las vistas.
"""

import os
import shutil
from datetime import datetime

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
BACKUP_DIR = os.path.join(BASE_DIR, 'templates_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))

# Templates que están siendo utilizados por las vistas según views.py
TEMPLATES_EN_USO = {
    'index_master.html',      # Template base principal
    'index.html',             # Vista index
    'agregar.html',           # Vista agregar
    'modificar.html',         # Vista modificar  
    'eliminar.html',          # Vista eliminar
    'listar_estudiantes.html', # Vista listar_estudiantes
    'listar_profesores.html', # Vista listar_profesores
    'gestionar_profesor.html', # Vista gestionar_profesor
    'calendario.html',        # Vista calendario principal
    'inicio.html',            # Vista inicio
    'login.html',             # Vista login
    'mis_horarios.html',      # Vista mis_horarios
    'mi_curso.html',          # Vista mi_curso
    'listar_cursos.html',     # Vista listar_cursos
    'listar_asignaturas.html', # Vista listar_asignaturas (principal funcional)
    'ingresar_notas.html',    # Vista ingresar_notas
    'ver_notas_curso.html',   # Vista ver_notas_curso
    'registrar_asistencia_alumno.html', # Vista registrar_asistencia_alumno
    'ver_asistencia_alumno.html', # Vista ver_asistencia_alumno
    'registrar_asistencia_profesor.html', # Vista registrar_asistencia_profesor
    'ver_asistencia_profesor.html', # Vista ver_asistencia_profesor
    'editar_evento.html',     # Vista editar_evento
    'eliminar_evento.html',   # Vista eliminar_evento
    'error_permisos.html',    # Vista error_permisos
    'agregar_curso.html',     # Vista agregar_curso
    'editar_curso.html',      # Vista editar_curso
    'eliminar_curso.html',    # Vista eliminar_curso
    'gestionar_horarios.html', # Vista gestionar_horarios
    'agregar_asignatura.html', # Vista agregar_asignatura
    'eliminar_asignatura.html', # Vista eliminar_asignatura
    'ver_horario_curso.html', # Vista ver_horario_curso
    'agregar_asignatura_completa.html', # Vista agregar_asignatura_completa
    'editar_nota.html',       # Vista editar_nota
    'eliminar_nota.html',     # Vista eliminar_nota
    'editar_asistencia_alumno.html', # Vista editar_asistencia_alumno
    'editar_asistencia_profesores.html', # Vista editar_asistencia_profesor
    'agregar_horario.html',   # Vista agregar_horario (función pero sin template específico)
    'editar_horario.html',    # Vista editar_horario
    'eliminar_horario.html',  # Vista eliminar_horario
    'gestionar_horarios_asignatura.html', # Vista gestionar_horarios_asignatura
    'editar_asignatura.html', # Vista editar_asignatura
}

# Templates que son duplicados, obsoletos o innecesarios
TEMPLATES_A_ELIMINAR = {
    # Duplicados de calendario
    'calendario_backup.html',
    'calendario_backup_old.html', 
    'calendario_funcional.html',
    'calendario_nuevo.html',
    'calendario_real.html',
    'calendario_real_completo.html',
    
    # Duplicados de agregar
    'agregar_nuevo.html',
    'agregar_curso_nuevo.html',
    'agregar_curso_test.html',
    
    # Duplicados de listar estudiantes
    'listar_estudiantes_clean.html',
    'listar_estudiantes_fixed.html',
    'listar_estudiantes_mejorado.html',
    'listar_estudiantes_new.html',
    
    # Templates de backup/fixed
    'modificar_fixed.html',
    
    # Templates de debug/prueba
    'debug_info.html',
    
    # Templates sin uso específico detectado
    'editar_asistencia_profesor.html',  # La vista usa 'editar_asistencia_profesores.html'
}

# Templates standalone (HTML independientes en root)
TEMPLATES_STANDALONE_A_ELIMINAR = {
    'calendario_debug.html',
    'debug_calendario_completo.html', 
    'debug_calendario_html.html',
}

def crear_backup():
    """Crear un backup de todos los templates antes de eliminar"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    print(f"📦 Creando backup en: {BACKUP_DIR}")
    
    # Copiar todos los templates
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            src = os.path.join(TEMPLATES_DIR, filename)
            dst = os.path.join(BACKUP_DIR, filename)
            shutil.copy2(src, dst)
    
    # Copiar templates standalone del directorio raíz
    for filename in TEMPLATES_STANDALONE_A_ELIMINAR:
        src = os.path.join(BASE_DIR, filename)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, f"standalone_{filename}")
            shutil.copy2(src, dst)
    
    print(f"✅ Backup creado exitosamente")

def analizar_templates():
    """Analizar y mostrar qué templates se van a conservar y eliminar"""
    templates_existentes = set()
    
    # Escanear templates en directorio templates/
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            templates_existentes.add(filename)
    
    # Agregar templates standalone
    for filename in TEMPLATES_STANDALONE_A_ELIMINAR:
        if os.path.exists(os.path.join(BASE_DIR, filename)):
            templates_existentes.add(f"standalone_{filename}")
    
    templates_a_conservar = templates_existentes & TEMPLATES_EN_USO
    templates_a_eliminar_confirmados = templates_existentes & TEMPLATES_A_ELIMINAR
    templates_standalone_confirmados = set()
    
    for filename in TEMPLATES_STANDALONE_A_ELIMINAR:
        if os.path.exists(os.path.join(BASE_DIR, filename)):
            templates_standalone_confirmados.add(filename)
    
    print("📊 ANÁLISIS DE TEMPLATES")
    print("=" * 50)
    print(f"📁 Total de templates encontrados: {len(templates_existentes)}")
    print(f"✅ Templates a conservar (en uso): {len(templates_a_conservar)}")
    print(f"🗑️  Templates a eliminar (duplicados/obsoletos): {len(templates_a_eliminar_confirmados)}")
    print(f"🗑️  Templates standalone a eliminar: {len(templates_standalone_confirmados)}")
    
    print("\n🔍 DETALLES:")
    print("\n✅ TEMPLATES A CONSERVAR:")
    for template in sorted(templates_a_conservar):
        print(f"   • {template}")
    
    print("\n🗑️  TEMPLATES A ELIMINAR (duplicados/obsoletos):")
    for template in sorted(templates_a_eliminar_confirmados):
        print(f"   • {template}")
    
    print("\n🗑️  TEMPLATES STANDALONE A ELIMINAR:")
    for template in sorted(templates_standalone_confirmados):
        print(f"   • {template} (archivo independiente)")
    
    return templates_a_eliminar_confirmados, templates_standalone_confirmados

def eliminar_templates(templates_a_eliminar, templates_standalone):
    """Eliminar los templates identificados"""
    eliminados = 0
    
    # Eliminar templates del directorio templates/
    for template in templates_a_eliminar:
        file_path = os.path.join(TEMPLATES_DIR, template)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Eliminado: templates/{template}")
            eliminados += 1
    
    # Eliminar templates standalone del directorio raíz
    for template in templates_standalone:
        file_path = os.path.join(BASE_DIR, template)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Eliminado: {template} (standalone)")
            eliminados += 1
    
    return eliminados

def main():
    """Función principal"""
    print("🧹 LIMPIEZA DE TEMPLATES DEL PROYECTO SMA")
    print("=" * 50)
    print("Este script eliminará templates duplicados, obsoletos o innecesarios.")
    print("Se creará un backup antes de proceder.\n")
    
    # Analizar templates
    templates_a_eliminar, templates_standalone = analizar_templates()
    
    if not templates_a_eliminar and not templates_standalone:
        print("\n✨ ¡No hay templates para eliminar! El proyecto ya está limpio.")
        return
    
    total_a_eliminar = len(templates_a_eliminar) + len(templates_standalone)
    
    print(f"\n⚠️  SE VAN A ELIMINAR {total_a_eliminar} TEMPLATES")
    respuesta = input("\n¿Continuar? (s/N): ").strip().lower()
    
    if respuesta not in ['s', 'sí', 'si', 'y', 'yes']:
        print("❌ Operación cancelada por el usuario.")
        return
    
    # Crear backup
    crear_backup()
    
    # Eliminar templates
    print(f"\n🗑️  Eliminando templates...")
    eliminados = eliminar_templates(templates_a_eliminar, templates_standalone)
    
    print(f"\n✅ LIMPIEZA COMPLETADA")
    print("=" * 30)
    print(f"📊 Templates eliminados: {eliminados}")
    print(f"💾 Backup disponible en: {BACKUP_DIR}")
    print("\n🎉 El proyecto ha sido limpiado exitosamente.")
    print("📝 Los templates funcionales principales se mantuvieron intactos.")

if __name__ == "__main__":
    main()
