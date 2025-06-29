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
from django.utils import timezone
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
    
    return render(request, 'listar_profesores.html', {
        'profesores': profesores,
        'filtro_profesor': filtro_profesor,
        'total_profesores': total_profesores,
        'profesores_activos': profesores_activos,
        'profesores_con_asignaturas': profesores_con_asignaturas,
    })

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
                login(request, user)
                return redirect('index_master')
            else:
                mensaje = "Credenciales inválidas"
        else:
            mensaje = "Por favor ingresa usuario y contraseña"
    
    return render(request, 'login.html', {'mensaje': mensaje})

def logout_view(request):
    """Vista de logout personalizada"""
    logout(request)
    return redirect('login')

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
