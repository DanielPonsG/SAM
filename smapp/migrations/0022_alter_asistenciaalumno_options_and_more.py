# Generated by Django 4.2.7 on 2025-06-29 02:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smapp', '0021_alter_estudiante_numero_documento_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asistenciaalumno',
            options={'ordering': ['-fecha', '-hora_registro']},
        ),
        migrations.AlterModelOptions(
            name='asistenciaprofesor',
            options={'ordering': ['-fecha', '-hora_registro']},
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='curso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='smapp.curso'),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='fecha_creacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='fecha_modificacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='hora_registro',
            field=models.TimeField(default=django.utils.timezone.now, help_text='Hora en que se registró la asistencia'),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='justificacion',
            field=models.TextField(blank=True, help_text='Justificación de la inasistencia', null=True),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='profesor_registro',
            field=models.ForeignKey(blank=True, help_text='Profesor que registró la asistencia', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asistencias_registradas_alumnos', to='smapp.profesor'),
        ),
        migrations.AddField(
            model_name='asistenciaalumno',
            name='registrado_por_usuario',
            field=models.ForeignKey(blank=True, help_text='Usuario que registró la asistencia', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='curso',
            field=models.ForeignKey(blank=True, help_text='Curso en el que se registra la asistencia (opcional)', null=True, on_delete=django.db.models.deletion.CASCADE, to='smapp.curso'),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='fecha_creacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='fecha_modificacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='hora_registro',
            field=models.TimeField(default=django.utils.timezone.now, help_text='Hora en que se registró la asistencia'),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='justificacion',
            field=models.TextField(blank=True, help_text='Justificación de la inasistencia', null=True),
        ),
        migrations.AddField(
            model_name='asistenciaprofesor',
            name='registrado_por_usuario',
            field=models.ForeignKey(blank=True, help_text='Usuario que registró la asistencia', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='asistenciaprofesor',
            name='asignatura',
            field=models.ForeignKey(blank=True, help_text='Asignatura en la que se registra la asistencia (opcional)', null=True, on_delete=django.db.models.deletion.CASCADE, to='smapp.asignatura'),
        ),
    ]
