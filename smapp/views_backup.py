from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura, PeriodoAcademico
from .forms import EstudianteForm, ProfesorForm, EventoCalendarioForm, CursoForm, HorarioCursoForm, AsignaturaForm, AsignaturaCompletaForm, SeleccionCursoAlumnoForm, CalificacionForm, AsistenciaAlumnoForm, AsistenciaProfesorForm, RegistroMasivoAsistenciaForm
from django.db import models
from django.db.models import Q, Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Perfil
from django.http import HttpResponseForbidden, JsonResponse
from django.forms import formset_factory
from .models import Inscripcion, Grupo, Calificacion, AsistenciaAlumno, AsistenciaProfesor
from datetime import date, datetime, timedelta
from .decorators import admin_required, profesor_admin_required, all_users_required, profesor_con_asignaturas_required
from django.contrib import messages
import json

# Create your views here.
# Vista de la página de inicio del maestro
def index_master(request):
    """
    Redirección.
    """
    return render(request, 'index_master.html')
# Vista de la página de inicio del alumno
def index(request):
    """
    Redirección a la página de inicio.
    """
    return render(request, 'index.html')

# Vistas para el CRUD de Administrador
@admin_required
def agregar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    mensaje = ""
    if tipo == 'profesor':
        form = ProfesorForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            # Crear usuario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            # Crear perfil
            Perfil.objects.create(user=user, tipo_usuario='profesor')
            # Crear profesor
            profesor = form.save(commit=False)
            profesor.user = user
            profesor.save()
            # Si tienes campos ManyToMany (como asignaturas), asígnalos después de save()
            if 'asignaturas' in form.cleaned_data:
                profesor.asignaturas.set(form.cleaned_data['asignaturas'])
            mensaje = "Profesor agregado correctamente."
            form = ProfesorForm()  # Limpiar formulario
    else:
        form = EstudianteForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            # Crear usuario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            # Crear perfil
            Perfil.objects.create(user=user, tipo_usuario='alumno')
            # Crear estudiante
            estudiante = form.save(commit=False)
            estudiante.user = user
            estudiante.save()
            # Si tienes campos ManyToMany (como cursos), asígnalos después de save()
            if 'cursos' in form.cleaned_data:
                estudiante.cursos.set(form.cleaned_data['cursos'])
            mensaje = "Estudiante agregado correctamente."
            form = EstudianteForm()  # Limpiar formulario
    return render(request, 'agregar.html', {'form': form, 'tipo': tipo, 'mensaje': mensaje})
@admin_required
def modificar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    query = request.GET.get('q', '')
    seleccionado_id = request.GET.get('id')
    mensaje = ""
    form = None
    resultados = []

    if tipo == 'profesor':
        if query:
            resultados = Profesor.objects.filter(
                Q(primer_nombre__icontains=query) |
                Q(apellido_paterno__icontains=query) |
                Q(codigo_profesor__icontains=query) |
                Q(id__iexact=query)  # Permite buscar por ID exacto
            )
        else:
            resultados = Profesor.objects.none()
        if seleccionado_id:
            seleccionado = Profesor.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                form = ProfesorForm(request.POST, instance=seleccionado)
                if form.is_valid():
                    form.save()
                    mensaje = "Profesor modificado correctamente."
            else:
                form = ProfesorForm(instance=seleccionado)
    else:
        if query:
            resultados = Estudiante.objects.filter(
                Q(primer_nombre__icontains=query) |
                Q(apellido_paterno__icontains=query) |
                Q(codigo_estudiante__icontains=query) |
                Q(id__iexact=query)  # Permite buscar por ID exacto
            )
        else:
            resultados = Estudiante.objects.none()
        if seleccionado_id:
            seleccionado = Estudiante.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                form = EstudianteForm(request.POST, instance=seleccionado)
                if form.is_valid():
                    form.save()
                    mensaje = "Estudiante modificado correctamente."
            else:
                form = EstudianteForm(instance=seleccionado)

    return render(request, 'modificar.html', {
        'tipo': tipo,
        'query': query,
        'resultados': resultados,
        'form': form,
        'seleccionado_id': seleccionado_id,
        'mensaje': mensaje
    })
@admin_required
def eliminar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    query = request.GET.get('q', '')
    seleccionado_id = request.GET.get('id')
    mensaje = ""
    resultados = []
    objeto = None

    # Eliminar por ID directo
    if request.method == 'POST' and request.POST.get('eliminar_por_id'):
        id_a_eliminar = request.POST.get('id_a_eliminar')
        if tipo == 'profesor':
            try:
                obj = Profesor.objects.get(id=id_a_eliminar)
                obj.delete()
                mensaje = f"Profesor con ID {id_a_eliminar} eliminado correctamente."
            except Profesor.DoesNotExist:
                mensaje = f"No existe un profesor con ID {id_a_eliminar}."
        else:
            try:
                obj = Estudiante.objects.get(id=id_a_eliminar)
                obj.delete()
                mensaje = f"Estudiante con ID {id_a_eliminar} eliminado correctamente."
            except Estudiante.DoesNotExist:
                mensaje = f"No existe un estudiante con ID {id_a_eliminar}."

    # Buscar y mostrar resultados
    if tipo == 'profesor':
        if query:
            resultados = Profesor.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_profesor__icontains=query)
            )
        else:
            resultados = Profesor.objects.none()
        if seleccionado_id:
            objeto = Profesor.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                objeto.delete()
                mensaje = "Profesor eliminado correctamente."
                objeto = None
    else:
        if query:
            resultados = Estudiante.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_estudiante__icontains=query)
            )
        else:
            resultados = Estudiante.objects.none()
        if seleccionado_id:
            objeto = Estudiante.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                objeto.delete()
                mensaje = "Estudiante eliminado correctamente."
                objeto = None

    return render(request, 'eliminar.html', {
        'tipo': tipo,
        'query': query,
        'resultados': resultados,
        'objeto': objeto,
        'seleccionado_id': seleccionado_id,
        'mensaje': mensaje
    })

@profesor_admin_required
def listar_estudiantes(request):
    # Filtros para estudiantes
    q_estudiante = request.GET.get('q_estudiante', '')
    genero_estudiante = request.GET.get('genero_estudiante', '')
    tipo_doc_estudiante = request.GET.get('tipo_doc_estudiante', '')
    fecha_ingreso = request.GET.get('fecha_ingreso', '')
    
    # Filtros para profesores
    q_profesor = request.GET.get('q_profesor', '')
    genero_profesor = request.GET.get('genero_profesor', '')
    especialidad_profesor = request.GET.get('especialidad_profesor', '')

    # Obtener todos los estudiantes y profesores
    estudiantes = Estudiante.objects.select_related('user').all()
    profesores = Profesor.objects.select_related('user').all()

    # Aplicar filtros para estudiantes
    if q_estudiante:
        estudiantes = estudiantes.filter(
            models.Q(primer_nombre__icontains=q_estudiante) |
            models.Q(segundo_nombre__icontains=q_estudiante) |
            models.Q(apellido_paterno__icontains=q_estudiante) |
            models.Q(apellido_materno__icontains=q_estudiante) |
            models.Q(codigo_estudiante__icontains=q_estudiante) |
            models.Q(numero_documento__icontains=q_estudiante) |
            models.Q(email__icontains=q_estudiante)
        )
    
    if genero_estudiante:
        estudiantes = estudiantes.filter(genero=genero_estudiante)
    
    if tipo_doc_estudiante:
        estudiantes = estudiantes.filter(tipo_documento=tipo_doc_estudiante)
    
    if fecha_ingreso:
        estudiantes = estudiantes.filter(fecha_ingreso=fecha_ingreso)

    # Aplicar filtros para profesores
    if q_profesor:
        profesores = profesores.filter(
            models.Q(primer_nombre__icontains=q_profesor) |
            models.Q(segundo_nombre__icontains=q_profesor) |
            models.Q(apellido_paterno__icontains=q_profesor) |
            models.Q(apellido_materno__icontains=q_profesor) |
            models.Q(codigo_profesor__icontains=q_profesor) |
            models.Q(numero_documento__icontains=q_profesor) |
            models.Q(email__icontains=q_profesor)
        )
    
    if genero_profesor:
        profesores = profesores.filter(genero=genero_profesor)
    
    if especialidad_profesor:
        profesores = profesores.filter(especialidad__icontains=especialidad_profesor)

    # Ordenar resultados
    estudiantes = estudiantes.order_by('primer_nombre', 'apellido_paterno')
    profesores = profesores.order_by('primer_nombre', 'apellido_paterno')

    # Estadísticas
    total_estudiantes = estudiantes.count()
    total_profesores = profesores.count()
    
    # Obtener especialidades únicas para el filtro
    especialidades = Profesor.objects.values_list('especialidad', flat=True).distinct().exclude(especialidad__isnull=True).exclude(especialidad__exact='')
    
    return render(request, 'listar_estudiantes.html', {
        'estudiantes': estudiantes,
        'profesores': profesores,
        'estudiantes_filtrados': estudiantes,  # Para compatibilidad con template
        'profesores_filtrados': profesores,    # Para compatibilidad con template
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
        'especialidades': especialidades,
    })

@admin_required
def listar_profesores(request):
    """Vista para que el administrador gestione profesores"""
    filtro_profesor = request.GET.get('filtro_profesor', '')
    
    # Obtener todos los profesores
    profesores = Profesor.objects.select_related('user').all()
    
    # Aplicar filtros si existen
    if filtro_profesor:
        profesores = profesores.filter(
            models.Q(primer_nombre__icontains=filtro_profesor) |
            models.Q(apellido_paterno__icontains=filtro_profesor) |
            models.Q(apellido_materno__icontains=filtro_profesor) |
            models.Q(codigo_profesor__icontains=filtro_profesor) |
            models.Q(email__icontains=filtro_profesor) |
            models.Q(id__iexact=filtro_profesor)
        )
    
    # Estadísticas
    total_profesores = profesores.count()
    profesores_activos = profesores.filter(user__is_active=True).count()
    profesores_con_asignaturas = profesores.filter(asignaturas__isnull=False).distinct().count()
    
    # Obtener asignaturas para mostrar información
    from .models import Asignatura
    asignaturas = Asignatura.objects.all()
    
    context = {
        'profesores': profesores,
        'total_profesores': total_profesores,
        'profesores_activos': profesores_activos,
        'profesores_con_asignaturas': profesores_con_asignaturas,
        'filtro_profesor': filtro_profesor,
        'asignaturas': asignaturas,
        'user_type': 'administrador',
    }
    
    return render(request, 'listar_profesores.html', context)

@admin_required
def gestionar_profesor(request, profesor_id=None):
    """Vista para agregar/editar profesores"""
    from django.contrib.auth.models import User
    from .models import Perfil
    
    profesor = None
    if profesor_id:
        try:
            profesor = Profesor.objects.get(id=profesor_id)
        except Profesor.DoesNotExist:
            messages.error(request, 'El profesor no existe.')
            return redirect('listar_profesores')
    
    if request.method == 'POST':
        try:
            # Datos del formulario
            primer_nombre = request.POST.get('primer_nombre')
            apellido_paterno = request.POST.get('apellido_paterno')
            apellido_materno = request.POST.get('apellido_materno', '')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono', '')
            direccion = request.POST.get('direccion', '')
            codigo_profesor = request.POST.get('codigo_profesor')
            asignaturas_ids = request.POST.getlist('asignaturas')
            
            # Validaciones básicas
            if not all([primer_nombre, apellido_paterno, email, codigo_profesor]):
                messages.error(request, 'Todos los campos obligatorios deben ser completados.')
                return render(request, 'gestionar_profesor.html', {
                    'profesor': profesor,
                    'asignaturas': Asignatura.objects.all(),
                    'action': 'Editar' if profesor else 'Agregar',
                })
            
            if profesor:
                # Editar profesor existente
                profesor.primer_nombre = primer_nombre
                profesor.apellido_paterno = apellido_paterno
                profesor.apellido_materno = apellido_materno
                profesor.email = email
                profesor.telefono = telefono
                profesor.direccion = direccion
                profesor.codigo_profesor = codigo_profesor
                profesor.save()
                
                # Actualizar asignaturas
                profesor.asignaturas.set(asignaturas_ids)
                
                # Actualizar usuario asociado si existe
                if profesor.user:
                    profesor.user.first_name = primer_nombre
                    profesor.user.last_name = f"{apellido_paterno} {apellido_materno}".strip()
                    profesor.user.email = email
                    profesor.user.save()
                
                messages.success(request, f'Profesor {primer_nombre} {apellido_paterno} actualizado correctamente.')
                
            else:
                # Crear nuevo profesor
                username = f"prof_{codigo_profesor.lower()}"
                password = f"temp_{codigo_profesor}123"  # Contraseña temporal
                
                # Verificar si el username ya existe
                if User.objects.filter(username=username).exists():
                    counter = 1
                    original_username = username
                    while User.objects.filter(username=f"{original_username}_{counter}").exists():
                        counter += 1
                    username = f"{original_username}_{counter}"
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=primer_nombre,
                    last_name=f"{apellido_paterno} {apellido_materno}".strip()
                )
                
                # Crear perfil
                perfil = Perfil.objects.create(
                    user=user,
                    tipo_usuario='profesor'
                )
                
                # Crear profesor
                profesor = Profesor.objects.create(
                    user=user,
                    primer_nombre=primer_nombre,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    email=email,
                    telefono=telefono,
                    direccion=direccion,
                    codigo_profesor=codigo_profesor
                )
                
                # Asignar asignaturas
                profesor.asignaturas.set(asignaturas_ids)
                
                messages.success(request, f'Profesor {primer_nombre} {apellido_paterno} creado correctamente.')
                messages.info(request, f'Usuario: {username}, Contraseña temporal: {password}')
            
            return redirect('listar_profesores')
            
        except Exception as e:
            messages.error(request, f'Error al guardar profesor: {str(e)}')
    
    context = {
        'profesor': profesor,
        'asignaturas': Asignatura.objects.all(),
        'action': 'Editar' if profesor else 'Agregar',
    }
    
    return render(request, 'gestionar_profesor.html', context)

@all_users_required
def calendario(request):
    """Vista del calendario con funcionalidad completa"""
    from django.utils import timezone
    from django.db.models import Q
    from django.http import JsonResponse
    import json
    
    # Determinar tipo de usuario y permisos
    user_type = 'otro'
    puede_crear_eventos = False
    
    # Lógica mejorada para detectar tipo de usuario
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
            elif hasattr(request.user, 'estudiante'):
                user_type = 'estudiante'
        except Exception as e:
            # Fallback para superusuarios sin perfil
            if request.user.is_superuser or request.user.is_staff:
                user_type = 'administrador'
                puede_crear_eventos = True
    
    print(f"DEBUG: Usuario {request.user.username}, tipo: {user_type}, puede crear: {puede_crear_eventos}")  # Debug
    
    # Obtener filtros
    fecha_filtro = request.GET.get('fecha_filtro', '')
    curso_filtro = request.GET.get('curso_filtro', '')
    
    # Base de eventos según tipo de usuario
    eventos_base = EventoCalendario.objects.all()
    
    # Filtrar eventos por permisos de usuario
    if user_type == 'estudiante':
        # Estudiantes ven eventos de sus cursos o eventos generales (NO los de solo profesores)
        try:
            estudiante = request.user.estudiante
            cursos_estudiante = estudiante.cursos.all()
            eventos_base = eventos_base.filter(
                Q(para_todos_los_cursos=True) | Q(cursos__in=cursos_estudiante)
            ).filter(solo_profesores=False).distinct()
        except:
            eventos_base = eventos_base.filter(
                para_todos_los_cursos=True,
                solo_profesores=False
            )
    elif user_type == 'profesor':
        # Profesores ven eventos de sus cursos asignados, eventos generales y eventos solo para profesores
        try:
            profesor = request.user.profesor
            cursos_profesor = Curso.objects.filter(
                Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor)
            ).distinct()
            eventos_base = eventos_base.filter(
                Q(para_todos_los_cursos=True) | Q(cursos__in=cursos_profesor) | Q(solo_profesores=True)
            ).distinct()
        except:
            eventos_base = eventos_base.filter(
                Q(para_todos_los_cursos=True) | Q(solo_profesores=True)
            )
    # Administradores y directores ven todos los eventos (sin filtro adicional)
    
    # Aplicar filtros de búsqueda
    eventos = eventos_base
    if fecha_filtro:
        try:
            from datetime import datetime
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha=fecha_obj)
        except ValueError:
            pass
    
    if curso_filtro and user_type in ['administrador', 'director']:
        eventos = eventos.filter(cursos__id=curso_filtro)
    
    # Manejar creación de evento (AJAX POST)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not puede_crear_eventos:
            return JsonResponse({'success': False, 'error': 'Sin permisos para crear eventos'})
        
        try:
            # Validaciones de servidor
            titulo = request.POST.get('titulo', '').strip()
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio') or None
            hora_fin = request.POST.get('hora_fin') or None
            
            # Validar campos obligatorios
            if not titulo:
                return JsonResponse({'success': False, 'error': 'El título es obligatorio'})
            if not fecha:
                return JsonResponse({'success': False, 'error': 'La fecha es obligatoria'})
            
            # Validar horas
            if hora_inicio and hora_fin:
                from datetime import datetime
                inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                fin = datetime.strptime(hora_fin, '%H:%M').time()
                if inicio >= fin:
                    return JsonResponse({'success': False, 'error': 'La hora de inicio debe ser menor que la hora de fin'})
            
            # Crear evento
            dirigido_a = request.POST.get('dirigido_a', 'todos')
            evento = EventoCalendario.objects.create(
                titulo=titulo,
                descripcion=request.POST.get('descripcion', ''),
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                tipo_evento=request.POST.get('tipo_evento', 'general'),
                prioridad=request.POST.get('prioridad', 'media'),
                para_todos_los_cursos=dirigido_a == 'todos',
                solo_profesores=dirigido_a == 'solo_profesores',
                creado_por=request.user
            )
            
            # Asignar cursos específicos si es necesario
            if dirigido_a == 'cursos_especificos':
                cursos_ids = request.POST.getlist('cursos_especificos')
                if not cursos_ids:
                    return JsonResponse({'success': False, 'error': 'Debes seleccionar al menos un curso específico'})
                
                # Validar que el usuario tenga permisos sobre los cursos seleccionados
                if user_type == 'profesor':
                    profesor = request.user.profesor
                    cursos_permitidos = Curso.objects.filter(
                        Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor)
                    ).values_list('id', flat=True)
                    
                    cursos_no_permitidos = [cid for cid in cursos_ids if int(cid) not in cursos_permitidos]
                    if cursos_no_permitidos:
                        return JsonResponse({'success': False, 'error': 'No tienes permisos para crear eventos en algunos de los cursos seleccionados'})
                
                evento.cursos.set(cursos_ids)
            
            return JsonResponse({
                'success': True, 
                'evento_id': evento.id,
                'message': 'Evento creado exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al crear el evento: {str(e)}'})
    
    # Preparar datos para FullCalendar
    eventos_json = []
    for evento in eventos:
        eventos_json.append({
            'id': evento.id,
            'title': evento.titulo,
            'start': evento.fecha.isoformat(),
            'description': evento.descripcion or '',
            'backgroundColor': evento.color_por_tipo,
            'borderColor': evento.color_por_tipo,
            'textColor': '#fff',
            'url': f'/eventos/detalle/{evento.id}/' if hasattr(evento, 'get_absolute_url') else None
        })
    
    print(f"DEBUG: Preparando {len(eventos_json)} eventos para FullCalendar")  # Debug
    
    # Obtener cursos disponibles para filtros y modal
    cursos = []
    if user_type in ['administrador', 'director']:
        cursos = Curso.objects.filter(anio=timezone.now().year).order_by('nivel', 'paralelo')
    elif user_type == 'profesor':
        try:
            profesor = request.user.profesor
            cursos = Curso.objects.filter(
                Q(profesor_jefe=profesor) | Q(asignaturas__profesores=profesor),
                anio=timezone.now().year
            ).distinct().order_by('nivel', 'paralelo')
        except:
            cursos = []
    
    context = {
        'eventos': eventos.order_by('fecha')[:10],  # Próximos 10 eventos para la tabla
        'eventos_json': json.dumps(eventos_json),
        'cursos': cursos,
        'fecha_filtro': fecha_filtro,
        'curso_filtro': curso_filtro,
        'puede_crear_eventos': puede_crear_eventos,
        'user_type': user_type,
        'tipos_evento': EventoCalendario.TIPO_EVENTO_CHOICES,
        'prioridades': EventoCalendario.PRIORIDAD_CHOICES,
    }
    
    return render(request, 'calendario.html', context)

@login_required
def inicio(request):
    """Vista del panel de inicio personalizado por tipo de usuario"""
    context = {
        'user': request.user,
    }
    return render(request, 'inicio.html', context)

def login_view(request):
    """Vista de login personalizada"""
    mensaje = ""
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirigir según el tipo de usuario
                    if user.is_superuser or (hasattr(user, 'perfil') and user.perfil.tipo_usuario in ['director', 'administrador']):
                        return redirect('calendario')  # Ir directo al calendario para admins
                    else:
                        return redirect('inicio')
                else:
                    mensaje = "Esta cuenta está desactivada."
            else:
                mensaje = "Usuario o contraseña incorrectos."
        else:
            mensaje = "Por favor ingresa usuario y contraseña."
    
    return render(request, 'login.html', {'mensaje': mensaje})

@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    return redirect('login')

# Agregar funciones básicas restantes para que el sistema funcione
@login_required
def mis_horarios(request):
    """Vista para mostrar horarios del usuario"""
    context = {}
    return render(request, 'mis_horarios.html', context)

@login_required  
def mi_curso(request):
    """Vista para mostrar información del curso"""
    context = {}
    return render(request, 'mi_curso.html', context)

@login_required
def listar_cursos(request):
    """Vista para listar cursos y gestionar estudiantes pendientes"""
    from .forms import AsignarEstudianteForm
    from django.contrib import messages
    from django.utils import timezone
    
    # Manejar la asignación de estudiantes pendientes
    if request.method == 'POST' and 'asignar_estudiante' in request.POST:
        # Verificar permisos
        if not (hasattr(request.user, 'perfil') and 
                request.user.perfil.tipo_usuario in ['director', 'administrador', 'profesor_jefe']):
            messages.error(request, 'No tienes permisos para asignar estudiantes a cursos.')
        else:
            form_asignar = AsignarEstudianteForm(request.POST)
            if form_asignar.is_valid():
                estudiante = form_asignar.cleaned_data['estudiante']
                curso = form_asignar.cleaned_data['curso']
                
                # Asignar el estudiante al curso
                curso.estudiantes.add(estudiante)
                messages.success(
                    request, 
                    f'Estudiante {estudiante.primer_nombre} {estudiante.apellido_paterno} '
                    f'asignado exitosamente al curso {curso.get_nivel_display()}{curso.paralelo}.'
                )
            else:
                for error in form_asignar.errors.values():
                    messages.error(request, error[0])
    
    # Obtener datos de cursos
    cursos_queryset = Curso.objects.filter(anio=timezone.now().year)
    total_cursos = cursos_queryset.count()
    
    # Ordenar correctamente: básica antes que media
    cursos = sorted(cursos_queryset, key=lambda c: (c.orden_nivel, c.paralelo))
    
    # Calcular estadísticas
    total_estudiantes_asignados = sum(curso.estudiantes.count() for curso in cursos)
    profesores_jefe_asignados = len([curso for curso in cursos if curso.profesor_jefe])
    total_asignaturas_asignadas = sum(curso.asignaturas.count() for curso in cursos)
    
    # Obtener estudiantes pendientes (no asignados a ningún curso del año actual)
    estudiantes_asignados_ids = set()
    for curso in cursos_queryset:
        estudiantes_curso = list(curso.estudiantes.values_list('id', flat=True))
        estudiantes_asignados_ids.update(estudiantes_curso)
    
    estudiantes_pendientes = Estudiante.objects.exclude(
        id__in=estudiantes_asignados_ids
    ).order_by('primer_nombre', 'apellido_paterno')
    
    # Crear formulario para asignar estudiantes pendientes
    form_asignar = AsignarEstudianteForm()
    
    # Verificar permisos del usuario
    puede_editar = (hasattr(request.user, 'perfil') and 
                   request.user.perfil.tipo_usuario in ['director', 'administrador', 'profesor_jefe'])
    
    context = {
        'cursos': cursos,
        'total_cursos': total_cursos,
        'total_estudiantes_asignados': total_estudiantes_asignados,
        'profesores_jefe_asignados': profesores_jefe_asignados,
        'total_asignaturas_asignadas': total_asignaturas_asignadas,
        'estudiantes_pendientes': estudiantes_pendientes,
        'total_estudiantes_pendientes': estudiantes_pendientes.count(),
        'form_asignar': form_asignar,
        'puede_editar': puede_editar,
        'anio_actual': timezone.now().year,
    }
    return render(request, 'listar_cursos.html', context)

@login_required
def listar_asignaturas(request):
    """Vista para listar asignaturas con filtros y gestión completa"""
    from django.utils import timezone
    from django.db.models import Q, Count
    
    # Determinar tipo de usuario
    user_type = 'otro'
    if request.user.is_superuser:
        user_type = 'administrador'
    elif hasattr(request.user, 'perfil'):
        user_type = request.user.perfil.tipo_usuario
    elif hasattr(request.user, 'profesor'):
        user_type = 'profesor'
    elif hasattr(request.user, 'estudiante'):
        user_type = 'estudiante'
    
    # Manejar solicitudes POST para asignar/remover profesores y cursos
    if request.method == 'POST' and user_type in ['administrador', 'director']:
        if 'asignar_profesor' in request.POST:
            try:
                asignatura_id = request.POST.get('asignatura_id')
                profesor_id = request.POST.get('profesor_id')
                
                if asignatura_id and profesor_id:
                    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
                    profesor = get_object_or_404(Profesor, id=profesor_id)
                    
                    # Agregar profesor a la asignatura (usando ManyToMany)
                    asignatura.profesores_responsables.add(profesor)
                    
                    # También actualizar el campo individual para compatibilidad
                    if not asignatura.profesor_responsable:
                        asignatura.profesor_responsable = profesor
                        asignatura.save()
                    
                    messages.success(request, f'Profesor {profesor.get_nombre_completo()} asignado exitosamente a {asignatura.nombre}.')
                else:
                    messages.error(request, 'Datos incompletos para asignar profesor.')
                    
            except Exception as e:
                messages.error(request, f'Error al asignar profesor: {str(e)}')
                
        elif 'remover_profesor' in request.POST:
            try:
                asignatura_id = request.POST.get('asignatura_id')
                profesor_id = request.POST.get('profesor_id')
                
                if asignatura_id and profesor_id:
                    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
                    profesor = get_object_or_404(Profesor, id=profesor_id)
                    
                    # Remover profesor de la asignatura
                    asignatura.profesores_responsables.remove(profesor)
                    
                    # Si era el profesor responsable principal, limpiar ese campo
                    if asignatura.profesor_responsable == profesor:
                        # Asignar otro profesor responsable si hay más
                        otros_profesores = asignatura.profesores_responsables.first()
                        asignatura.profesor_responsable = otros_profesores
                        asignatura.save()
                    
                    messages.success(request, f'Profesor {profesor.get_nombre_completo()} removido exitosamente de {asignatura.nombre}.')
                else:
                    messages.error(request, 'Datos incompletos para remover profesor.')
                    
            except Exception as e:
                messages.error(request, f'Error al remover profesor: {str(e)}')
                
        elif 'asignar_curso' in request.POST:
            try:
                asignatura_id = request.POST.get('asignatura_id')
                curso_id = request.POST.get('curso_id')
                
                if asignatura_id and curso_id:
                    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
                    curso = get_object_or_404(Curso, id=curso_id)
                    
                    # Asignar asignatura al curso
                    curso.asignaturas.add(asignatura)
                    
                    messages.success(request, f'Asignatura {asignatura.nombre} asignada exitosamente al curso {curso}.')
                else:
                    messages.error(request, 'Datos incompletos para asignar curso.')
                    
            except Exception as e:
                messages.error(request, f'Error al asignar curso: {str(e)}')
                
        elif 'remover_curso' in request.POST:
            try:
                asignatura_id = request.POST.get('asignatura_id')
                curso_nombre = request.POST.get('curso_nombre')
                
                if asignatura_id and curso_nombre:
                    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
                    
                    # Buscar el curso por el nombre corto (ej: "1° BásicoA")
                    cursos = asignatura.cursos.all()
                    curso_encontrado = None
                    
                    for curso in cursos:
                        if curso.get_nivel_display() + curso.paralelo == curso_nombre:
                            curso_encontrado = curso
                            break
                    
                    if curso_encontrado:
                        # Remover asignatura del curso
                        curso_encontrado.asignaturas.remove(asignatura)
                        messages.success(request, f'Asignatura {asignatura.nombre} removida exitosamente del curso {curso_encontrado}.')
                    else:
                        messages.error(request, 'No se pudo encontrar el curso especificado.')
                else:
                    messages.error(request, 'Datos incompletos para remover curso.')
                    
            except Exception as e:
                messages.error(request, f'Error al remover curso: {str(e)}')
        
        # Redirigir para evitar reenvío del formulario
        return redirect('listar_asignaturas')
    
    # Obtener filtros
    filtro_codigo = request.GET.get('filtro_codigo', '')
    filtro_profesor = request.GET.get('filtro_profesor', '')
    filtro_sin_profesor = request.GET.get('filtro_sin_profesor', '')
    filtro_nombre = request.GET.get('filtro_nombre', '')
    
    # Base de asignaturas según tipo de usuario
    if user_type == 'estudiante':
        # Estudiantes solo ven sus asignaturas
        try:
            estudiante = request.user.estudiante
            cursos_estudiante = estudiante.cursos.all()
            asignaturas = Asignatura.objects.filter(cursos__in=cursos_estudiante).distinct()
            cursos_alumno_ids = [curso.id for curso in cursos_estudiante]
        except:
            asignaturas = Asignatura.objects.none()
            cursos_alumno_ids = []
    elif user_type == 'profesor':
        # Profesores ven sus asignaturas asignadas
        try:
            profesor = request.user.profesor
            asignaturas = profesor.asignaturas.all()
        except:
            asignaturas = Asignatura.objects.none()
        cursos_alumno_ids = []
    else:
        # Administradores y directores ven todas las asignaturas con información de cursos
        asignaturas = Asignatura.objects.select_related('profesor_responsable').prefetch_related(
            'horarios__curso', 
            'cursos',  # Agregar cursos para mostrar en la tabla
            'profesores_responsables'  # Incluir profesores del many-to-many
        )
        cursos_alumno_ids = []
        
        # Aplicar filtros para administradores/directores
        if filtro_codigo:
            asignaturas = asignaturas.filter(codigo_asignatura__icontains=filtro_codigo)
        
        if filtro_nombre:
            asignaturas = asignaturas.filter(nombre__icontains=filtro_nombre)
        
        if filtro_profesor:
            asignaturas = asignaturas.filter(
                Q(profesor_responsable__primer_nombre__icontains=filtro_profesor) |
                Q(profesor_responsable__apellido_paterno__icontains=filtro_profesor) |
                Q(profesor_responsable__codigo_profesor__icontains=filtro_profesor)
            )
        
        if filtro_sin_profesor:
            asignaturas = asignaturas.filter(profesor_responsable__isnull=True)
    
    # Ordenar asignaturas
    asignaturas = asignaturas.order_by('nombre')
    
    # Estadísticas mejoradas para administradores/directores
    estadisticas = {}
    total_asignaturas = 0
    asignaturas_con_profesor = 0
    asignaturas_sin_profesor_count = 0
    asignaturas_sin_profesor = []
    asignaturas_con_cursos = 0
    asignaturas_sin_cursos = 0
    
    if user_type in ['administrador', 'director']:
        from django.db.models import Count
        
        total_asignaturas = Asignatura.objects.count()
        
        # Contar asignaturas con/sin profesor (considerando ambos campos)
        asignaturas_con_profesor_query = Asignatura.objects.filter(
            Q(profesor_responsable__isnull=False) | Q(profesores_responsables__isnull=False)
        ).distinct()
        asignaturas_con_profesor = asignaturas_con_profesor_query.count()
        asignaturas_sin_profesor_count = total_asignaturas - asignaturas_con_profesor
        
        # Asignaturas sin profesor para la sección especial
        asignaturas_sin_profesor = Asignatura.objects.filter(
            profesor_responsable__isnull=True,
            profesores_responsables__isnull=True
        ).distinct()
        
        # Contar asignaturas con/sin cursos
        asignaturas_con_cursos = Asignatura.objects.filter(cursos__isnull=False).distinct().count()
        asignaturas_sin_cursos = total_asignaturas - asignaturas_con_cursos
        
        # Contar asignaturas con/sin horarios
        con_horarios = Asignatura.objects.filter(horarios__isnull=False).distinct().count()
        sin_horarios = total_asignaturas - con_horarios
        
        estadisticas = {
            'total_asignaturas': total_asignaturas,
            'con_profesor': asignaturas_con_profesor,
            'sin_profesor': asignaturas_sin_profesor_count,
            'con_cursos': asignaturas_con_cursos,
            'sin_cursos': asignaturas_sin_cursos,
            'con_horarios': con_horarios,
            'sin_horarios': sin_horarios
        }
    
    # Obtener profesores para el filtro
    profesores = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
    
    # Obtener cursos disponibles para asignar
    from django.utils import timezone
    anio_actual = timezone.now().year
    cursos_disponibles = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')

    context = {
        'asignaturas': asignaturas,
        'tipo_usuario': user_type,
        'cursos_alumno_ids': cursos_alumno_ids,
        'user': request.user,
        'filtro_codigo': filtro_codigo,
        'filtro_profesor': filtro_profesor,
        'filtro_sin_profesor': filtro_sin_profesor,
        'filtro_nombre': filtro_nombre,
        'profesores': profesores,
        'cursos_disponibles': cursos_disponibles,  # Agregado para el modal
        'estadisticas': estadisticas,
        'puede_gestionar': user_type in ['administrador', 'director'],
        'puede_editar': user_type in ['administrador', 'director'],  # Alias para compatibilidad
        'total_asignaturas': total_asignaturas,
        'asignaturas_con_profesor': asignaturas_con_profesor,
        'asignaturas_sin_profesor_count': asignaturas_sin_profesor_count,
        'asignaturas_sin_profesor': asignaturas_sin_profesor,
        'asignaturas_con_cursos': asignaturas_con_cursos,
        'asignaturas_sin_cursos': asignaturas_sin_cursos,
    }
    
    return render(request, 'listar_asignaturas.html', context)

@login_required
def ingresar_notas(request):
    """Vista para ingresar notas - Selección por curso y asignatura"""
    from .forms import CalificacionForm
    from django.utils import timezone
    
    # Verificar permisos
    user_type = getattr(request.user, 'perfil', None)
    if not user_type or user_type.tipo_usuario not in ['director', 'administrador', 'profesor']:
        messages.error(request, 'No tienes permisos para ingresar notas.')
        return redirect('inicio')
    
    # Inicializar variables
    cursos_disponibles = []
    curso_seleccionado = None
    asignaturas_disponibles = []
    asignatura_seleccionada = None
    estudiantes_curso_asignatura = []
    
    # Obtener parámetros
    curso_id = request.GET.get('curso_id') or request.POST.get('curso_id')
    asignatura_id = request.GET.get('asignatura_id') or request.POST.get('asignatura_id')
    
    # Obtener datos según el tipo de usuario
    if user_type.tipo_usuario in ['director', 'administrador']:
        # Director y administrador pueden ver todos los cursos
        anio_actual = timezone.now().year
        cursos_disponibles = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
        
        if curso_id:
            try:
                curso_seleccionado = cursos_disponibles.get(id=curso_id)
                
                # CORREGIDO: Solo obtener asignaturas que están asignadas al curso
                asignaturas_disponibles = curso_seleccionado.asignaturas.all().order_by('nombre')
                
                # Si no hay asignaturas asignadas al curso, mostrar mensaje informativo
                if not asignaturas_disponibles.exists():
                    messages.info(request, f'El curso {curso_seleccionado} no tiene asignaturas asignadas. Asigna asignaturas al curso primero desde la gestión de asignaturas.')
                
            except Curso.DoesNotExist:
                messages.error(request, 'El curso seleccionado no existe.')
                
    else:
        # Profesor: solo sus cursos y asignaturas
        try:
            profesor = Profesor.objects.get(user=request.user)
            
            # Cursos donde es profesor jefe
            cursos_como_jefe = Curso.objects.filter(profesor_jefe=profesor)
            
            # Cursos donde imparte asignaturas
            cursos_con_asignaturas = Curso.objects.filter(
                estudiantes__inscripcion__grupo__profesor=profesor
            ).distinct()
            
            # Combinar ambos tipos de cursos
            cursos_disponibles = (cursos_como_jefe | cursos_con_asignaturas).distinct().order_by('nivel', 'paralelo')
            
            if curso_id:
                try:
                    curso_seleccionado = cursos_disponibles.get(id=curso_id)
                    
                    # CORREGIDO: Solo obtener asignaturas asignadas al curso donde el profesor tiene permisos
                    asignaturas_curso = curso_seleccionado.asignaturas.all()
                    
                    # Filtrar solo las asignaturas donde el profesor es responsable
                    asignaturas_profesor = profesor.asignaturas_responsable.all()
                    asignaturas_profesor_old = Asignatura.objects.filter(profesor_responsable=profesor)
                    
                    # Asignaturas donde es jefe de curso (todas las del curso)
                    asignaturas_jefe = asignaturas_curso if curso_seleccionado.profesor_jefe == profesor else Asignatura.objects.none()
                    
                    # Combinar todas las fuentes de asignaturas para este profesor y curso
                    ids_asignaturas = set()
                    ids_asignaturas.update(asignaturas_profesor.values_list('id', flat=True))
                    ids_asignaturas.update(asignaturas_profesor_old.values_list('id', flat=True))
                    ids_asignaturas.update(asignaturas_jefe.values_list('id', flat=True))
                    
                    # Solo incluir asignaturas que están asignadas al curso
                    asignaturas_disponibles = asignaturas_curso.filter(
                        id__in=ids_asignaturas
                    ).distinct().order_by('nombre')
                    
                    if not asignaturas_disponibles.exists():
                        if asignaturas_curso.exists():
                            messages.warning(request, f'No tienes permisos para ingresar notas en las asignaturas de {curso_seleccionado}.')
                        else:
                            messages.info(request, f'El curso {curso_seleccionado} no tiene asignaturas asignadas.')
                    
                except Curso.DoesNotExist:
                    messages.error(request, 'No tienes permisos para este curso.')
                    
        except Profesor.DoesNotExist:
            messages.error(request, 'No tienes un perfil de profesor asociado.')
            return redirect('inicio')
    
    # Si hay curso y asignatura seleccionados, obtener estudiantes
    if curso_seleccionado and asignatura_id:
        try:
            asignatura_seleccionada = asignaturas_disponibles.get(id=asignatura_id)
            
            # Obtener o crear grupo para esta asignatura y curso
            periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
            if not periodo_actual:
                # Crear periodo académico si no existe
                from datetime import date
                anio_actual = timezone.now().year
                periodo_actual = PeriodoAcademico.objects.create(
                    nombre=f"Año Lectivo {anio_actual}",
                    fecha_inicio=date(anio_actual, 3, 1),
                    fecha_fin=date(anio_actual, 12, 15),
                    activo=True
                )
            
            # Buscar o crear grupo
            profesor_asignatura = asignatura_seleccionada.profesores_responsables.first() or asignatura_seleccionada.profesor_responsable
            
            grupo, created = Grupo.objects.get_or_create(
                asignatura=asignatura_seleccionada,
                periodo_academico=periodo_actual,
                profesor=profesor_asignatura,
                defaults={
                    'capacidad_maxima': 50
                }
            )
            
            if created:
                print(f"Grupo creado: {grupo}")
            
            # Inscribir automáticamente a todos los estudiantes del curso si no están inscritos
            estudiantes_curso = curso_seleccionado.estudiantes.all()
            for estudiante in estudiantes_curso:
                inscripcion, created = Inscripcion.objects.get_or_create(
                    estudiante=estudiante,
                    grupo=grupo
                )
                if created:
                    print(f"Inscripción creada: {inscripcion}")
            
            # Obtener inscripciones de estudiantes del curso en la asignatura seleccionada
            inscripciones_filtradas = Inscripcion.objects.filter(
                estudiante__in=curso_seleccionado.estudiantes.all(),
                grupo__asignatura=asignatura_seleccionada
            ).select_related('estudiante', 'grupo')
            
            # Para profesores, verificar que sea su grupo
            if user_type.tipo_usuario == 'profesor':
                profesor = Profesor.objects.get(user=request.user)
                inscripciones_filtradas = inscripciones_filtradas.filter(grupo__profesor=profesor)
            
            estudiantes_curso_asignatura = inscripciones_filtradas.order_by(
                'estudiante__primer_nombre', 
                'estudiante__apellido_paterno'
            )
            
        except Asignatura.DoesNotExist:
            messages.error(request, 'La asignatura seleccionada no existe.')
    
    # Procesar formulario de notas
    if request.method == 'POST' and estudiantes_curso_asignatura:
        notas_creadas = 0
        errores = 0
        
        for inscripcion in estudiantes_curso_asignatura:
            nombre_evaluacion = request.POST.get(f'nombre_evaluacion_{inscripcion.id}', '').strip()
            puntaje_str = request.POST.get(f'puntaje_{inscripcion.id}', '').strip()
            porcentaje_str = request.POST.get(f'porcentaje_{inscripcion.id}', '0').strip()
            detalle = request.POST.get(f'detalle_{inscripcion.id}', '').strip()
            descripcion = request.POST.get(f'descripcion_{inscripcion.id}', '').strip()
            
            # Solo crear nota si hay nombre de evaluación y puntaje
            if nombre_evaluacion and puntaje_str:
                try:
                    puntaje = float(puntaje_str)
                    porcentaje = float(porcentaje_str) if porcentaje_str else 0
                    
                    # Validar rango de puntaje
                    if puntaje < 1.0 or puntaje > 7.0:
                        messages.error(request, f'El puntaje para {inscripcion.estudiante.primer_nombre} debe estar entre 1.0 y 7.0')
                        errores += 1
                        continue
                    
                    # Validar rango de porcentaje
                    if porcentaje < 0 or porcentaje > 100:
                        messages.error(request, f'El porcentaje para {inscripcion.estudiante.primer_nombre} debe estar entre 0 y 100')
                        errores += 1
                        continue
                    
                    # Crear la calificación
                    Calificacion.objects.create(
                        inscripcion=inscripcion,
                        nombre_evaluacion=nombre_evaluacion,
                        puntaje=puntaje,
                        porcentaje=porcentaje,
                        detalle=detalle,
                        descripcion=descripcion,
                        fecha_evaluacion=timezone.now().date()
                    )
                    notas_creadas += 1
                    
                except ValueError:
                    messages.error(request, f'Valores inválidos para {inscripcion.estudiante.primer_nombre}')
                    errores += 1
                except Exception as e:
                    messages.error(request, f'Error al crear nota para {inscripcion.estudiante.primer_nombre}: {str(e)}')
                    errores += 1
        
        # Mostrar resultado
        if notas_creadas > 0:
            messages.success(request, f'Se crearon {notas_creadas} notas exitosamente.')
            if errores > 0:
                messages.warning(request, f'{errores} notas no se pudieron crear debido a errores.')
            
            # Redirigir a ver notas con filtros aplicados
            return redirect(f'/notas/ver/?curso_id={curso_id}&asignatura_id={asignatura_id}')
        else:
            if errores > 0:
                messages.error(request, f'No se crearon notas. {errores} intentos fallaron.')
            else:
                messages.warning(request, 'No se ingresaron datos válidos para crear notas.')
    
    context = {
        'cursos_disponibles': cursos_disponibles,
        'curso_seleccionado': curso_seleccionado,
        'asignaturas_disponibles': asignaturas_disponibles,
        'asignatura_seleccionada': asignatura_seleccionada,
        'estudiantes_curso_asignatura': estudiantes_curso_asignatura,
        'user_type': user_type.tipo_usuario if user_type else 'unknown'
    }
    return render(request, 'ingresar_notas.html', context)

@login_required
def asignar_asignaturas_curso(request):
    """Vista para asignar asignaturas a un curso"""
    if request.method == 'POST':
        # Verificar permisos
        user_type = getattr(request.user, 'perfil', None)
        if not user_type or user_type.tipo_usuario not in ['director', 'administrador']:
            messages.error(request, 'No tienes permisos para asignar asignaturas.')
            return redirect('inicio')
        
        curso_id = request.POST.get('curso_id')
        asignaturas_ids = request.POST.getlist('asignaturas_ids')
        
        if not curso_id or not asignaturas_ids:
            messages.error(request, 'Datos incompletos para asignar asignaturas.')
            return redirect('ingresar_notas')
        
        try:
            curso = get_object_or_404(Curso, id=curso_id)
            asignaturas = Asignatura.objects.filter(id__in=asignaturas_ids)
            
            # Asignar las asignaturas al curso
            asignaturas_asignadas = 0
            for asignatura in asignaturas:
                if asignatura not in curso.asignaturas.all():
                    curso.asignaturas.add(asignatura)
                    asignaturas_asignadas += 1
            
            if asignaturas_asignadas > 0:
                messages.success(
                    request, 
                    f'Se asignaron {asignaturas_asignadas} asignaturas exitosamente al curso {curso}.'
                )
            else:
                messages.warning(request, 'Las asignaturas seleccionadas ya estaban asignadas al curso.')
                
        except Exception as e:
            messages.error(request, f'Error al asignar asignaturas: {str(e)}')
        
        # Redirigir de vuelta a ingresar notas con el curso seleccionado
        return redirect(f'{reverse("ingresar_notas")}?curso_id={curso_id}')
    
    return redirect('ingresar_notas')

@login_required
def ver_notas_curso(request):
    """Vista para ver notas según el tipo de usuario con filtros avanzados"""
    from django.db.models import Avg, Count, Q
    
    user_type = getattr(request.user, 'perfil', None)
    
    if not user_type:
        messages.error(request, 'No tienes un perfil de usuario válido.')
        return redirect('inicio')
    
    # Inicializar variables
    cursos_disponibles = []
    curso_seleccionado = None
    asignaturas_curso = []
    asignatura_seleccionada = None
    calificaciones = []
    asignaturas_disponibles = []
    puede_editar = False
    promedios_estudiantes = {}
    
    # Obtener parámetros de filtrado
    curso_id = request.GET.get('curso_id')
    asignatura_id = request.GET.get('asignatura_id')
    buscar_alumno = request.GET.get('buscar_alumno', '').strip()
    
    # Determinar permisos y datos según tipo de usuario
    if user_type.tipo_usuario in ['director', 'administrador']:
        from django.utils import timezone
        anio_actual = timezone.now().year
        cursos_disponibles = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
        puede_editar = True
        
        if curso_id:
            try:
                curso_seleccionado = cursos_disponibles.get(id=curso_id)
                
                # NUEVA LÓGICA: Combinar asignaturas del curso y con grupos
                asignaturas_curso_directo = curso_seleccionado.asignaturas.all()
                
                inscripciones_curso = Inscripcion.objects.filter(
                    estudiante__in=curso_seleccionado.estudiantes.all()
                ).select_related('grupo__asignatura')
                
                asignaturas_con_grupos = Asignatura.objects.filter(
                    grupo__inscripcion__in=inscripciones_curso
                ).distinct()
                
                # Combinar usando IDs para evitar problemas de union
                ids_asignaturas = set()
                ids_asignaturas.update(asignaturas_curso_directo.values_list('id', flat=True))
                ids_asignaturas.update(asignaturas_con_grupos.values_list('id', flat=True))
                
                asignaturas_curso = Asignatura.objects.filter(id__in=ids_asignaturas).distinct().order_by('nombre')
                
                # Filtrar por asignatura si se selecciona
                if asignatura_id:
                    try:
                        asignatura_seleccionada = asignaturas_curso.get(id=asignatura_id)
                        inscripciones_filtradas = inscripciones_curso.filter(
                            grupo__asignatura=asignatura_seleccionada
                        )
                    except Asignatura.DoesNotExist:
                        inscripciones_filtradas = inscripciones_curso
                else:
                    inscripciones_filtradas = inscripciones_curso
                
                # Aplicar filtro de búsqueda de alumno
                if buscar_alumno:
                    inscripciones_filtradas = inscripciones_filtradas.filter(
                        Q(estudiante__primer_nombre__icontains=buscar_alumno) |
                        Q(estudiante__apellido_paterno__icontains=buscar_alumno) |
                        Q(estudiante__apellido_materno__icontains=buscar_alumno) |
                        Q(estudiante__numero_documento__icontains=buscar_alumno) |
                        Q(estudiante__codigo_estudiante__icontains=buscar_alumno)
                    )
                
                calificaciones = Calificacion.objects.filter(
                    inscripcion__in=inscripciones_filtradas
                ).select_related(
                    'inscripcion__estudiante', 
                    'inscripcion__grupo__asignatura'
                ).order_by(
                    'inscripcion__estudiante__primer_nombre',
                    'inscripcion__estudiante__apellido_paterno',
                    'inscripcion__grupo__asignatura__nombre',
                    'fecha_evaluacion'
                )
                
                # Calcular promedios por estudiante
                for inscripcion in inscripciones_filtradas:
                    estudiante = inscripcion.estudiante
                    if estudiante.id not in promedios_estudiantes:
                        notas_estudiante = Calificacion.objects.filter(
                            inscripcion__estudiante=estudiante,
                            inscripcion__in=inscripciones_curso
                        )
                        if asignatura_seleccionada:
                            notas_estudiante = notas_estudiante.filter(
                                inscripcion__grupo__asignatura=asignatura_seleccionada
                            )
                        
                        promedio = notas_estudiante.aggregate(Avg('puntaje'))['puntaje__avg']
                        total_notas = notas_estudiante.count()
                        
                        promedios_estudiantes[estudiante.id] = {
                            'estudiante': estudiante,
                            'promedio': round(promedio, 1) if promedio else 0,
                            'total_notas': total_notas,
                            'estado': 'Aprobado' if promedio and promedio >= 4.0 else 'Reprobado'
                        }
                        
            except Curso.DoesNotExist:
                messages.error(request, 'El curso seleccionado no existe.')
    
    elif user_type.tipo_usuario == 'profesor':
        try:
            profesor = Profesor.objects.get(user=request.user)
            cursos_como_jefe = Curso.objects.filter(profesor_jefe=profesor)
            asignaturas_que_imparte = profesor.asignaturas.all()
            
            if curso_id:
                # Ver notas como profesor jefe
                try:
                    curso_seleccionado = cursos_como_jefe.get(id=curso_id)
                    inscripciones_curso = Inscripcion.objects.filter(
                        estudiante__in=curso_seleccionado.estudiantes.all()
                    ).select_related('estudiante', 'grupo__asignatura')
                    
                    asignaturas_curso = Asignatura.objects.filter(
                        grupo__inscripcion__in=inscripciones_curso
                    ).distinct().order_by('nombre')
                    
                    if asignatura_id:
                        try:
                            asignatura_seleccionada = asignaturas_curso.get(id=asignatura_id)
                            inscripciones_filtradas = inscripciones_curso.filter(
                                grupo__asignatura=asignatura_seleccionada
                            )
                        except Asignatura.DoesNotExist:
                            inscripciones_filtradas = inscripciones_curso
                    else:
                        inscripciones_filtradas = inscripciones_curso
                    
                    if buscar_alumno:
                        inscripciones_filtradas = inscripciones_filtradas.filter(
                            Q(estudiante__primer_nombre__icontains=buscar_alumno) |
                            Q(estudiante__apellido_paterno__icontains=buscar_alumno) |
                            Q(estudiante__apellido_materno__icontains=buscar_alumno) |
                            Q(estudiante__numero_documento__icontains=buscar_alumno) |
                            Q(estudiante__codigo_estudiante__icontains=buscar_alumno)
                        )
                    
                    calificaciones = Calificacion.objects.filter(
                        inscripcion__in=inscripciones_filtradas
                    ).select_related(
                        'inscripcion__estudiante', 
                        'inscripcion__grupo__asignatura'
                    ).order_by(
                        'inscripcion__estudiante__primer_nombre',
                        'inscripcion__estudiante__apellido_paterno',
                        'inscripcion__grupo__asignatura__nombre',
                        'fecha_evaluacion'
                    )
                    
                    puede_editar = False  # Como jefe solo puede ver
                    
                    # Calcular promedios
                    for inscripcion in inscripciones_filtradas:
                        estudiante = inscripcion.estudiante
                        if estudiante.id not in promedios_estudiantes:
                            notas_estudiante = Calificacion.objects.filter(
                                inscripcion__estudiante=estudiante,
                                inscripcion__in=inscripciones_curso
                            )
                            if asignatura_seleccionada:
                                notas_estudiante = notas_estudiante.filter(
                                    inscripcion__grupo__asignatura=asignatura_seleccionada
                                )
                            
                            promedio = notas_estudiante.aggregate(Avg('puntaje'))['puntaje__avg']
                            total_notas = notas_estudiante.count()
                            
                            promedios_estudiantes[estudiante.id] = {
                                'estudiante': estudiante,
                                'promedio': round(promedio, 1) if promedio else 0,
                                'total_notas': total_notas,
                                'estado': 'Aprobado' if promedio and promedio >= 4.0 else 'Reprobado'
                            }
                            
            messages.error(request, 'No tienes un perfil de estudiante asociado.')
            return redirect('inicio')
    
    else:
        messages.error(request, 'Tipo de usuario no válido para ver notas.')
        return redirect('inicio')
    
    # Calcular promedio por asignatura si hay calificaciones
    promedio_asignatura = None
    if calificaciones and asignatura_seleccionada:
        notas_asignatura = calificaciones.filter(
            inscripcion__grupo__asignatura=asignatura_seleccionada
        ) if not isinstance(calificaciones, list) else [
            cal for cal in calificaciones 
            if cal.inscripcion.grupo.asignatura == asignatura_seleccionada
        ]
        
        if notas_asignatura:
            if isinstance(notas_asignatura, list):
                suma_notas = sum(cal.puntaje for cal in notas_asignatura)
                promedio_asignatura = round(suma_notas / len(notas_asignatura), 1)
            else:
                promedio = notas_asignatura.aggregate(Avg('puntaje'))['puntaje__avg']
                promedio_asignatura = round(promedio, 1) if promedio else 0

    context = {
        'cursos_disponibles': cursos_disponibles,
        'curso_seleccionado': curso_seleccionado,
        'asignaturas_curso': asignaturas_curso,
        'asignatura_seleccionada': asignatura_seleccionada,
        'asignaturas_disponibles': asignaturas_disponibles,
        'calificaciones': calificaciones,
        'user_type': user_type.tipo_usuario,
        'puede_editar': puede_editar,
        'total_calificaciones': calificaciones.count() if calificaciones else 0,
        'buscar_alumno': buscar_alumno,
        'promedios_estudiantes': promedios_estudiantes,
        'promedio_asignatura': promedio_asignatura
    }
    return render(request, 'ver_notas_curso.html', context)

@login_required
def registrar_asistencia_alumno(request):
    """Vista simplificada para registrar asistencia solo por curso"""
    from .forms import RegistroMasivoAsistenciaForm
    from django.utils import timezone
    from django.db import transaction
    
    # Verificar permisos básicos
    user_type = getattr(request.user, 'perfil', None)
    if not user_type or user_type.tipo_usuario not in ['director', 'administrador', 'profesor']:
        messages.error(request, 'No tienes permisos para registrar asistencia.')
        return redirect('inicio')
    
    # Obtener cursos según el tipo de usuario
    cursos_disponibles = []
    profesor_actual = None
    
    if user_type.tipo_usuario in ['director', 'administrador']:
        # Administradores y directores ven TODOS los cursos
        cursos_disponibles = Curso.objects.all().order_by('nivel', 'paralelo')
    elif user_type.tipo_usuario == 'profesor':
        try:
            profesor_actual = Profesor.objects.get(user=request.user)
            cursos_ids = set()
            
            # 1. Cursos donde es profesor jefe
            cursos_jefatura = profesor_actual.get_cursos_jefatura()
            cursos_ids.update(cursos_jefatura.values_list('id', flat=True))
            
            # 2. Cursos donde imparte asignaturas
            cursos_asignaturas = Curso.objects.filter(
                estudiantes__inscripcion__grupo__profesor=profesor_actual
            )
            cursos_ids.update(cursos_asignaturas.values_list('id', flat=True))
            
            # 3. Cursos donde es responsable principal de asignatura
            cursos_responsable = Curso.objects.filter(
                estudiantes__inscripcion__grupo__profesor=profesor_actual
            )
            cursos_ids.update(cursos_responsable.values_list('id', flat=True))
            
            # Obtener cursos únicos
            if cursos_ids:
                cursos_disponibles = Curso.objects.filter(id__in=list(cursos_ids)).distinct().order_by('nivel', 'paralelo')
            else:
                cursos_disponibles = Curso.objects.none()
            
            if not cursos_disponibles.exists():
                messages.error(request, 'No tienes cursos asignados para registrar asistencia.')
                return redirect('inicio')
                
        except Profesor.DoesNotExist:
            messages.error(request, 'No tienes un perfil de profesor asociado.')
            return redirect('inicio')
    
    # Procesar formulario
    if request.method == 'POST':
        # Registro masivo
        if 'registro_masivo' in request.POST:
            curso_id = request.POST.get('curso')
            
            try:
                curso = Curso.objects.get(id=curso_id)
                
                # Verificar permisos
                if curso not in cursos_disponibles:
                    messages.error(request, 'No tienes permisos para registrar asistencia en este curso.')
                    return redirect('registrar_asistencia_alumno')
                
                # Obtener asignatura automáticamente
                asignatura = None
                if profesor_actual:
                    # Buscar asignaturas del curso donde el profesor es responsable
                    asignaturas_profesor = curso.asignaturas.filter(
                        Q(profesores_responsables=profesor_actual) |
                        Q(profesor_responsable=profesor_actual)
                    ).first()
                    
                    if asignaturas_profesor:
                        asignatura = asignaturas_profesor
                    else:
                        # Si no tiene asignatura específica, tomar la primera del curso
                        asignatura = curso.asignaturas.first()
                else:
                    # Para administradores, tomar la primera asignatura
                    asignatura = curso.asignaturas.first()
                
                if not asignatura:
                    messages.error(request, f'El curso {curso} no tiene asignaturas configuradas.')
                    return redirect('registrar_asistencia_alumno')
                
                # Procesar asistencia de estudiantes
                fecha_hoy = timezone.now().date()
                hora_actual = timezone.now().time()
                estudiantes_curso = curso.estudiantes.all()
                
                registros_creados = 0
                registros_actualizados = 0
                
                with transaction.atomic():
                    for estudiante in estudiantes_curso:
                        presente = f'presente_{estudiante.id}' in request.POST
                        observacion = request.POST.get(f'observacion_{estudiante.id}', '').strip()
                        justificacion = request.POST.get(f'justificacion_{estudiante.id}', '').strip()
                        
                        # Buscar si ya existe un registro para hoy
                        try:
                            asistencia = AsistenciaAlumno.objects.get(
                                estudiante=estudiante,
                                asignatura=asignatura,
                                fecha=fecha_hoy
                            )
                            # Actualizar registro existente
                            asistencia.presente = presente
                            asistencia.observacion = observacion
                            asistencia.justificacion = justificacion
                            asistencia.profesor_registro = profesor_actual
                            asistencia.hora_registro = hora_actual
                            asistencia.registrado_por_usuario = request.user
                            asistencia.curso = curso
                            asistencia.save()
                            registros_actualizados += 1
                            
                        except AsistenciaAlumno.DoesNotExist:
                            # Crear nuevo registro
                            asistencia = AsistenciaAlumno.objects.create(
                                estudiante=estudiante,
                                curso=curso,
                                asignatura=asignatura,
                                fecha=fecha_hoy,
                                hora_registro=hora_actual,
                                presente=presente,
                                observacion=observacion,
                                justificacion=justificacion,
                                profesor_registro=profesor_actual,
                                registrado_por_usuario=request.user
                            )
                            registros_creados += 1
                
                # Mensaje de éxito
                mensaje = f'Asistencia registrada exitosamente para {curso}. '
                if registros_creados > 0:
                    mensaje += f'{registros_creados} registros nuevos. '
                if registros_actualizados > 0:
                    mensaje += f'{registros_actualizados} registros actualizados.'
                
                messages.success(request, mensaje)
                return redirect('ver_asistencia_alumno')
                
            except Curso.DoesNotExist:
                messages.error(request, 'Curso no encontrado.')
                return redirect('registrar_asistencia_alumno')
            except Exception as e:
                messages.error(request, f'Error al registrar asistencia: {str(e)}')
                return redirect('registrar_asistencia_alumno')
        
        # Formulario inicial - seleccionar curso
        else:
            form = RegistroMasivoAsistenciaForm(request.POST, cursos_disponibles=cursos_disponibles)
            if form.is_valid():
                curso_seleccionado = form.cleaned_data['curso']
                
                # Verificar permisos
                if curso_seleccionado not in cursos_disponibles:
                    messages.error(request, 'No tienes permisos para registrar asistencia en este curso.')
                    return redirect('registrar_asistencia_alumno')
                
                # Obtener asignatura automáticamente
                asignatura_seleccionada = None
                if profesor_actual:
                    asignaturas_profesor = curso_seleccionado.asignaturas.filter(
                        Q(profesores_responsables=profesor_actual) |
                        Q(profesor_responsable=profesor_actual)
                    ).first()
                    
                    if asignaturas_profesor:
                        asignatura_seleccionada = asignaturas_profesor
                    else:
                        asignatura_seleccionada = curso_seleccionado.asignaturas.first()
                else:
                    asignatura_seleccionada = curso_seleccionado.asignaturas.first()
                
                if not asignatura_seleccionada:
                    messages.error(request, f'El curso {curso_seleccionado} no tiene asignaturas configuradas.')
                    return redirect('registrar_asistencia_alumno')
                
                # Obtener estudiantes y registros existentes
                estudiantes = curso_seleccionado.estudiantes.all().order_by('primer_nombre', 'apellido_paterno')
                fecha_hoy = timezone.now().date()
                
                # Obtener asistencias existentes del día
                asistencias_existentes = {}
                asistencias_hoy = AsistenciaAlumno.objects.filter(
                    curso=curso_seleccionado,
                    fecha=fecha_hoy
                ).select_related('estudiante')
                
                for asistencia in asistencias_hoy:
                    asistencias_existentes[asistencia.estudiante.id] = asistencia
                
                return render(request, 'registrar_asistencia_alumno.html', {
                    'mostrar_lista': True,
                    'curso_seleccionado': curso_seleccionado,
                    'asignatura_seleccionada': asignatura_seleccionada,
                    'estudiantes': estudiantes,
                    'asistencias_existentes': asistencias_existentes,
                    'fecha_seleccionada': fecha_hoy,
                    'hora_seleccionada': timezone.now().time(),
                    'profesor_actual': profesor_actual,
                    'form': form
                })
    
    # Mostrar formulario inicial
    form = RegistroMasivoAsistenciaForm(cursos_disponibles=cursos_disponibles)
    
    return render(request, 'registrar_asistencia_alumno.html', {
        'form': form,
        'mostrar_lista': False,
        'cursos_disponibles': cursos_disponibles,
        'profesor_actual': profesor_actual
    })

@login_required
def ver_asistencia_alumno(request):
    """Vista simplificada para ver asistencia solo por curso, semana y estudiante específico"""
    from django.db.models import Q, Count
    from django.utils import timezone
    import datetime
    
    # Verificar permisos
    user_type = getattr(request.user, 'perfil', None)
    if not user_type or user_type.tipo_usuario not in ['director', 'administrador', 'profesor']:
        messages.error(request, 'No tienes permisos para ver asistencia.')
        return redirect('inicio')
    
    # Obtener cursos disponibles según el tipo de usuario
    cursos_disponibles = []
    profesor_actual = None
    
    if user_type.tipo_usuario in ['director', 'administrador']:
        # Administradores y directores ven todos los cursos
        cursos_disponibles = Curso.objects.all().order_by('nivel', 'paralelo')
    elif user_type.tipo_usuario == 'profesor':
        try:
            profesor_actual = Profesor.objects.get(user=request.user)
            # Obtener cursos disponibles para el profesor
            cursos_ids = set()
            
            # Cursos donde es jefe
            cursos_jefatura = profesor_actual.get_cursos_jefatura()
            cursos_ids.update(cursos_jefatura.values_list('id', flat=True))
            
            # Cursos donde hace clases (asignaturas asignadas)
            cursos_asignaturas = Curso.objects.filter(
                asignaturas__profesores_responsables=profesor_actual
            )
            cursos_ids.update(cursos_asignaturas.values_list('id', flat=True))
            
            # Cursos donde es responsable de asignatura
            cursos_responsable = Curso.objects.filter(
                asignaturas__profesor_responsable=profesor_actual
            )
            cursos_ids.update(cursos_responsable.values_list('id', flat=True))
            
            # Obtener todos los cursos del profesor (usar conjunto de IDs para evitar errores)
            if cursos_ids:
                cursos_disponibles = Curso.objects.filter(id__in=list(cursos_ids)).order_by('nivel', 'paralelo')
            else:
                cursos_disponibles = Curso.objects.none()
            
            if not cursos_disponibles.exists():
                messages.error(request, 'No tienes cursos asignados para ver asistencia.')
                return redirect('inicio')
                
        except Profesor.DoesNotExist:
            messages.error(request, 'No tienes un perfil de profesor asociado.')
            return redirect('inicio')
    
    # Obtener filtros simplificados: solo curso, semana y estudiante
    curso_id = request.GET.get('curso')
    estudiante_id = request.GET.get('estudiante')
    semana = request.GET.get('semana')  # Formato: YYYY-MM-DD (lunes de la semana)
    
    # Establecer curso por defecto si no se especifica
    curso_seleccionado = None
    if curso_id:
        try:
            curso_seleccionado = cursos_disponibles.get(id=curso_id)
        except Curso.DoesNotExist:
            messages.error(request, 'No tienes acceso a este curso.')
            return redirect('ver_asistencia_alumno')
    elif cursos_disponibles.exists():
        # Seleccionar el primer curso disponible por defecto
        curso_seleccionado = cursos_disponibles.first()
    
    # Si no hay curso seleccionado, mostrar mensaje
    if not curso_seleccionado:
        return render(request, 'ver_asistencia_alumno.html', {
            'cursos_disponibles': cursos_disponibles,
            'mensaje': 'Selecciona un curso para ver la asistencia',
            'profesor_actual': profesor_actual
        })
    
    # Obtener estudiantes del curso seleccionado
    estudiantes_curso = curso_seleccionado.estudiantes.all().order_by('primer_nombre', 'apellido_paterno')
    
    # Calcular fechas de la semana
    if semana:
        try:
            fecha_lunes = datetime.datetime.strptime(semana, '%Y-%m-%d').date()
        except ValueError:
            fecha_lunes = timezone.now().date()
            fecha_lunes = fecha_lunes - datetime.timedelta(days=fecha_lunes.weekday())
    else:
        # Semana actual por defecto
        fecha_lunes = timezone.now().date()
        fecha_lunes = fecha_lunes - datetime.timedelta(days=fecha_lunes.weekday())
    
    fecha_domingo = fecha_lunes + datetime.timedelta(days=6)
    
    # Base de asistencias del curso en la semana
    asistencias_query = AsistenciaAlumno.objects.filter(
        curso=curso_seleccionado,
        fecha__range=[fecha_lunes, fecha_domingo]
    )
    
    # Filtrar por estudiante específico si se selecciona
    estudiante_seleccionado = None
    if estudiante_id:
        try:
            estudiante_seleccionado = estudiantes_curso.get(id=estudiante_id)
            asistencias_query = asistencias_query.filter(estudiante=estudiante_seleccionado)
        except Estudiante.DoesNotExist:
            pass
    
    # Obtener asistencias
    asistencias = asistencias_query.select_related(
        'estudiante', 'asignatura', 'profesor_registro'
    ).order_by('-fecha', 'asignatura__nombre', 'estudiante__primer_nombre')
    
    # Estadísticas semanales
    total_asistencias = asistencias.count()
    presentes = asistencias.filter(presente=True).count()
    ausentes = asistencias.filter(presente=False).count()
    porcentaje_asistencia = round((presentes / total_asistencias * 100) if total_asistencias > 0 else 0, 1)
    
    # Crear lista de fechas de la semana para navegación
    fechas_semana = []
    for i in range(7):
        fecha = fecha_lunes + datetime.timedelta(days=i)
        fechas_semana.append({
            'fecha': fecha,
            'dia': fecha.strftime('%A'),
            'es_hoy': fecha == timezone.now().date()
        })
    
    # Semana anterior y siguiente para navegación
    semana_anterior = fecha_lunes - datetime.timedelta(days=7)
    semana_siguiente = fecha_lunes + datetime.timedelta(days=7)
    
    context = {
        'cursos_disponibles': cursos_disponibles,
        'curso_seleccionado': curso_seleccionado,
        'estudiantes_curso': estudiantes_curso,
        'estudiante_seleccionado': estudiante_seleccionado,
        'asistencias': asistencias,
        'estadisticas': {
            'total': total_asistencias,
            'presentes': presentes,
            'ausentes': ausentes,
            'porcentaje_asistencia': porcentaje_asistencia
        },
        'fecha_lunes': fecha_lunes,
        'fecha_domingo': fecha_domingo,
        'fechas_semana': fechas_semana,
        'semana_anterior': semana_anterior,
        'semana_siguiente': semana_siguiente,
        'profesor_actual': profesor_actual,
        'filtros': {
            'curso': curso_id,
            'estudiante': estudiante_id,
            'semana': semana
        }
    }
    
    return render(request, 'ver_asistencia_alumno.html', context)

@login_required
def registrar_asistencia_profesor(request):
    """Vista mejorada para registrar asistencia de profesores"""
    from .forms import AsistenciaProfesorForm
    from django.utils import timezone
    
    # Verificar permisos (solo admin/director)
    user_type = getattr(request.user, 'perfil', None)
    if not user_type or user_type.tipo_usuario not in ['director', 'administrador']:
        messages.error(request, 'No tienes permisos para registrar asistencia de profesores.')
        return redirect('inicio')
    
    if request.method == 'POST':
        # Registro masivo de profesores
        if 'registro_masivo' in request.POST:
            fecha_hoy = timezone.now().date()
            
            profesores = Profesor.objects.all()
            asistencias_creadas = 0
            asistencias_actualizadas = 0
            
            try:
                from django.db import transaction
                with transaction.atomic():
                    for profesor in profesores:
                        presente = request.POST.get(f'presente_{profesor.id}') == 'on'
                        observacion = request.POST.get(f'observacion_{profesor.id}', '')
                        justificacion = request.POST.get(f'justificacion_{profesor.id}', '')
                        asignatura_id = request.POST.get(f'asignatura_{profesor.id}')
                        curso_id = request.POST.get(f'curso_{profesor.id}')
                        
                        # Obtener asignatura y curso si se especifican
                        asignatura = None
                        curso = None
                        if asignatura_id:
                            try:
                                asignatura = Asignatura.objects.get(id=asignatura_id)
                            except Asignatura.DoesNotExist:
                                pass
                        
                        if curso_id:
                            try:
                                curso = Curso.objects.get(id=curso_id)
                            except Curso.DoesNotExist:
                                pass
                        
                        # Crear o actualizar asistencia
                        asistencia, created = AsistenciaProfesor.objects.update_or_create(
                            profesor=profesor,
                            asignatura=asignatura,
                            fecha=fecha_hoy,
                            defaults={
                                'curso': curso,
                                'presente': presente,
                                'observacion': observacion,
                                'justificacion': justificacion,
                                'registrado_por_usuario': request.user
                            }
                        )
                        
                        if created:
                            asistencias_creadas += 1
                        else:
                            asistencias_actualizadas += 1
                    
                    messages.success(
                        request, 
                        f'Asistencia registrada exitosamente. '
                        f'Creadas: {asistencias_creadas}, Actualizadas: {asistencias_actualizadas}'
                    )
                    return redirect('ver_asistencia_profesor')
                    
            except Exception as e:
                messages.error(request, f'Error al registrar asistencia: {str(e)}')
        
        # Registro individual
        else:
            form = AsistenciaProfesorForm(request.POST)
            if form.is_valid():
                asistencia = form.save(commit=False)
                asistencia.registrado_por_usuario = request.user
                asistencia.save()
                messages.success(request, 'Asistencia registrada exitosamente.')
                return redirect('ver_asistencia_profesor')
    
    else:
        form = AsistenciaProfesorForm()
    
    # Para mostrar lista de profesores en registro masivo
    profesores = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
    asignaturas = Asignatura.objects.all().order_by('nombre')
    cursos = Curso.objects.all().order_by('nivel', 'paralelo')
    
    # Verificar asistencias existentes para hoy
    fecha_hoy = timezone.now().date()
    asistencias_hoy = {}
    existing = AsistenciaProfesor.objects.filter(fecha=fecha_hoy)
    asistencias_hoy = {(a.profesor.id, a.asignatura.id if a.asignatura else None): a for a in existing}
    
    context = {
        'form': form,
        'profesores': profesores,
        'asignaturas': asignaturas,
        'cursos': cursos,
        'fecha_hoy': fecha_hoy,
        'asistencias_hoy': asistencias_hoy
    }
    
    return render(request, 'registrar_asistencia_profesor.html', context)

@login_required
def ver_asistencia_profesor(request):
    """Vista mejorada para ver asistencia de profesores con filtros avanzados"""
    from django.db.models import Q, Count
    from django.utils import timezone
    import datetime
    
    # Verificar permisos
    user_type = getattr(request.user, 'perfil', None)
    
    if not user_type:
        messages.error(request, 'No tienes un perfil de usuario válido.')
        return redirect('inicio')
    
    # Inicializar variables
    cursos_disponibles = []
    curso_seleccionado = None
    asignaturas_curso = []
    asignatura_seleccionada = None
    calificaciones = []
    asignaturas_disponibles = []
    puede_editar = False
    promedios_estudiantes = {}
    
    # Obtener parámetros de filtrado
    curso_id = request.GET.get('curso_id')
    asignatura_id = request.GET.get('asignatura_id')
    buscar_alumno = request.GET.get('buscar_alumno', '').strip()
    
    # Determinar permisos y datos según tipo de usuario
    if user_type.tipo_usuario in ['director', 'administrador']:
        from django.utils import timezone
        anio_actual = timezone.now().year
        cursos_disponibles = Curso.objects.filter(anio=anio_actual).order_by('nivel', 'paralelo')
        puede_editar = True
        
        if curso_id:
            try:
                curso_seleccionado = cursos_disponibles.get(id=curso_id)
                
                # NUEVA LÓGICA: Combinar asignaturas del curso y con grupos
                asignaturas_curso_directo = curso_seleccionado.asignaturas.all()
                
                inscripciones_curso = Inscripcion.objects.filter(
                    estudiante__in=curso_seleccionado.estudiantes.all()
                ).select_related('grupo__asignatura')
                
                asignaturas_con_grupos = Asignatura.objects.filter(
                    grupo__inscripcion__in=inscripciones_curso
                ).distinct()
                
                # Combinar usando IDs para evitar problemas de union
                ids_asignaturas = set()
                ids_asignaturas.update(asignaturas_curso_directo.values_list('id', flat=True))
                ids_asignaturas.update(asignaturas_con_grupos.values_list('id', flat=True))
                
                asignaturas_curso = Asignatura.objects.filter(id__in=ids_asignaturas).distinct().order_by('nombre')
                
                # Filtrar por asignatura si se selecciona
                if asignatura_id:
                    try:
                        asignatura_seleccionada = asignaturas_curso.get(id=asignatura_id)
                        inscripciones_filtradas = inscripciones_curso.filter(
                            grupo__asignatura=asignatura_seleccionada
                        )
                    except Asignatura.DoesNotExist:
                        inscripciones_filtradas = inscripciones_curso
                else:
                    inscripciones_filtradas = inscripciones_curso
                
                # Aplicar filtro de búsqueda de alumno
                if buscar_alumno:
                    inscripciones_filtradas = inscripciones_filtradas.filter(
                        Q(estudiante__primer_nombre__icontains=buscar_alumno) |
                        Q(estudiante__apellido_paterno__icontains=buscar_alumno) |
                        Q(estudiante__apellido_materno__icontains=buscar_alumno) |
                        Q(estudiante__numero_documento__icontains=buscar_alumno) |
                        Q(estudiante__codigo_estudiante__icontains=buscar_alumno)
                    )
                
                calificaciones = Calificacion.objects.filter(
                    inscripcion__in=inscripciones_filtradas
                ).select_related(
                    'inscripcion__estudiante', 
                    'inscripcion__grupo__asignatura'
                ).order_by(
                    'inscripcion__estudiante__primer_nombre',
                    'inscripcion__estudiante__apellido_paterno',
                    'inscripcion__grupo__asignatura__nombre',
                    'fecha_evaluacion'
                )
                
                # Calcular promedios por estudiante
                for inscripcion in inscripciones_filtradas:
                    estudiante = inscripcion.estudiante
                    if estudiante.id not in promedios_estudiantes:
                        notas_estudiante = Calificacion.objects.filter(
                            inscripcion__estudiante=estudiante,
                            inscripcion__in=inscripciones_curso
                        )
                        if asignatura_seleccionada:
                            notas_estudiante = notas_estudiante.filter(
                                inscripcion__grupo__asignatura=asignatura_seleccionada
                            )
                        
                        promedio = notas_estudiante.aggregate(Avg('puntaje'))['puntaje__avg']
                        total_notas = notas_estudiante.count()
                        
                        promedios_estudiantes[estudiante.id] = {
                            'estudiante': estudiante,
                            'promedio': round(promedio, 1) if promedio else 0,
                            'total_notas': total_notas,
                            'estado': 'Aprobado' if promedio and promedio >= 4.0 else 'Reprobado'
                        }
                        
            except Curso.DoesNotExist:
                messages.error(request, 'El curso seleccionado no existe.')
    
    elif user_type.tipo_usuario == 'profesor':
        try:
            profesor = Profesor.objects.get(user=request.user)
            cursos_como_jefe = Curso.objects.filter(profesor_jefe=profesor)
            asignaturas_que_imparte = profesor.asignaturas.all()
            
            if curso_id:
                # Ver notas como profesor jefe
                try:
                    curso_seleccionado = cursos_como_jefe.get(id=curso_id)
                    inscripciones_curso = Inscripcion.objects.filter(
                        estudiante__in=curso_seleccionado.estudiantes.all()
                    ).select_related('estudiante', 'grupo__asignatura')
                    
                    asignaturas_curso = Asignatura.objects.filter(
                        grupo__inscripcion__in=inscripciones_curso
                    ).distinct().order_by('nombre')
                    
                    if asignatura_id:
                        try:
                            asignatura_seleccionada = asignaturas_curso.get(id=asignatura_id)
                            inscripciones_filtradas = inscripciones_curso.filter(
                                grupo__asignatura=asignatura_seleccionada
                            )
                        except Asignatura.DoesNotExist:
                            inscripciones_filtradas = inscripciones_curso
                    else:
                        inscripciones_filtradas = inscripciones_curso
                    
                    if buscar_alumno:
                        inscripciones_filtradas = inscripciones_filtradas.filter(
                            Q(estudiante__primer_nombre__icontains=buscar_alumno) |
                            Q(estudiante__apellido_paterno__icontains=buscar_alumno) |
                            Q(estudiante__apellido_materno__icontains=buscar_alumno) |
                            Q(estudiante__numero_documento__icontains=buscar_alumno) |
                            Q(estudiante__codigo_estudiante__icontains=buscar_alumno)
                        )
                    
                    calificaciones = Calificacion.objects.filter(
                        inscripcion__in=inscripciones_filtradas
                    ).select_related(
                        'inscripcion__estudiante', 
                        'inscripcion__grupo__asignatura'
                    ).order_by(
                        'inscripcion__estudiante__primer_nombre',
                        'inscripcion__estudiante__apellido_paterno',
                        'inscripcion__grupo__asignatura__nombre',
                        'fecha_evaluacion'
                    )
                    
                    puede_editar = False  # Como jefe solo puede ver
                    
                    # Calcular promedios
                    for inscripcion in inscripciones_filtradas:
                        estudiante = inscripcion.estudiante
                        if estudiante.id not in promedios_estudiantes:
                            notas_estudiante = Calificacion.objects.filter(
                                inscripcion__estudiante=estudiante,
                                inscripcion__in=inscripciones_curso
                            )
                            if asignatura_seleccionada:
                                notas_estudiante = notas_estudiante.filter(
                                    inscripcion__grupo__asignatura=asignatura_seleccionada
                                )
                            
                            promedio = notas_estudiante.aggregate(Avg('puntaje'))['puntaje__avg']
                            total_notas = notas_estudiante.count()
                            
                            promedios_estudiantes[estudiante.id] = {
                                'estudiante': estudiante,
                                'promedio': round(promedio, 1) if promedio else 0,
                                'total_notas': total_notas,
                                'estado': 'Aprobado' if promedio and promedio >= 4.0 else 'Reprobado'
                            }
                            
            messages.error(request, 'No tienes un perfil de estudiante asociado.')
            return redirect('inicio')
    
    else:
        messages.error(request, 'Tipo de usuario no válido para ver notas.')
        return redirect('inicio')
    
    # Calcular promedio por asignatura si hay calificaciones
    promedio_asignatura = None
    if calificaciones and asignatura_seleccionada:
        notas_asignatura = calificaciones.filter(
            inscripcion__grupo__asignatura=asignatura_seleccionada
        ) if not isinstance(calificaciones, list) else [
            cal for cal in calificaciones 
            if cal.inscripcion.grupo.asignatura == asignatura_seleccionada
        ]
        
        if notas_asignatura:
            if isinstance(notas_asignatura, list):
                suma_notas = sum(cal.puntaje for cal in notas_asignatura)
                promedio_asignatura = round(suma_notas / len(notas_asignatura), 1)
            else:
                promedio = notas_asignatura.aggregate(Avg('puntaje'))['puntaje__avg']
                promedio_asignatura = round(promedio, 1) if promedio else 0

    context = {
        'cursos_disponibles': cursos_disponibles,
        'curso_seleccionado': curso_seleccionado,
        'asignaturas_curso': asignaturas_curso,
        'asignatura_seleccionada': asignatura_seleccionada,
        'asignaturas_disponibles': asignaturas_disponibles,
        'calificaciones': calificaciones,
        'user_type': user_type.tipo_usuario,
        'puede_editar': puede_editar,
        'total_calificaciones': calificaciones.count() if calificaciones else 0,
        'buscar_alumno': buscar_alumno,
        'promedios_estudiantes': promedios_estudiantes,
        'promedio_asignatura': promedio_asignatura
    }
    return render(request, 'ver_notas_curso.html', context)

@login_required
def agregar_evento(request):
    """Vista para agregar un nuevo evento al calendario"""
    from django.utils import timezone
    from django.db.models import Q
    
    # Determinar tipo de usuario y permisos
    user_type = 'otro'
    puede_crear_eventos = False
    
    # Lógica mejorada para detectar tipo de usuario
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

# ...existing code...