"""
Vistas para editar y eliminar eventos del calendario
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from smapp.models import EventoCalendario, Curso
from smapp.forms import EventoCalendarioForm

@login_required
def editar_evento_temp(request, evento_id):
    """Vista para editar un evento existente"""
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    
    # Verificar permisos
    user_type = 'otro'
    puede_editar = False
    
    if request.user.is_superuser:
        user_type = 'administrador'
        puede_editar = True
    else:
        try:
            if hasattr(request.user, 'perfil') and request.user.perfil:
                user_type = request.user.perfil.tipo_usuario
                puede_editar = user_type in ['administrador', 'director']
                
                # Los profesores solo pueden editar sus propios eventos
                if user_type == 'profesor' and evento.creado_por == request.user:
                    puede_editar = True
            elif hasattr(request.user, 'profesor') and evento.creado_por == request.user:
                user_type = 'profesor'
                puede_editar = True
        except Exception as e:
            if request.user.is_superuser or request.user.is_staff:
                user_type = 'administrador'
                puede_editar = True
    
    if not puede_editar:
        context = {
            'user_type': user_type,
            'required_types': ['administrador', 'director', 'profesor (propio evento)'],
            'error_message': 'No tienes permisos para editar este evento.'
        }
        return render(request, 'error_permisos.html', context, status=403)
    
    # Obtener cursos disponibles según el tipo de usuario
    cursos = []
    if user_type in ['administrador', 'director']:
        cursos = Curso.objects.all().order_by('nivel', 'paralelo', 'anio')
    elif user_type == 'profesor':
        try:
            profesor = request.user.profesor
            cursos = Curso.objects.filter(
                Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor)
            ).distinct().order_by('nivel', 'paralelo', 'anio')
        except:
            cursos = []
    
    if request.method == 'POST':
        try:
            # Actualizar campos básicos
            evento.titulo = request.POST.get('titulo', '').strip()
            evento.fecha = request.POST.get('fecha')
            evento.descripcion = request.POST.get('descripcion', '').strip()
            evento.hora_inicio = request.POST.get('hora_inicio') or None
            evento.hora_fin = request.POST.get('hora_fin') or None
            evento.tipo_evento = request.POST.get('tipo_evento', 'general')
            evento.prioridad = request.POST.get('prioridad', 'media')
            
            dirigido_a = request.POST.get('dirigido_a', 'todos')
            evento.para_todos_los_cursos = dirigido_a == 'todos'
            evento.solo_profesores = dirigido_a == 'solo_profesores'
            
            # Validar campos obligatorios
            if not evento.titulo:
                messages.error(request, 'El título es obligatorio')
                return render(request, 'editar_evento.html', {
                    'evento': evento, 
                    'cursos': cursos,
                    'cursos_seleccionados': evento.cursos.all()
                })
            if not evento.fecha:
                messages.error(request, 'La fecha es obligatoria')
                return render(request, 'editar_evento.html', {
                    'evento': evento, 
                    'cursos': cursos,
                    'cursos_seleccionados': evento.cursos.all()
                })
            
            # Validar horas
            if evento.hora_inicio and evento.hora_fin:
                from datetime import datetime
                try:
                    inicio = datetime.strptime(evento.hora_inicio, '%H:%M').time() if isinstance(evento.hora_inicio, str) else evento.hora_inicio
                    fin = datetime.strptime(evento.hora_fin, '%H:%M').time() if isinstance(evento.hora_fin, str) else evento.hora_fin
                    if inicio >= fin:
                        messages.error(request, 'La hora de inicio debe ser menor que la hora de fin')
                        return render(request, 'editar_evento.html', {
                            'evento': evento, 
                            'cursos': cursos,
                            'cursos_seleccionados': evento.cursos.all()
                        })
                except ValueError:
                    messages.error(request, 'Formato de hora inválido')
                    return render(request, 'editar_evento.html', {
                        'evento': evento, 
                        'cursos': cursos,
                        'cursos_seleccionados': evento.cursos.all()
                    })
            
            # Guardar cambios
            evento.save()
            
            # Actualizar cursos específicos
            if dirigido_a == 'cursos_especificos':
                cursos_ids = request.POST.getlist('cursos_especificos')
                if not cursos_ids:
                    messages.error(request, 'Debes seleccionar al menos un curso específico')
                    return render(request, 'editar_evento.html', {
                        'evento': evento, 
                        'cursos': cursos,
                        'cursos_seleccionados': evento.cursos.all()
                    })
                
                # Validar permisos sobre cursos
                if user_type == 'profesor':
                    profesor = request.user.profesor
                    cursos_permitidos = Curso.objects.filter(
                        Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor)
                    ).values_list('id', flat=True)
                    
                    cursos_no_permitidos = [cid for cid in cursos_ids if int(cid) not in cursos_permitidos]
                    if cursos_no_permitidos:
                        messages.error(request, 'No tienes permisos para asignar el evento a algunos de los cursos seleccionados')
                        return render(request, 'editar_evento.html', {
                            'evento': evento, 
                            'cursos': cursos,
                            'cursos_seleccionados': evento.cursos.all()
                        })
                
                evento.cursos.set(cursos_ids)
            else:
                # Limpiar cursos si no es específico
                evento.cursos.clear()
            
            messages.success(request, f'Evento "{evento.titulo}" actualizado exitosamente')
            return redirect('calendario')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el evento: {str(e)}')
            return render(request, 'editar_evento.html', {
                'evento': evento, 
                'cursos': cursos,
                'cursos_seleccionados': evento.cursos.all()
            })
    
    # Determinar tipo de dirigido_a actual
    dirigido_a_actual = 'todos'
    if evento.solo_profesores:
        dirigido_a_actual = 'solo_profesores'
    elif evento.cursos.exists():
        dirigido_a_actual = 'cursos_especificos'
    
    context = {
        'evento': evento,
        'cursos': cursos,
        'cursos_seleccionados': evento.cursos.all(),
        'dirigido_a_actual': dirigido_a_actual,
        'user_type': user_type,
        'puede_editar': puede_editar
    }
    return render(request, 'editar_evento.html', context)

@login_required
def eliminar_evento_temp(request, evento_id):
    """Vista para eliminar un evento"""
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    
    # Verificar permisos (misma lógica que editar)
    user_type = 'otro'
    puede_eliminar = False
    
    if request.user.is_superuser:
        user_type = 'administrador'
        puede_eliminar = True
    else:
        try:
            if hasattr(request.user, 'perfil') and request.user.perfil:
                user_type = request.user.perfil.tipo_usuario
                puede_eliminar = user_type in ['administrador', 'director']
                
                # Los profesores solo pueden eliminar sus propios eventos
                if user_type == 'profesor' and evento.creado_por == request.user:
                    puede_eliminar = True
            elif hasattr(request.user, 'profesor') and evento.creado_por == request.user:
                user_type = 'profesor'
                puede_eliminar = True
        except Exception as e:
            if request.user.is_superuser or request.user.is_staff:
                user_type = 'administrador'
                puede_eliminar = True
    
    if not puede_eliminar:
        context = {
            'user_type': user_type,
            'required_types': ['administrador', 'director', 'profesor (propio evento)'],
            'error_message': 'No tienes permisos para eliminar este evento.'
        }
        return render(request, 'error_permisos.html', context, status=403)
    
    if request.method == 'POST':
        titulo_evento = evento.titulo
        evento.delete()
        messages.success(request, f'Evento "{titulo_evento}" eliminado exitosamente')
        return redirect('calendario')
    
    context = {
        'evento': evento,
        'user_type': user_type,
        'puede_eliminar': puede_eliminar
    }
    return render(request, 'eliminar_evento.html', context)
