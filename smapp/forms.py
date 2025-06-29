from django import forms
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura, Inscripcion, Calificacion, Grupo, PeriodoAcademico, AsistenciaAlumno, AsistenciaProfesor
from datetime import date, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

def validar_rut(rut):
    """Validar formato y dígito verificador del RUT chileno"""
    # Limpiar el RUT
    rut = rut.replace(".", "").replace("-", "").upper()
    
    if len(rut) < 2:
        return False
    
    # Separar número y dígito verificador
    numero = rut[:-1]
    dv = rut[-1]
    
    # Validar que el número contenga solo dígitos
    if not numero.isdigit():
        return False
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digit in reversed(numero):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    return dv == dv_calculado

def formatear_rut(rut):
    """Formatear RUT con puntos y guión"""
    # Limpiar el RUT
    rut = rut.replace(".", "").replace("-", "").upper()
    
    if len(rut) < 2:
        return rut
    
    # Separar número y dígito verificador
    numero = rut[:-1]
    dv = rut[-1]
    
    # Formatear con puntos
    numero_formateado = ""
    for i, digit in enumerate(reversed(numero)):
        if i > 0 and i % 3 == 0:
            numero_formateado = "." + numero_formateado
        numero_formateado = digit + numero_formateado
    
    return f"{numero_formateado}-{dv}"

def calcular_edad(fecha_nacimiento):
    """Calcular edad en años a partir de la fecha de nacimiento"""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if hoy.month < fecha_nacimiento.month or (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1
    
    return edad

class EstudianteForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese nombre de usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese contraseña'
        })
    )

    class Meta:
        model = Estudiante
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_estudiante'
        ]
        widgets = {
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            'segundo_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre (opcional)'
            }),
            'apellido_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido paterno'
            }),
            'apellido_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido materno (opcional)'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control rut-input',
                'placeholder': '20.589.644-9',
                'maxlength': '15',
                'pattern': '[0-9]{1,2}(\.[0-9]{3}){1,2}-[0-9kK]{1}'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'codigo_estudiante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EST001'
            })
        }
        labels = {
            'numero_documento': 'RUT',
            'codigo_estudiante': 'Código de Estudiante'
        }

    def clean_numero_documento(self):
        rut = self.cleaned_data.get('numero_documento')
        if rut:
            # Validar formato y dígito verificador del RUT
            if not validar_rut(rut):
                raise forms.ValidationError('RUT inválido. Formato esperado: 20.589.644-9')
            # Formatear correctamente
            rut = formatear_rut(rut)
        return rut

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            edad = calcular_edad(fecha_nacimiento)
            # Validar edad mínima (3 años) y máxima (25 años) para estudiantes
            if edad < 3:
                raise forms.ValidationError(
                    f"El estudiante debe tener al menos 3 años. Edad actual: {edad} años."
                )
            elif edad > 25:
                raise forms.ValidationError(
                    f"El estudiante no puede tener más de 25 años. Edad actual: {edad} años."
                )
                
        return fecha_nacimiento

class ProfesorForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese nombre de usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese contraseña'
        })
    )

    class Meta:
        model = Profesor
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_profesor', 'especialidad'
        ]
        widgets = {
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            'segundo_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre (opcional)'
            }),
            'apellido_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido paterno'
            }),
            'apellido_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido materno (opcional)'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control rut-input',
                'placeholder': '20.589.644-9',
                'maxlength': '15',
                'pattern': '[0-9]{1,2}(\.[0-9]{3}){1,2}-[0-9kK]{1}'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'codigo_profesor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PROF001'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Matemáticas, Historia, etc.'
            })
        }
        labels = {
            'numero_documento': 'RUT',
            'codigo_profesor': 'Código de Profesor'
        }

    def clean_numero_documento(self):
        rut = self.cleaned_data.get('numero_documento')
        if rut:
            # Validar formato y dígito verificador del RUT
            if not validar_rut(rut):
                raise forms.ValidationError('RUT inválido. Formato esperado: 20.589.644-9')
            # Formatear correctamente
            rut = formatear_rut(rut)
        return rut

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            edad = calcular_edad(fecha_nacimiento)
            # Validar edad mínima (22 años) y máxima (70 años) para profesores
            if edad < 22:
                raise forms.ValidationError(
                    f"El profesor debe tener al menos 22 años (título universitario). Edad actual: {edad} años."
                )
            elif edad > 70:
                raise forms.ValidationError(
                    f"El profesor no puede tener más de 70 años (edad de jubilación). Edad actual: {edad} años."
                )
            
            # Validar que la fecha no sea futura
            if fecha_nacimiento > date.today():
                raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
                
        return fecha_nacimiento

class EventoCalendarioForm(forms.ModelForm):
    # Campo para seleccionar cursos específicos
    cursos_especificos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'multiple': True,
            'size': '6'
        }),
        label='Cursos específicos',
        required=False,
        help_text='Selecciona los cursos que verán este evento (opcional si es para todos)'
    )
    
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'descripcion', 'fecha', 'hora_inicio', 'hora_fin', 
                 'tipo_evento', 'prioridad', 'para_todos_los_cursos']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del evento'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del evento'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tipo_evento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'para_todos_los_cursos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Configurar cursos disponibles según el tipo de usuario
            anio_actual = timezone.now().year
            
            if user.is_superuser or user.groups.filter(name='Director').exists():
                # Admin y Director ven todos los cursos
                cursos_disponibles = Curso.objects.filter(anio=anio_actual)
            elif hasattr(user, 'profesor'):
                # Profesores solo ven sus cursos (como jefe o con asignaturas)
                cursos_jefe = user.profesor.cursos_jefatura.filter(anio=anio_actual)
                cursos_asignaturas = Curso.objects.filter(
                    asignaturas__profesor_responsable=user.profesor,
                    anio=anio_actual
                )
                cursos_disponibles = (cursos_jefe | cursos_asignaturas).distinct()
            else:
                cursos_disponibles = Curso.objects.none()
            
            self.fields['cursos_especificos'].queryset = cursos_disponibles.order_by('nivel', 'paralelo')
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        para_todos = cleaned_data.get('para_todos_los_cursos')
        cursos_especificos = cleaned_data.get('cursos_especificos')
        
        # Validar fecha no sea en el pasado
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError(
                'La fecha del evento no puede ser en el pasado.'
            )
        
        # Validar horarios
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError(
                'La hora de inicio debe ser anterior a la hora de fin.'
            )
        
        # Validar asignación de cursos
        if not para_todos and not cursos_especificos:
            raise forms.ValidationError(
                'Debes seleccionar al menos un curso específico o marcar "Para todos los cursos".'
            )
        
        return cleaned_data
    
    def save(self, commit=True, user=None):
        evento = super().save(commit=False)
        
        if user:
            evento.creado_por = user
        
        if commit:
            evento.save()
            
            # Asignar cursos específicos si no es para todos
            if not evento.para_todos_los_cursos:
                cursos_especificos = self.cleaned_data.get('cursos_especificos', [])
                evento.cursos.set(cursos_especificos)
            else:
                evento.cursos.clear()
        
        return evento

class CursoForm(forms.ModelForm):
    # Campo para crear nueva asignatura directamente (opcional)
    nueva_asignatura = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opcional: Crear nueva asignatura'
        }),
        label='Nueva Asignatura',
        help_text='Si especificas una nueva asignatura, se creará automáticamente y se asignará al curso'
    )
    
    class Meta:
        model = Curso
        fields = ['nivel', 'paralelo', 'profesor_jefe', 'estudiantes', 'asignaturas']
        widgets = {
            'nivel': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'paralelo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'profesor_jefe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estudiantes': forms.SelectMultiple(attrs={
                'class': 'form-select curso-estudiantes',
                'size': '12',
                'style': 'height: 300px;'
            }),
            'asignaturas': forms.SelectMultiple(attrs={
                'class': 'form-select curso-asignaturas',
                'size': '8',
                'style': 'height: 200px;'
            })
        }
        labels = {
            'nivel': 'Nivel *',
            'paralelo': 'Paralelo *',
            'profesor_jefe': 'Profesor Jefe',
            'estudiantes': 'Estudiantes del Curso',
            'asignaturas': 'Asignaturas del Curso'
        }
        help_texts = {
            'estudiantes': 'Mantén presionado Ctrl (Cmd en Mac) para seleccionar múltiples estudiantes',
            'asignaturas': 'Mantén presionado Ctrl (Cmd en Mac) para seleccionar múltiples asignaturas'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar queryset para mostrar información más útil
        self.fields['profesor_jefe'].queryset = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
        self.fields['profesor_jefe'].empty_label = "-- Seleccionar Profesor Jefe (Opcional) --"
        
        # Filtrar estudiantes para mostrar solo los que NO están asignados a ningún curso del año actual
        anio_actual = timezone.now().year
        
        # Obtener IDs de estudiantes que ya están en algún curso del año actual
        # Usando la relación ManyToMany correctamente
        cursos_actuales = Curso.objects.filter(anio=anio_actual)
        
        # Si estamos editando un curso existente, excluirlo del filtro
        if self.instance and self.instance.pk:
            cursos_actuales = cursos_actuales.exclude(pk=self.instance.pk)
        
        # Obtener todos los estudiantes asignados a estos cursos
        estudiantes_asignados_ids = []
        for curso in cursos_actuales:
            estudiantes_curso = list(curso.estudiantes.values_list('id', flat=True))
            estudiantes_asignados_ids.extend(estudiantes_curso)
        
        # Convertir a set para eliminar duplicados
        estudiantes_asignados_ids = set(estudiantes_asignados_ids)
        
        # Filtrar estudiantes disponibles (no asignados)
        estudiantes_disponibles = Estudiante.objects.exclude(
            id__in=estudiantes_asignados_ids
        ).order_by('primer_nombre', 'apellido_paterno')
        
        # Si estamos editando un curso existente, incluir también sus estudiantes actuales
        if self.instance and self.instance.pk:
            estudiantes_del_curso = self.instance.estudiantes.all()
            estudiantes_disponibles = (estudiantes_disponibles | estudiantes_del_curso).distinct().order_by('primer_nombre', 'apellido_paterno')
        
        self.fields['estudiantes'].queryset = estudiantes_disponibles
        self.fields['asignaturas'].queryset = Asignatura.objects.all().order_by('nombre')
        
        # Hacer que ciertos campos no sean requeridos
        self.fields['profesor_jefe'].required = False
        self.fields['estudiantes'].required = False
        self.fields['asignaturas'].required = False
        
        # Campos requeridos
        self.fields['nivel'].required = True
        self.fields['paralelo'].required = True

    def clean(self):
        cleaned_data = super().clean()
        nivel = cleaned_data.get('nivel')
        paralelo = cleaned_data.get('paralelo')
        estudiantes = cleaned_data.get('estudiantes')
        anio_actual = timezone.now().year
        
        if nivel and paralelo:
            # Verificar que no exista otro curso con la misma combinación en el año actual
            existing_curso = Curso.objects.filter(
                nivel=nivel,
                paralelo=paralelo,
                anio=anio_actual
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_curso.exists():
                raise forms.ValidationError(
                    f'Ya existe un curso {dict(Curso.NIVELES)[nivel]}{paralelo} para el año {anio_actual}. '
                    'Cada curso debe tener una combinación única de nivel y paralelo.'
                )
        
        # Validación adicional por seguridad (aunque el formulario ya filtra estudiantes disponibles)
        if estudiantes:
            estudiantes_con_curso = []
            for estudiante in estudiantes:
                # Buscar si el estudiante ya está en otro curso del año actual
                cursos_existentes = Curso.objects.filter(
                    estudiantes=estudiante,
                    anio=anio_actual
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if cursos_existentes.exists():
                    curso_actual = cursos_existentes.first()
                    estudiantes_con_curso.append(
                        f'{estudiante.primer_nombre} {estudiante.apellido_paterno} '
                        f'(ya está en {curso_actual.get_nivel_display()}{curso_actual.paralelo})'
                    )
            
            if estudiantes_con_curso:
                # Esto no debería suceder si el formulario está funcionando correctamente
                error_msg = 'Error interno: Se seleccionaron estudiantes ya asignados. Por favor, recarga la página e intenta nuevamente.'
                raise forms.ValidationError(error_msg)
        
        return cleaned_data
    
    def clean_nueva_asignatura(self):
        nueva_asignatura = self.cleaned_data.get('nueva_asignatura')
        if nueva_asignatura:
            nueva_asignatura = nueva_asignatura.strip()
            # Verificar que no exista ya una asignatura con ese nombre
            if Asignatura.objects.filter(nombre__iexact=nueva_asignatura).exists():
                raise forms.ValidationError('Ya existe una asignatura con este nombre. Selecciónala de la lista en lugar de crear una nueva.')
        return nueva_asignatura
    
    def save(self, commit=True):
        curso = super().save(commit=commit)
        
        if commit:
            # Crear nueva asignatura si se especificó
            nueva_asignatura_nombre = self.cleaned_data.get('nueva_asignatura')
            if nueva_asignatura_nombre:
                # Generar código automático para la nueva asignatura
                import re
                codigo_base = re.sub(r'[^A-Z0-9]', '', nueva_asignatura_nombre.upper())[:6]
                contador = 1
                codigo_asignatura = f"{codigo_base}{contador:02d}"
                
                # Asegurar que el código sea único
                while Asignatura.objects.filter(codigo_asignatura=codigo_asignatura).exists():
                    contador += 1
                    codigo_asignatura = f"{codigo_base}{contador:02d}"
                
                # Crear la nueva asignatura
                nueva_asignatura = Asignatura.objects.create(
                    nombre=nueva_asignatura_nombre,
                    codigo_asignatura=codigo_asignatura,
                    descripcion=f"Asignatura creada desde el curso {curso}",
                    profesor_responsable=curso.profesor_jefe
                )
                
                # Agregar la nueva asignatura al curso
                curso.asignaturas.add(nueva_asignatura)
        
        return curso

# Formularios básicos adicionales
class HorarioCursoForm(forms.ModelForm):
    class Meta:
        model = HorarioCurso
        fields = ['dia', 'hora_inicio', 'hora_fin', 'tipo_periodo', 'asignatura', 'profesor', 'observaciones']
        widgets = {
            'dia': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time',
                'required': True
            }),
            'tipo_periodo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'asignatura': forms.Select(attrs={
                'class': 'form-control'
            }),
            'profesor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones opcionales...'
            })
        }
        labels = {
            'dia': 'Día de la semana',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin',
            'tipo_periodo': 'Tipo de período',
            'asignatura': 'Asignatura',
            'profesor': 'Profesor responsable',
            'observaciones': 'Observaciones'
        }
    
    def __init__(self, *args, **kwargs):
        self.curso = kwargs.pop('curso', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset de asignaturas según el curso
        if self.curso:
            self.fields['asignatura'].queryset = self.curso.asignaturas.all()
            self.fields['asignatura'].empty_label = "Seleccionar asignatura..."
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.all()
        
        # Configurar profesores disponibles
        self.fields['profesor'].queryset = Profesor.objects.all()
        self.fields['profesor'].empty_label = "Seleccionar profesor..."
        
        # Configurar campos según el tipo de período
        if self.instance and self.instance.pk:
            if self.instance.tipo_periodo in ['recreo', 'almuerzo']:
                self.fields['asignatura'].required = False
                self.fields['profesor'].required = False
                self.fields['asignatura'].widget.attrs['disabled'] = True
                self.fields['profesor'].widget.attrs['disabled'] = True
        
        # Añadir help text
        self.fields['tipo_periodo'].help_text = "Selecciona 'Clase' para períodos académicos, 'Recreo' o 'Almuerzo' para descansos"
        self.fields['asignatura'].help_text = "Solo requerido para períodos de clase"
        self.fields['profesor'].help_text = "El profesor debe estar asignado a la asignatura seleccionada"
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_periodo = cleaned_data.get('tipo_periodo')
        asignatura = cleaned_data.get('asignatura')
        profesor = cleaned_data.get('profesor')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        dia = cleaned_data.get('dia')
        
        # Validar horas
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise forms.ValidationError("La hora de inicio debe ser menor que la hora de fin")
        
        # Validaciones según tipo de período
        if tipo_periodo == 'clase':
            if not asignatura:
                raise forms.ValidationError("Para períodos de clase, la asignatura es obligatoria")
            
            # Validar que el profesor puede enseñar la asignatura
            if profesor and asignatura:
                profesores_asignatura = asignatura.get_todos_los_profesores()
                if profesor not in profesores_asignatura:
                    raise forms.ValidationError(
                        f"El profesor {profesor.primer_nombre} {profesor.apellido_paterno} "
                        f"no está asignado a la asignatura {asignatura.nombre}"
                    )
        
        elif tipo_periodo in ['recreo', 'almuerzo']:
            if asignatura:
                cleaned_data['asignatura'] = None
            if profesor:
                cleaned_data['profesor'] = None
        
        # Crear instancia temporal para validaciones
        if self.curso and dia and hora_inicio and hora_fin:
            horario_temp = HorarioCurso(
                curso=self.curso,
                dia=dia,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                tipo_periodo=tipo_periodo,
                asignatura=asignatura,
                profesor=profesor
            )
            
            if self.instance and self.instance.pk:
                horario_temp.pk = self.instance.pk
            
            try:
                horario_temp.clean()
            except ValidationError as e:
                raise forms.ValidationError(f"Error de validación: {e.message}")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.curso:
            instance.curso = self.curso
        
        if commit:
            instance.save()
        return instance

class HorarioRapidoForm(forms.Form):
    """Formulario para asignación rápida de horarios"""
    
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Asignatura',
        help_text='Selecciona la asignatura para este período'
    )
    
    profesor = forms.ModelChoiceField(
        queryset=Profesor.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Profesor',
        empty_label="Seleccionar profesor..."
    )
    
    def __init__(self, *args, **kwargs):
        self.curso = kwargs.pop('curso', None)
        self.horario = kwargs.pop('horario', None)
        super().__init__(*args, **kwargs)
        
        if self.curso:
            # Solo asignaturas del curso
            self.fields['asignatura'].queryset = self.curso.asignaturas.all()
            
        if self.horario and self.horario.asignatura:
            # Solo profesores de la asignatura
            self.fields['profesor'].queryset = self.horario.asignatura.get_todos_los_profesores()
            
            # Filtrar profesores disponibles en este horario
            profesores_disponibles = []
            for profesor in self.fields['profesor'].queryset:
                horario_temp = HorarioCurso(
                    curso=self.curso,
                    profesor=profesor,
                    dia=self.horario.dia,
                    hora_inicio=self.horario.hora_inicio,
                    hora_fin=self.horario.hora_fin,
                    tipo_periodo='clase'
                )
                horario_temp.pk = self.horario.pk  # Para excluir este horario de la validación
                
                if not horario_temp.verificar_conflictos_profesor():
                    profesores_disponibles.append(profesor.id)
            
            self.fields['profesor'].queryset = self.fields['profesor'].queryset.filter(id__in=profesores_disponibles)
        else:
            self.fields['profesor'].queryset = Profesor.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        asignatura = cleaned_data.get('asignatura')
        profesor = cleaned_data.get('profesor')
        
        if asignatura and profesor:
            # Verificar que el profesor puede enseñar la asignatura
            profesores_asignatura = asignatura.get_todos_los_profesores()
            if profesor not in profesores_asignatura:
                raise forms.ValidationError(
                    f"El profesor {profesor.primer_nombre} {profesor.apellido_paterno} "
                    f"no está asignado a la asignatura {asignatura.nombre}"
                )
        
        return cleaned_data

class CalificacionForm(forms.ModelForm):
    """Formulario para editar calificaciones"""
    
    class Meta:
        model = Calificacion
        fields = ['nombre_evaluacion', 'puntaje', 'porcentaje', 'detalle', 'descripcion']
        widgets = {
            'nombre_evaluacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Prueba 1, Tarea 2, etc.'
            }),
            'puntaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1.0',
                'max': '7.0',
                'step': '0.1',
                'placeholder': '1.0 - 7.0'
            }),
            'porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': '0 - 100'
            }),
            'detalle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Excelente, Bueno, Regular, etc.'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción adicional (opcional)'
            })
        }
        labels = {
            'nombre_evaluacion': 'Nombre de la Evaluación',
            'puntaje': 'Puntaje (1.0 - 7.0)',
            'porcentaje': 'Porcentaje (%)',
            'detalle': 'Detalle/Observación',
            'descripcion': 'Descripción Adicional'
        }
        help_texts = {
            'puntaje': 'Ingresa una nota entre 1.0 y 7.0 según el sistema chileno',
            'porcentaje': 'Porcentaje de logro (opcional)',
            'detalle': 'Observación breve sobre el desempeño',
            'descripcion': 'Información adicional sobre la evaluación'
        }
    
    def clean_puntaje(self):
        puntaje = self.cleaned_data.get('puntaje')
        if puntaje is not None:
            if puntaje < 1.0 or puntaje > 7.0:
                raise forms.ValidationError('El puntaje debe estar entre 1.0 y 7.0')
        return puntaje
    
    def clean_porcentaje(self):
        porcentaje = self.cleaned_data.get('porcentaje')
        if porcentaje is not None:
            if porcentaje < 0 or porcentaje > 100:
                raise forms.ValidationError('El porcentaje debe estar entre 0 y 100')
        return porcentaje

class AsistenciaAlumnoForm(forms.ModelForm):
    """Formulario mejorado para asistencia de alumnos"""
    
    class Meta:
        model = AsistenciaAlumno
        fields = ['estudiante', 'curso', 'asignatura', 'profesor_registro', 
                 'presente', 'observacion', 'justificacion']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'asignatura': forms.Select(attrs={'class': 'form-select'}),
            'profesor_registro': forms.Select(attrs={'class': 'form-select'}),
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observaciones sobre la asistencia'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Justificación en caso de ausencia'})
        }
        labels = {
            'estudiante': 'Estudiante',
            'curso': 'Curso',
            'asignatura': 'Asignatura',
            'profesor_registro': 'Profesor que registra',
            'presente': 'Presente',
            'observacion': 'Observación',
            'justificacion': 'Justificación'
        }

    def __init__(self, *args, **kwargs):
        curso_id = kwargs.pop('curso_id', None)
        profesor_id = kwargs.pop('profesor_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar estudiantes por curso si se proporciona
        if curso_id:
            try:
                curso = Curso.objects.get(id=curso_id)
                self.fields['estudiante'].queryset = curso.estudiantes.all().order_by('primer_nombre', 'apellido_paterno')
                self.fields['curso'].queryset = Curso.objects.filter(id=curso_id)
                self.fields['asignatura'].queryset = curso.asignaturas.all().order_by('nombre')
            except Curso.DoesNotExist:
                pass
        
        # Establecer profesor por defecto si se proporciona
        if profesor_id:
            try:
                profesor = Profesor.objects.get(id=profesor_id)
                self.fields['profesor_registro'].queryset = Profesor.objects.filter(id=profesor_id)
                # Filtrar asignaturas del profesor
                asignaturas_profesor = profesor.asignaturas_responsable.all()
                if hasattr(profesor, 'profesor_responsable'):
                    asignaturas_profesor = asignaturas_profesor | Asignatura.objects.filter(profesor_responsable=profesor)
                self.fields['asignatura'].queryset = asignaturas_profesor.distinct().order_by('nombre')
            except Profesor.DoesNotExist:
                pass

class AsistenciaProfesorForm(forms.ModelForm):
    """Formulario mejorado para asistencia de profesores"""
    
    class Meta:
        model = AsistenciaProfesor
        fields = ['profesor', 'asignatura', 'curso', 
                 'presente', 'observacion', 'justificacion']
        widgets = {
            'profesor': forms.Select(attrs={'class': 'form-select'}),
            'asignatura': forms.Select(attrs={'class': 'form-select'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'presente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observaciones sobre la asistencia'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Justificación en caso de ausencia'})
        }
        labels = {
            'profesor': 'Profesor',
            'asignatura': 'Asignatura (opcional)',
            'curso': 'Curso (opcional)',
            'presente': 'Presente',
            'observacion': 'Observación',
            'justificacion': 'Justificación'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos opcionales
        self.fields['asignatura'].required = False
        self.fields['curso'].required = False
        self.fields['justificacion'].required = False
        
        # Ordenar opciones
        self.fields['profesor'].queryset = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
        self.fields['asignatura'].queryset = Asignatura.objects.all().order_by('nombre')
        self.fields['curso'].queryset = Curso.objects.all().order_by('nivel', 'paralelo')

# Formulario específico para registro masivo de asistencia de alumnos
class RegistroMasivoAsistenciaForm(forms.Form):
    """Formulario simplificado para registro masivo de asistencia solo por curso"""
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Curso',
        help_text='Selecciona el curso para registrar asistencia'
    )

    def __init__(self, *args, **kwargs):
        cursos_disponibles = kwargs.pop('cursos_disponibles', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar cursos disponibles según permisos del usuario
        if cursos_disponibles is not None:
            self.fields['curso'].queryset = cursos_disponibles
        else:
            self.fields['curso'].queryset = Curso.objects.all().order_by('nivel', 'paralelo')

class AsignaturaForm(forms.ModelForm):
    """Formulario para crear y editar asignaturas con múltiples profesores"""
    
    profesores_responsables = forms.ModelMultipleChoiceField(
        queryset=Profesor.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control chosen-select',
            'multiple': True,
            'size': '6'
        }),
        required=False,
        label='Profesores Responsables',
        help_text='Mantén presionada Ctrl para seleccionar múltiples profesores'
    )
    
    # Agregar campo de cursos que faltaba
    cursos = forms.ModelMultipleChoiceField(
        queryset=None,  # Se configurará en __init__
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control chosen-select',
            'multiple': True,
            'size': '6'
        }),
        required=False,
        label='Cursos Asignados',
        help_text='Mantén presionada Ctrl para seleccionar múltiples cursos'
    )
    
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesores_responsables', 'cursos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Matemáticas Aplicadas'
            }),
            'codigo_asignatura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MAT-01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la asignatura (opcional)'
            })
        }
        labels = {
            'nombre': 'Nombre de la Asignatura',
            'codigo_asignatura': 'Código de Asignatura',
            'descripcion': 'Descripción'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar profesores disponibles
        self.fields['profesores_responsables'].queryset = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
        
        # Configurar cursos disponibles
        from .models import Curso
        self.fields['cursos'].queryset = Curso.objects.all().order_by('nivel', 'paralelo')
        
        # Si estamos editando, preseleccionar los profesores y cursos actuales
        if self.instance and self.instance.pk:
            self.initial['profesores_responsables'] = self.instance.profesores_responsables.all()
            self.initial['cursos'] = self.instance.cursos.all()
    
    def clean_codigo_asignatura(self):
        codigo = self.cleaned_data.get('codigo_asignatura', '').strip().upper()
        
        if not codigo:
            raise forms.ValidationError("El código de asignatura es obligatorio")
        
        # Verificar unicidad
        queryset = Asignatura.objects.filter(codigo_asignatura=codigo)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError(f"Ya existe una asignatura con el código '{codigo}'")
        
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        
        if not nombre:
            raise forms.ValidationError("El nombre de la asignatura es obligatorio")
        
        # Verificar que no exista otra asignatura con el mismo nombre
        queryset = Asignatura.objects.filter(nombre__iexact=nombre)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError(
                f'Ya existe una asignatura con el nombre "{nombre}". '
                'Por favor, usa un nombre diferente.'
            )
        return nombre
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        if commit:
            # Limpiar profesores anteriores de la relación inversa
            for profesor in Profesor.objects.filter(asignaturas=instance):
                profesor.asignaturas.remove(instance)
            
            # Guardar las relaciones many-to-many
            instance.profesores_responsables.set(self.cleaned_data['profesores_responsables'])
            instance.cursos.set(self.cleaned_data['cursos'])
            
            # También agregar las asignaturas a los profesores
            for profesor in self.cleaned_data['profesores_responsables']:
                profesor.asignaturas.add(instance)
        
        return instance

class AsignaturaCompletaForm(forms.ModelForm):
    # Campo para seleccionar cursos
    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'multiple': True,
            'size': '5'
        }),
        label='Cursos asignados',
        required=False,
        help_text='Mantén presionada Ctrl (o Cmd en Mac) para seleccionar varios cursos'
    )
    
    # Campo para días de la semana
    DIAS_CHOICES = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
        ('SA', 'Sábado'),
        ('DO', 'Domingo'),
    ]
    
    dias = forms.MultipleChoiceField(
        choices=DIAS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Días de la semana',
        required=False
    )
    
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesores_responsables', 'cursos', 'dias']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Matemáticas Aplicadas'
            }),
            'codigo_asignatura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MAT-01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la asignatura'
            }),
            'profesores_responsables': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre de la Asignatura',
            'codigo_asignatura': 'Código de Asignatura',
            'descripcion': 'Descripción',
            'profesores_responsables': 'Profesores Responsables'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar querysets
        self.fields['cursos'].queryset = Curso.objects.all().order_by('nivel', 'paralelo')
        self.fields['profesores_responsables'].queryset = Profesor.objects.all().order_by('primer_nombre', 'apellido_paterno')
        
        # Si estamos editando, precargar datos
        if self.instance and self.instance.pk:
            self.initial['cursos'] = self.instance.cursos.all()
            self.initial['profesores_responsables'] = self.instance.profesores_responsables.all()
    
    def clean_codigo_asignatura(self):
        codigo = self.cleaned_data.get('codigo_asignatura', '').strip().upper()
        
        if not codigo:
            raise forms.ValidationError("El código de asignatura es obligatorio")
        
        # Verificar unicidad
        queryset = Asignatura.objects.filter(codigo_asignatura=codigo)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError(f"Ya existe una asignatura con el código '{codigo}'")
        
        return codigo
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        
        if not nombre:
            raise forms.ValidationError("El nombre de la asignatura es obligatorio")
        
        # Verificar que no exista otra asignatura con el mismo nombre
        queryset = Asignatura.objects.filter(nombre__iexact=nombre)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError(
                f'Ya existe una asignatura con el nombre "{nombre}". '
                'Por favor, usa un nombre diferente.'
            )
        return nombre
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        if commit:
            # Guardar las relaciones many-to-many
            instance.profesores_responsables.set(self.cleaned_data['profesores_responsables'])
            instance.cursos.set(self.cleaned_data['cursos'])
            
            # Sincronizar relaciones inversas con profesores
            for profesor in Profesor.objects.filter(asignaturas=instance):
                profesor.asignaturas.remove(instance)
            
            for profesor in self.cleaned_data['profesores_responsables']:
                profesor.asignaturas.add(instance)
        
        return instance

class SeleccionCursoAlumnoForm(forms.Form):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label="Curso")
    asignatura = forms.ModelChoiceField(queryset=Asignatura.objects.none(), label="Asignatura", required=False)
    alumno = forms.ModelChoiceField(queryset=Estudiante.objects.none(), label="Alumno", required=False)

class AsignarEstudianteForm(forms.Form):
    """Formulario para asignar estudiantes pendientes a cursos"""
    
    estudiante = forms.ModelChoiceField(
        queryset=Estudiante.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Estudiante',
        help_text='Selecciona el estudiante a asignar'
    )
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Curso',
        help_text='Selecciona el curso de destino'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        
        # Solo estudiantes sin curso asignado en el año actual
        cursos_queryset = Curso.objects.filter(anio=timezone.now().year)
        estudiantes_asignados_ids = set()
        for curso in cursos_queryset:
            estudiantes_curso = list(curso.estudiantes.values_list('id', flat=True))
            estudiantes_asignados_ids.update(estudiantes_curso)
        
        self.fields['estudiante'].queryset = Estudiante.objects.exclude(
            id__in=estudiantes_asignados_ids
        ).order_by('primer_nombre', 'apellido_paterno')
        
        # Solo cursos del año actual
        self.fields['curso'].queryset = cursos_queryset.order_by('nivel', 'paralelo')
    
    def clean(self):
        cleaned_data = super().clean()
        estudiante = cleaned_data.get('estudiante')
        curso = cleaned_data.get('curso')
        
        if estudiante and curso:
            # Verificar que el estudiante no esté ya asignado al curso
            if curso.estudiantes.filter(id=estudiante.id).exists():
                raise ValidationError(
                    f'El estudiante {estudiante.primer_nombre} {estudiante.apellido_paterno} '
                    f'ya está asignado al curso {curso.get_nivel_display()}{curso.paralelo}.',
                    code='estudiante_ya_asignado'
                )
        
        return cleaned_data
