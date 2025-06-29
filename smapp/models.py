from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Persona(models.Model):
    """
    Clase base abstracta para reusar campos comunes entre Estudiantes, Profesores, etc.
    No se creará una tabla para esta clase en la base de datos, solo sus herederos.
    """
    TIPOS_DOCUMENTO = [
        ('RUT', 'RUT (Rol Único Tributario)'),
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('PA', 'Pasaporte'),
        ('CE', 'Cédula de Extranjería'),
    ]

    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO, default='RUT')
    numero_documento = models.CharField(max_length=15, unique=True, verbose_name="RUT")  # Aumentado para RUTs con puntos
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        abstract = True # Indica que esta es una clase abstracta

    def __str__(self):
        return f"{self.primer_nombre} {self.apellido_paterno}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo de la persona"""
        if self.segundo_nombre and self.apellido_materno:
            return f"{self.primer_nombre} {self.segundo_nombre} {self.apellido_paterno} {self.apellido_materno}"
        elif self.segundo_nombre:
            return f"{self.primer_nombre} {self.segundo_nombre} {self.apellido_paterno}"
        elif self.apellido_materno:
            return f"{self.primer_nombre} {self.apellido_paterno} {self.apellido_materno}"
        else:
            return f"{self.primer_nombre} {self.apellido_paterno}"
    
    @property
    def edad(self):
        """Calcula la edad actual de la persona"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

class Estudiante(Persona):
    """
    Modelo para los estudiantes. Hereda de Persona.
    """
    codigo_estudiante = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True) # Se establece automáticamente al crear
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.codigo_estudiante} - {self.primer_nombre} {self.apellido_paterno}"
    
    def get_curso_actual(self):
        """Retorna el curso actual del estudiante (del año actual)"""
        from datetime import date
        return self.cursos.filter(anio=date.today().year).first()
    
    @property
    def nombre_completo(self):
        """Alias para get_nombre_completo()"""
        return self.get_nombre_completo()

class Profesor(Persona):
    """
    Modelo para los profesores. Hereda de Persona.
    """
    codigo_profesor = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    fecha_contratacion = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    asignaturas = models.ManyToManyField('Asignatura', related_name='profesores', blank=True)

    def __str__(self):
        return f"{self.codigo_profesor} - {self.primer_nombre} {self.apellido_paterno}"
    
    def get_cursos_jefatura(self):
        """Retorna los cursos donde este profesor es jefe"""
        return self.cursos_jefatura.all()
    
    def get_asignaturas_responsable(self):
        """Retorna las asignaturas donde este profesor es responsable"""
        return self.asignaturas_responsable.all()
    
    @property
    def nombre_completo(self):
        """Alias para get_nombre_completo()"""
        return self.get_nombre_completo()

class Curso(models.Model):
    """
    Modelo para los cursos escolares chilenos - Sistema completo: 1° a 8° Básico y 1° a 4° Medio
    """
    NIVELES = [
        # Educación Básica
        ('1B', '1° Básico'),
        ('2B', '2° Básico'),
        ('3B', '3° Básico'),
        ('4B', '4° Básico'),
        ('5B', '5° Básico'),
        ('6B', '6° Básico'),
        ('7B', '7° Básico'),
        ('8B', '8° Básico'),
        # Educación Media
        ('1M', '1° Medio'),
        ('2M', '2° Medio'),
        ('3M', '3° Medio'),
        ('4M', '4° Medio'),
    ]
    
    PARALELOS = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
    ]
    
    nivel = models.CharField(max_length=2, choices=NIVELES, verbose_name="Nivel", default='1M')
    paralelo = models.CharField(max_length=1, choices=PARALELOS, verbose_name="Paralelo", default='A')
    anio = models.IntegerField(default=timezone.now().year, verbose_name="Año", editable=False)
    profesor_jefe = models.ForeignKey('Profesor', on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos_jefatura', verbose_name="Profesor Jefe")
    estudiantes = models.ManyToManyField('Estudiante', blank=True, related_name='cursos')
    asignaturas = models.ManyToManyField('Asignatura', blank=True, related_name='cursos')

    class Meta:
        unique_together = ('nivel', 'paralelo', 'anio')
        ordering = ['anio', 'nivel', 'paralelo']
    
    @property
    def orden_nivel(self):
        """Retorna un número para ordenar correctamente básica antes que media"""
        if self.nivel.endswith('B'):  # Básico
            return int(self.nivel[0])  # 1B -> 1, 2B -> 2, etc.
        else:  # Medio
            return 10 + int(self.nivel[0])  # 1M -> 11, 2M -> 12, etc.

    @property
    def nombre(self):
        return f"{self.get_nivel_display()}{self.paralelo}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del curso"""
        return f"{self.get_nivel_display()}{self.paralelo}"
    
    def clean(self):
        """Validación personalizada del modelo"""
        from django.core.exceptions import ValidationError
        super().clean()
        
    def add_estudiante(self, estudiante):
        """Método seguro para agregar un estudiante al curso"""
        from django.core.exceptions import ValidationError
        
        # Verificar si el estudiante ya está en otro curso del mismo año
        cursos_existentes = Curso.objects.filter(
            estudiantes=estudiante,
            anio=self.anio
        ).exclude(id=self.id)
        
        if cursos_existentes.exists():
            curso_actual = cursos_existentes.first()
            raise ValidationError(
                f'El estudiante {estudiante} ya está asignado al curso {curso_actual} '
                f'para el año {self.anio}. Un estudiante solo puede estar en un curso por año.'
            )
        
        self.estudiantes.add(estudiante)
    
    def __str__(self):
        return f"{self.get_nivel_display()}{self.paralelo} ({self.anio})"
    
    def get_total_estudiantes(self):
        """Retorna el número total de estudiantes en el curso"""
        return self.estudiantes.count()
    
    def get_horarios_por_dia(self, dia=None):
        """Retorna los horarios del curso, opcionalmente filtrados por día"""
        if dia:
            return self.horarios.filter(dia=dia).order_by('hora_inicio')
        return self.horarios.all().order_by('dia', 'hora_inicio')
    
    def tiene_conflicto_horario(self, dia, hora_inicio, hora_fin, excluir_horario=None):
        """Verifica si hay conflicto de horarios en el curso"""
        horarios = self.horarios.filter(dia=dia)
        if excluir_horario:
            horarios = horarios.exclude(id=excluir_horario.id)
        
        for horario in horarios:
            # Verificar solapamiento de horarios
            if not (hora_fin <= horario.hora_inicio or hora_inicio >= horario.hora_fin):
                return True
        return False

class Asignatura(models.Model):
    """
    Modelo para las asignaturas o materias que componen un curso.
    Un Curso puede tener varias Asignaturas (ej. Matemáticas: Álgebra, Geometría).
    O bien, Asignatura puede ser el nivel más bajo (Matemáticas I, Matemáticas II).
    Si tu escuela tiene "materias" que no son lo mismo que un "curso" general.
    Si no, puedes simplificar y usar solo 'Curso' como la materia a impartir.
    Por simplicidad, vamos a usar 'Asignatura' como la materia que se imparte en un 'Grupo'.
    """
    nombre = models.CharField(max_length=100)
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    # Cambiado a ManyToMany para permitir múltiples profesores responsables
    profesores_responsables = models.ManyToManyField(
        'Profesor',
        blank=True,
        related_name='asignaturas_responsable'
    )
    # Mantener campo original para compatibilidad hacia atrás (deprecado)
    profesor_responsable = models.ForeignKey(
        'Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asignaturas_responsable_old',
        help_text='Campo deprecado - usar profesores_responsables'
    )

    def __str__(self):
        return self.nombre
    
    def get_cursos_asignados(self):
        """Retorna todos los cursos donde está asignada esta asignatura"""
        return self.cursos.all()
    
    def get_cursos_nombres(self):
        """Retorna los nombres de los cursos donde está asignada esta asignatura"""
        cursos = self.get_cursos_asignados()
        if cursos.exists():
            return ", ".join([str(curso) for curso in cursos])
        return "Sin cursos asignados"
    
    def tiene_cursos(self):
        """Verifica si la asignatura está asignada a algún curso"""
        return self.cursos.exists()
    
    def get_info_completa(self):
        """Retorna información completa de la asignatura"""
        return {
            'nombre': self.nombre,
            'codigo': self.codigo_asignatura,
            'profesores': self.get_profesores_nombres(),
            'cursos': self.get_cursos_nombres(),
            'tiene_profesores': self.tiene_profesores(),
            'tiene_cursos': self.tiene_cursos(),
        }
    
    def get_horarios_totales(self):
        """Retorna el total de horarios programados para esta asignatura"""
        return self.horarios.count()
    
    def get_profesores_nombres(self):
        """Retorna los nombres de todos los profesores responsables"""
        profesores = self.profesores_responsables.all()
        if profesores.exists():
            return ", ".join([prof.get_nombre_completo() for prof in profesores])
        # Fallback al campo antiguo si existe
        if self.profesor_responsable:
            return self.profesor_responsable.get_nombre_completo()
        return "Sin profesores asignados"
    
    def get_profesor_nombre_completo(self):
        """Método para compatibilidad hacia atrás"""
        return self.get_profesores_nombres()
    
    def tiene_profesores(self):
        """Verifica si la asignatura tiene profesores asignados"""
        return self.profesores_responsables.exists() or self.profesor_responsable is not None
    
    def agregar_profesor(self, profesor):
        """Agrega un profesor a la asignatura"""
        self.profesores_responsables.add(profesor)
        # También agregar a las asignaturas del profesor
        profesor.asignaturas.add(self)
    
    def remover_profesor(self, profesor):
        """Remueve un profesor de la asignatura"""
        self.profesores_responsables.remove(profesor)
        # También remover de las asignaturas del profesor
        profesor.asignaturas.remove(self)
    
    def get_todos_los_profesores(self):
        """Retorna todos los profesores asignados (tanto del campo nuevo como del antiguo)"""
        profesores = list(self.profesores_responsables.all())
        # Agregar el profesor del campo antiguo si existe y no está ya en la lista
        if self.profesor_responsable and self.profesor_responsable not in profesores:
            profesores.append(self.profesor_responsable)
        return profesores
    
    def get_profesores_display(self):
        """Retorna una lista de profesores para mostrar en templates"""
        return self.get_todos_los_profesores()

class Salon(models.Model):
    """
    Modelo para los salones o aulas donde se imparten las clases.
    """
    numero_salon = models.CharField(max_length=10, unique=True)
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Salón {self.numero_salon}"

class PeriodoAcademico(models.Model):
    """
    Modelo para los periodos académicos (ej. Semestre I 2024, Año Escolar 2024-2025).
    """
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    """
    Representa una instancia de una Asignatura impartida en un Periodo Académico por un Profesor
    en un Salón, a un conjunto de Estudiantes.
    """
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True)
    periodo_academico = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True)
    estudiantes = models.ManyToManyField(Estudiante, through='Inscripcion') # Relación N:M a través de Inscripcion
    capacidad_maxima = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.periodo_academico.nombre} ({self.profesor.primer_nombre} {self.profesor.apellido_paterno if self.profesor else 'Sin Profesor'})"

class Inscripcion(models.Model):
    """
    Modelo para registrar la inscripción de un estudiante a un grupo.
    También puede almacenar la calificación final.
    """
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    calificacion_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('estudiante', 'grupo') # Un estudiante no puede inscribirse dos veces al mismo grupo

    def __str__(self):
        return f"Inscripción de {self.estudiante} en {self.grupo}"

class Calificacion(models.Model):
    """
    Modelo para registrar calificaciones específicas dentro de un grupo para un estudiante.
    Podría ser para parciales, tareas, exámenes, etc.
    """
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    nombre_evaluacion = models.CharField(max_length=100) # Ej. 'Primer Parcial', 'Tarea 1', etc.
    puntaje = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Nuevo campo
    detalle = models.CharField(max_length=255, blank=True, null=True)            # Nuevo campo
    descripcion = models.TextField(blank=True, null=True)                        # Nuevo campo
    fecha_evaluacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscripcion.estudiante} - {self.inscripcion.grupo.asignatura.nombre} - {self.nombre_evaluacion}: {self.puntaje}"

class EventoCalendario(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    
    TIPO_EVENTO_CHOICES = [
        ('general', 'Evento General'),
        ('evaluacion', 'Evaluación/Prueba'),
        ('reunion', 'Reunión'),
        ('actividad', 'Actividad Escolar'),
        ('administrativo', 'Administrativo'),
        ('otro', 'Otro'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    tipo_evento = models.CharField(max_length=15, choices=TIPO_EVENTO_CHOICES, default='general')
    
    # Asignación a cursos
    cursos = models.ManyToManyField('Curso', blank=True, related_name='eventos')
    para_todos_los_cursos = models.BooleanField(default=False, verbose_name='Para todos los cursos')
    solo_profesores = models.BooleanField(default=False, verbose_name='Solo para profesores')
    
    # Quien creó el evento
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_creados', null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-hora_inicio']
        verbose_name = "Evento de Calendario"
        verbose_name_plural = "Eventos de Calendario"

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"
    
    @property
    def es_evaluacion(self):
        """Indica si el evento es una evaluación"""
        return self.tipo_evento == 'evaluacion'
    
    @property
    def color_por_tipo(self):
        """Retorna color para el calendario según el tipo"""
        colores = {
            'evaluacion': '#e74c3c',     # Rojo suave para evaluaciones
            'reunion': '#3498db',        # Azul suave para reuniones
            'actividad': '#2ecc71',      # Verde suave para actividades
            'general': '#9b59b6',        # Púrpura suave para eventos generales
            'administrativo': '#f39c12', # Naranja suave para administrativo
            'otro': '#95a5a6'            # Gris suave para otros
        }
        return colores.get(self.tipo_evento, '#95a5a6')

class HorarioCurso(models.Model):
    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
        ('SA', 'Sábado'),
        ('DO', 'Domingo'),
    ]
    
    TIPO_PERIODO = [
        ('clase', 'Clase'),
        ('recreo', 'Recreo'),
        ('almuerzo', 'Almuerzo'),
        ('otro', 'Otro'),
    ]
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='horarios')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='horarios', null=True, blank=True)
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, related_name='horarios_asignados', null=True, blank=True)
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_periodo = models.CharField(max_length=10, choices=TIPO_PERIODO, default='clase')
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['dia', 'hora_inicio']
        verbose_name = "Horario de Curso"
        verbose_name_plural = "Horarios de Curso"
        unique_together = ['curso', 'dia', 'hora_inicio', 'hora_fin']

    def __str__(self):
        if self.tipo_periodo == 'recreo' or self.tipo_periodo == 'almuerzo':
            return f"{self.get_dia_display()} {self.hora_inicio} - {self.hora_fin} ({self.get_tipo_periodo_display()})"
        return f"{self.get_dia_display()} {self.hora_inicio} - {self.hora_fin} - {self.asignatura_nombre} ({self.curso.nombre})"
    
    def clean(self):
        """Validación personalizada del horario"""
        from django.core.exceptions import ValidationError
        super().clean()
        
        # Validar que hora_inicio < hora_fin
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser menor que la hora de fin")
        
        # Para clases, asignatura es obligatoria
        if self.tipo_periodo == 'clase' and not self.asignatura:
            raise ValidationError("Para períodos de clase, la asignatura es obligatoria")
        
        # Para recreos/almuerzo, no debe haber asignatura
        if self.tipo_periodo in ['recreo', 'almuerzo'] and self.asignatura:
            raise ValidationError("Los recreos y almuerzo no deben tener asignatura asignada")
        
        # Validar conflictos de horario en el mismo curso
        if self.curso:
            conflictos = self.verificar_conflictos_curso()
            if conflictos:
                raise ValidationError(f"Conflicto de horario en el curso: {conflictos}")
        
        # Validar conflictos de profesor
        if self.profesor and self.tipo_periodo == 'clase':
            conflictos_profesor = self.verificar_conflictos_profesor()
            if conflictos_profesor:
                raise ValidationError(f"Conflicto de profesor: {conflictos_profesor}")
    
    def verificar_conflictos_curso(self):
        """Verifica si hay conflictos de horario en el mismo curso"""
        horarios_conflicto = HorarioCurso.objects.filter(
            curso=self.curso,
            dia=self.dia,
            activo=True
        )
        
        if self.pk:
            horarios_conflicto = horarios_conflicto.exclude(pk=self.pk)
        
        conflictos = []
        for horario in horarios_conflicto:
            if self.hay_solapamiento(horario):
                conflictos.append(f"{horario.hora_inicio}-{horario.hora_fin} ({horario.asignatura_nombre})")
        
        return conflictos
    
    def verificar_conflictos_profesor(self):
        """Verifica si el profesor ya está asignado en otro curso en el mismo horario"""
        horarios_profesor = HorarioCurso.objects.filter(
            profesor=self.profesor,
            dia=self.dia,
            tipo_periodo='clase',
            activo=True
        )
        
        if self.pk:
            horarios_profesor = horarios_profesor.exclude(pk=self.pk)
        
        conflictos = []
        for horario in horarios_profesor:
            if self.hay_solapamiento(horario):
                conflictos.append(f"El profesor ya está asignado en {horario.curso.nombre} de {horario.hora_inicio} a {horario.hora_fin}")
        
        return conflictos
    
    def hay_solapamiento(self, otro_horario):
        """Verifica si hay solapamiento entre dos horarios"""
        return not (self.hora_fin <= otro_horario.hora_inicio or self.hora_inicio >= otro_horario.hora_fin)
    
    @property
    def duracion_minutos(self):
        """Retorna la duración del horario en minutos"""
        if self.hora_inicio and self.hora_fin:
            from datetime import datetime
            inicio = datetime.combine(datetime.today().date(), self.hora_inicio)
            fin = datetime.combine(datetime.today().date(), self.hora_fin)
            return int((fin - inicio).total_seconds() / 60)
        return 0
    
    @property
    def asignatura_nombre(self):
        """Retorna el nombre de la asignatura o el tipo de período"""
        if self.tipo_periodo in ['recreo', 'almuerzo']:
            return self.get_tipo_periodo_display()
        return self.asignatura.nombre if self.asignatura else "Sin asignatura"
    
    @property
    def profesor_nombre(self):
        """Retorna el nombre del profesor o 'Sin asignar'"""
        if self.tipo_periodo in ['recreo', 'almuerzo']:
            return "N/A"
        return f"{self.profesor.primer_nombre} {self.profesor.apellido_paterno}" if self.profesor else "Sin asignar"
    
    def get_profesores_disponibles(self):
        """Retorna los profesores disponibles para esta asignatura en este horario"""
        if not self.asignatura:
            return Profesor.objects.none()
        
        # Profesores que pueden enseñar esta asignatura
        profesores_asignatura = self.asignatura.get_todos_los_profesores()
        
        # Filtrar los que no tienen conflictos de horario
        profesores_disponibles = []
        for profesor in profesores_asignatura:
            # Crear horario temporal para verificar conflictos
            horario_temp = HorarioCurso(
                profesor=profesor,
                dia=self.dia,
                hora_inicio=self.hora_inicio,
                hora_fin=self.hora_fin,
                tipo_periodo='clase'
            )
            if self.pk:
                horario_temp.pk = self.pk
            
            if not horario_temp.verificar_conflictos_profesor():
                profesores_disponibles.append(profesor)
        
        return profesores_disponibles
    
    @staticmethod
    def generar_horario_base(curso):
        """Genera un horario base con recreos para un curso"""
        from datetime import time
        
        horarios_base = [
            # Lunes
            {'dia': 'LU', 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(8, 45), 'hora_fin': time(9, 30), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(9, 30), 'hora_fin': time(9, 45), 'tipo': 'recreo'},
            {'dia': 'LU', 'hora_inicio': time(9, 45), 'hora_fin': time(10, 30), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(10, 30), 'hora_fin': time(11, 15), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(11, 15), 'hora_fin': time(11, 30), 'tipo': 'recreo'},
            {'dia': 'LU', 'hora_inicio': time(11, 30), 'hora_fin': time(12, 15), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(12, 15), 'hora_fin': time(13, 30), 'tipo': 'almuerzo'},
            {'dia': 'LU', 'hora_inicio': time(13, 30), 'hora_fin': time(14, 15), 'tipo': 'clase'},
            {'dia': 'LU', 'hora_inicio': time(14, 15), 'hora_fin': time(15, 0), 'tipo': 'clase'},
            
            # Martes
            {'dia': 'MA', 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(8, 45), 'hora_fin': time(9, 30), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(9, 30), 'hora_fin': time(9, 45), 'tipo': 'recreo'},
            {'dia': 'MA', 'hora_inicio': time(9, 45), 'hora_fin': time(10, 30), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(10, 30), 'hora_fin': time(11, 15), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(11, 15), 'hora_fin': time(11, 30), 'tipo': 'recreo'},
            {'dia': 'MA', 'hora_inicio': time(11, 30), 'hora_fin': time(12, 15), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(12, 15), 'hora_fin': time(13, 30), 'tipo': 'almuerzo'},
            {'dia': 'MA', 'hora_inicio': time(13, 30), 'hora_fin': time(14, 15), 'tipo': 'clase'},
            {'dia': 'MA', 'hora_inicio': time(14, 15), 'hora_fin': time(15, 0), 'tipo': 'clase'},
            
            # Miércoles
            {'dia': 'MI', 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(8, 45), 'hora_fin': time(9, 30), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(9, 30), 'hora_fin': time(9, 45), 'tipo': 'recreo'},
            {'dia': 'MI', 'hora_inicio': time(9, 45), 'hora_fin': time(10, 30), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(10, 30), 'hora_fin': time(11, 15), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(11, 15), 'hora_fin': time(11, 30), 'tipo': 'recreo'},
            {'dia': 'MI', 'hora_inicio': time(11, 30), 'hora_fin': time(12, 15), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(12, 15), 'hora_fin': time(13, 30), 'tipo': 'almuerzo'},
            {'dia': 'MI', 'hora_inicio': time(13, 30), 'hora_fin': time(14, 15), 'tipo': 'clase'},
            {'dia': 'MI', 'hora_inicio': time(14, 15), 'hora_fin': time(15, 0), 'tipo': 'clase'},
            
            # Jueves
            {'dia': 'JU', 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(8, 45), 'hora_fin': time(9, 30), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(9, 30), 'hora_fin': time(9, 45), 'tipo': 'recreo'},
            {'dia': 'JU', 'hora_inicio': time(9, 45), 'hora_fin': time(10, 30), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(10, 30), 'hora_fin': time(11, 15), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(11, 15), 'hora_fin': time(11, 30), 'tipo': 'recreo'},
            {'dia': 'JU', 'hora_inicio': time(11, 30), 'hora_fin': time(12, 15), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(12, 15), 'hora_fin': time(13, 30), 'tipo': 'almuerzo'},
            {'dia': 'JU', 'hora_inicio': time(13, 30), 'hora_fin': time(14, 15), 'tipo': 'clase'},
            {'dia': 'JU', 'hora_inicio': time(14, 15), 'hora_fin': time(15, 0), 'tipo': 'clase'},
            
            # Viernes
            {'dia': 'VI', 'hora_inicio': time(8, 0), 'hora_fin': time(8, 45), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(8, 45), 'hora_fin': time(9, 30), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(9, 30), 'hora_fin': time(9, 45), 'tipo': 'recreo'},
            {'dia': 'VI', 'hora_inicio': time(9, 45), 'hora_fin': time(10, 30), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(10, 30), 'hora_fin': time(11, 15), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(11, 15), 'hora_fin': time(11, 30), 'tipo': 'recreo'},
            {'dia': 'VI', 'hora_inicio': time(11, 30), 'hora_fin': time(12, 15), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(12, 15), 'hora_fin': time(13, 30), 'tipo': 'almuerzo'},
            {'dia': 'VI', 'hora_inicio': time(13, 30), 'hora_fin': time(14, 15), 'tipo': 'clase'},
            {'dia': 'VI', 'hora_inicio': time(14, 15), 'hora_fin': time(15, 0), 'tipo': 'clase'},
        ]
        
        horarios_creados = []
        for horario_data in horarios_base:
            horario = HorarioCurso(
                curso=curso,
                dia=horario_data['dia'],
                hora_inicio=horario_data['hora_inicio'],
                hora_fin=horario_data['hora_fin'],
                tipo_periodo=horario_data['tipo']
            )
            horarios_creados.append(horario)
        
        return horarios_creados

class Perfil(models.Model):
    TIPOS_USUARIO = [
        ('director', 'Director'),
        ('profesor', 'Profesor'),
        ('alumno', 'Alumno'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO)

    def __str__(self):
        return f"{self.user.username} ({self.get_tipo_usuario_display()})"
    
    def es_director(self):
        """Verifica si el usuario es director"""
        return self.tipo_usuario == 'director'
    
    def es_profesor(self):
        """Verifica si el usuario es profesor"""
        return self.tipo_usuario == 'profesor'
    
    def es_alumno(self):
        """Verifica si el usuario es alumno"""
        return self.tipo_usuario == 'alumno'
    
    def puede_gestionar(self):
        """Verifica si el usuario puede gestionar el sistema (director)"""
        return self.es_director()
    
    def get_perfil_detalle(self):
        """Retorna el objeto específico según el tipo de usuario"""
        if self.es_profesor():
            return getattr(self.user, 'profesor', None)
        elif self.es_alumno():
            return getattr(self.user, 'estudiante', None)
        return None

class AsistenciaAlumno(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)  # Temporal para migración
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor_registro = models.ForeignKey(Profesor, on_delete=models.CASCADE, 
                                       related_name='asistencias_registradas_alumnos',
                                       help_text='Profesor que registró la asistencia',
                                       null=True, blank=True)  # Temporal para migración
    fecha = models.DateField(default=timezone.now, help_text='Fecha del registro de asistencia')
    hora_registro = models.TimeField(default=timezone.now, 
                                   help_text='Hora en que se registró la asistencia')
    presente = models.BooleanField(default=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos adicionales para mejor control
    justificacion = models.TextField(blank=True, null=True, 
                                   help_text='Justificación de la inasistencia')
    registrado_por_usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                             help_text='Usuario que registró la asistencia')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('estudiante', 'asignatura', 'fecha')
        ordering = ['-fecha', '-hora_registro']

    def __str__(self):
        return f"{self.estudiante.get_nombre_completo()} - {self.asignatura.nombre} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"

    def clean(self):
        """Validar que el profesor esté asignado a la asignatura y curso"""
        from django.core.exceptions import ValidationError
        
        if self.profesor_registro and self.asignatura:
            # Verificar que el profesor esté asignado a la asignatura
            if not self.asignatura.profesores_responsables.filter(id=self.profesor_registro.id).exists():
                if self.asignatura.profesor_responsable != self.profesor_registro:
                    raise ValidationError(
                        f'El profesor {self.profesor_registro.get_nombre_completo()} no está asignado a la asignatura {self.asignatura.nombre}'
                    )
        
        if self.curso and self.estudiante:
            # Verificar que el estudiante esté en el curso
            if not self.curso.estudiantes.filter(id=self.estudiante.id).exists():
                raise ValidationError(
                    f'El estudiante {self.estudiante.get_nombre_completo()} no pertenece al curso {self.curso}'
                )
        
        if self.curso and self.asignatura:
            # Verificar que la asignatura esté asignada al curso
            if not self.curso.asignaturas.filter(id=self.asignatura.id).exists():
                raise ValidationError(
                    f'La asignatura {self.asignatura.nombre} no está asignada al curso {self.curso}'
                )

class AsistenciaProfesor(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, null=True, blank=True,
                                 help_text='Asignatura en la que se registra la asistencia (opcional)')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True,
                            help_text='Curso en el que se registra la asistencia (opcional)')
    fecha = models.DateField(auto_now_add=True)
    hora_registro = models.TimeField(auto_now_add=True,
                                   help_text='Hora en que se registró la asistencia')
    presente = models.BooleanField(default=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos adicionales
    justificacion = models.TextField(blank=True, null=True,
                                   help_text='Justificación de la inasistencia')
    registrado_por_usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                             help_text='Usuario que registró la asistencia')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profesor', 'asignatura', 'fecha')
        ordering = ['-fecha', '-hora_registro']

    def __str__(self):
        asignatura_str = f" - {self.asignatura.nombre}" if self.asignatura else ""
        curso_str = f" - {self.curso}" if self.curso else ""
        return f"{self.profesor.get_nombre_completo()}{asignatura_str}{curso_str} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"


