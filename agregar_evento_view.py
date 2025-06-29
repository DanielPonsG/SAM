"""
Vista temporal para agregar eventos al calendario
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from smapp.models import EventoCalendario, Curso

@login_required
def agregar_evento_temp(request):
    """Vista para agregar un nuevo evento al calendario"""
    from django.utils import timezone
    
    # Determinar tipo de usuario y permisos
    user_type = 'otro'
    puede_crear_eventos = False
    
    if request.user.is_superuser:
        user_type = 'administrador'
        puede_crear_eventos = True
    else:
        try:
            if hasattr(request.user, 'perfil') and request.user.perfil:
                user_type = request.user.perfil.tipo_usuario
                puede_crear_eventos = user_type in ['administrador', 'director', 'profesor']
            elif hasattr(request.user, 'profesor'):
                user_type = 'profesor'
                puede_crear_eventos = True
        except Exception as e:
            if request.user.is_superuser or request.user.is_staff:
                user_type = 'administrador'
                puede_crear_eventos = True
    
    if not puede_crear_eventos:
        context = {
            'user_type': user_type,
            'required_types': ['administrador', 'director', 'profesor'],
            'error_message': 'No tienes permisos para crear eventos.'
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
            # Validaciones de servidor
            titulo = request.POST.get('titulo', '').strip()
            fecha = request.POST.get('fecha')
            descripcion = request.POST.get('descripcion', '').strip()
            hora_inicio = request.POST.get('hora_inicio') or None
            hora_fin = request.POST.get('hora_fin') or None
            tipo_evento = request.POST.get('tipo_evento', 'general')
            prioridad = request.POST.get('prioridad', 'media')
            dirigido_a = request.POST.get('dirigido_a', 'todos')
            
            # Validar campos obligatorios
            if not titulo:
                messages.error(request, 'El título es obligatorio')
                return render(request, 'agregar_evento.html', {'cursos': cursos})
            if not fecha:
                messages.error(request, 'La fecha es obligatoria')
                return render(request, 'agregar_evento.html', {'cursos': cursos})
            
            # Validar horas
            if hora_inicio and hora_fin:
                from datetime import datetime
                try:
                    inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                    fin = datetime.strptime(hora_fin, '%H:%M').time()
                    if inicio >= fin:
                        messages.error(request, 'La hora de inicio debe ser menor que la hora de fin')
                        return render(request, 'agregar_evento.html', {'cursos': cursos})
                except ValueError:
                    messages.error(request, 'Formato de hora inválido')
                    return render(request, 'agregar_evento.html', {'cursos': cursos})
            
            # Crear evento
            evento = EventoCalendario.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                tipo_evento=tipo_evento,
                prioridad=prioridad,
                para_todos_los_cursos=dirigido_a == 'todos',
                solo_profesores=dirigido_a == 'solo_profesores',
                creado_por=request.user
            )
            
            # Asignar cursos específicos si es necesario
            if dirigido_a == 'cursos_especificos':
                cursos_ids = request.POST.getlist('cursos_especificos')
                if not cursos_ids:
                    messages.error(request, 'Debes seleccionar al menos un curso específico')
                    evento.delete()
                    return render(request, 'agregar_evento.html', {'cursos': cursos})
                
                # Validar que el usuario tenga permisos sobre los cursos seleccionados
                if user_type == 'profesor':
                    profesor = request.user.profesor
                    cursos_permitidos = Curso.objects.filter(
                        Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor)
                    ).values_list('id', flat=True)
                    
                    cursos_no_permitidos = [cid for cid in cursos_ids if int(cid) not in cursos_permitidos]
                    if cursos_no_permitidos:
                        messages.error(request, 'No tienes permisos para crear eventos en algunos de los cursos seleccionados')
                        evento.delete()
                        return render(request, 'agregar_evento.html', {'cursos': cursos})
                
                evento.cursos.set(cursos_ids)
            
            messages.success(request, f'Evento "{titulo}" creado exitosamente')
            return redirect('calendario')
            
        except Exception as e:
            messages.error(request, f'Error al crear el evento: {str(e)}')
            return render(request, 'agregar_evento.html', {'cursos': cursos})
    
    context = {
        'cursos': cursos,
        'user_type': user_type,
        'puede_crear_eventos': puede_crear_eventos
    }
    return render(request, 'agregar_evento.html', context)
