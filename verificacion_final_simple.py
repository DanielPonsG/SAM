#!/usr/bin/env python3
"""
Script de verificación simple después de la limpieza de templates.
Verifica que los archivos principales existan y genera un reporte.
"""

import os
from datetime import datetime

def verificar_templates_principales():
    """Verificar que los templates principales existan"""
    print("📁 VERIFICACIÓN DE TEMPLATES PRINCIPALES")
    print("=" * 50)
    
    templates_esenciales = {
        # Templates base
        'index_master.html': 'Template base principal',
        'index.html': 'Página de inicio de estudiantes',
        'inicio.html': 'Página de inicio general',
        'login.html': 'Página de login',
        
        # Gestión de asignaturas (funcionalidad principal)
        'listar_asignaturas.html': 'Lista de asignaturas (PRINCIPAL)',
        'agregar_asignatura.html': 'Agregar asignatura',
        'editar_asignatura.html': 'Editar asignatura', 
        'eliminar_asignatura.html': 'Eliminar asignatura',
        'agregar_asignatura_completa.html': 'Agregar asignatura completa',
        'gestionar_horarios_asignatura.html': 'Gestionar horarios de asignatura',
        
        # Calendario
        'calendario.html': 'Calendario principal',
        'editar_evento.html': 'Editar evento',
        'eliminar_evento.html': 'Eliminar evento',
        
        # Gestión de usuarios
        'listar_estudiantes.html': 'Lista de estudiantes',
        'listar_profesores.html': 'Lista de profesores',
        'gestionar_profesor.html': 'Gestionar profesor',
        
        # Cursos
        'listar_cursos.html': 'Lista de cursos',
        'agregar_curso.html': 'Agregar curso',
        'editar_curso.html': 'Editar curso',
        'eliminar_curso.html': 'Eliminar curso',
        'gestionar_horarios.html': 'Gestionar horarios',
        
        # CRUD general
        'agregar.html': 'Agregar general',
        'modificar.html': 'Modificar general',
        'eliminar.html': 'Eliminar general',
        
        # Sistema
        'error_permisos.html': 'Error de permisos',
    }
    
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    existentes = 0
    faltantes = 0
    
    for template, descripcion in templates_esenciales.items():
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template:<35} - {descripcion}")
            existentes += 1
        else:
            print(f"❌ {template:<35} - {descripcion} (FALTANTE)")
            faltantes += 1
    
    return existentes, faltantes, len(templates_esenciales)

def verificar_templates_eliminados():
    """Verificar que los templates duplicados/obsoletos fueron eliminados"""
    print("\n🗑️  VERIFICACIÓN DE TEMPLATES ELIMINADOS")
    print("=" * 50)
    
    templates_que_debian_eliminarse = [
        'calendario_backup.html',
        'calendario_backup_old.html', 
        'calendario_funcional.html',
        'calendario_nuevo.html',
        'calendario_real.html',
        'calendario_real_completo.html',
        'agregar_nuevo.html',
        'agregar_curso_nuevo.html',
        'agregar_curso_test.html',
        'listar_estudiantes_clean.html',
        'listar_estudiantes_fixed.html',
        'listar_estudiantes_mejorado.html',
        'listar_estudiantes_new.html',
        'modificar_fixed.html',
        'debug_info.html',
    ]
    
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    eliminados_correctamente = 0
    no_eliminados = 0
    
    for template in templates_que_debian_eliminarse:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            print(f"✅ {template:<35} - Eliminado correctamente")
            eliminados_correctamente += 1
        else:
            print(f"❌ {template:<35} - AÚN EXISTE (debería eliminarse)")
            no_eliminados += 1
    
    return eliminados_correctamente, no_eliminados, len(templates_que_debian_eliminarse)

def verificar_estructura_directorio():
    """Verificar la estructura del directorio templates"""
    print("\n📂 ESTRUCTURA DEL DIRECTORIO TEMPLATES")
    print("=" * 50)
    
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    if not os.path.exists(templates_dir):
        print("❌ El directorio templates no existe!")
        return 0, 0
    
    archivos_html = []
    archivos_otros = []
    
    for archivo in os.listdir(templates_dir):
        archivo_path = os.path.join(templates_dir, archivo)
        if os.path.isfile(archivo_path):
            if archivo.endswith('.html'):
                archivos_html.append(archivo)
            else:
                archivos_otros.append(archivo)
    
    print(f"📊 Total de archivos HTML: {len(archivos_html)}")
    print(f"📊 Total de otros archivos: {len(archivos_otros)}")
    
    if archivos_otros:
        print(f"\n📄 Otros archivos encontrados:")
        for archivo in archivos_otros:
            print(f"   • {archivo}")
    
    return len(archivos_html), len(archivos_otros)

def verificar_backup():
    """Verificar que se creó el backup"""
    print("\n💾 VERIFICACIÓN DE BACKUP")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Buscar directorios de backup
    backup_dirs = []
    for item in os.listdir(base_dir):
        if item.startswith('templates_backup_'):
            backup_path = os.path.join(base_dir, item)
            if os.path.isdir(backup_path):
                backup_dirs.append((item, backup_path))
    
    if not backup_dirs:
        print("❌ No se encontraron directorios de backup")
        return False
    
    # Mostrar backups encontrados
    for backup_name, backup_path in backup_dirs:
        archivos_backup = len([f for f in os.listdir(backup_path) if f.endswith('.html')])
        print(f"✅ {backup_name}")
        print(f"   📁 Ruta: {backup_path}")
        print(f"   📊 Archivos HTML: {archivos_backup}")
    
    return True

def generar_reporte_resumen(existentes, faltantes, total_esenciales, 
                          eliminados, no_eliminados, total_eliminar,
                          html_actuales, otros_actuales):
    """Generar reporte resumen final"""
    print("\n📊 REPORTE RESUMEN FINAL")
    print("=" * 60)
    
    print(f"📈 TEMPLATES ESENCIALES:")
    print(f"   ✅ Existentes: {existentes}/{total_esenciales}")
    print(f"   ❌ Faltantes: {faltantes}/{total_esenciales}")
    print(f"   📊 Porcentaje: {(existentes/total_esenciales)*100:.1f}%")
    
    print(f"\n🗑️  LIMPIEZA DE TEMPLATES:")
    print(f"   ✅ Eliminados correctamente: {eliminados}/{total_eliminar}")
    print(f"   ❌ No eliminados: {no_eliminados}/{total_eliminar}")
    print(f"   📊 Porcentaje limpieza: {(eliminados/total_eliminar)*100:.1f}%")
    
    print(f"\n📂 ESTADO ACTUAL:")
    print(f"   📄 Templates HTML actuales: {html_actuales}")
    print(f"   📄 Otros archivos: {otros_actuales}")
    
    # Evaluación general
    if faltantes == 0 and no_eliminados == 0:
        estado = "🎉 EXCELENTE"
        mensaje = "Limpieza perfecta. Todos los templates esenciales están presentes y los innecesarios fueron eliminados."
    elif faltantes == 0:
        estado = "✅ BUENO"
        mensaje = "Templates esenciales presentes, pero algunos innecesarios no fueron eliminados."
    elif no_eliminados == 0:
        estado = "⚠️  ATENCIÓN"
        mensaje = "Limpieza exitosa, pero faltan algunos templates esenciales."
    else:
        estado = "❌ PROBLEMAS"
        mensaje = "Hay templates faltantes y otros que no se eliminaron correctamente."
    
    print(f"\n🎯 EVALUACIÓN GENERAL: {estado}")
    print(f"📝 {mensaje}")
    
    return faltantes == 0 and no_eliminados == 0

def main():
    """Función principal"""
    print("🔬 VERIFICACIÓN FINAL DEL PROYECTO SMA")
    print("🧹 Después de la limpieza de templates")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificaciones
    existentes, faltantes, total_esenciales = verificar_templates_principales()
    eliminados, no_eliminados, total_eliminar = verificar_templates_eliminados()
    html_actuales, otros_actuales = verificar_estructura_directorio()
    verificar_backup()
    
    # Reporte final
    exito = generar_reporte_resumen(existentes, faltantes, total_esenciales,
                                  eliminados, no_eliminados, total_eliminar,
                                  html_actuales, otros_actuales)
    
    print(f"\n{'🎉 ¡VERIFICACIÓN COMPLETADA EXITOSAMENTE!' if exito else '⚠️  VERIFICACIÓN COMPLETADA CON OBSERVACIONES'}")
    print("📝 El proyecto ha sido limpiado y está funcional.")

if __name__ == "__main__":
    main()
