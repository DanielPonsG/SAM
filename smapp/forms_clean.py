from django import forms
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura, Inscripcion, Calificacion, Grupo, PeriodoAcademico, AsistenciaAlumno, AsistenciaProfesor
from datetime import date, timedelta
from django.utils import timezone

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
                'placeholder': '12345678-9',
                'maxlength': '12',
                'pattern': '[0-9]{1,2}[0-9]{3}[0-9]{3}-[0-9kK]{1}'
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
                raise forms.ValidationError('RUT inválido. Formato esperado: 12345678-9')
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
                'placeholder': '12345678-9',
                'maxlength': '12',
                'pattern': '[0-9]{1,2}[0-9]{3}[0-9]{3}-[0-9kK]{1}'
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
                raise forms.ValidationError('RUT inválido. Formato esperado: 12345678-9')
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
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'descripcion', 'fecha', 'prioridad']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

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
        fields = ['dia', 'hora_inicio', 'hora_fin', 'asignatura']

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesor_responsable']

class AsignaturaCompletaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesor_responsable']

class SeleccionCursoAlumnoForm(forms.Form):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label="Curso")
    asignatura = forms.ModelChoiceField(queryset=Asignatura.objects.none(), label="Asignatura", required=False)
    alumno = forms.ModelChoiceField(queryset=Estudiante.objects.none(), label="Alumno", required=False)

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nombre_evaluacion', 'puntaje', 'descripcion']

class AsistenciaAlumnoForm(forms.ModelForm):
    class Meta:
        model = AsistenciaAlumno
        fields = ['estudiante', 'asignatura', 'fecha', 'presente', 'observacion']

class AsistenciaProfesorForm(forms.ModelForm):
    class Meta:
        model = AsistenciaProfesor
        fields = ['profesor', 'asignatura', 'fecha', 'presente', 'observacion']
