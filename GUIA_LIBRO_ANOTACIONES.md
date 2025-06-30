# 📚 Sistema de Libro de Anotaciones - Guía de Usuario

## 🎯 Descripción General

El Sistema de Libro de Anotaciones es una herramienta completa para la gestión del comportamiento estudiantil en instituciones educativas. Permite registrar, consultar y gestionar anotaciones positivas, negativas y neutras de los estudiantes, con un sistema de puntuación para evaluar el comportamiento general.

## 👥 Tipos de Usuario y Permisos

### 🔧 Administrador/Director
- **Acceso completo** a todas las anotaciones del sistema
- Puede ver, crear, editar y eliminar anotaciones de cualquier estudiante
- Acceso a estadísticas generales del sistema
- Gestión de usuarios y configuración del sistema

### 👨‍🏫 Profesor Jefe
- Puede ver y gestionar anotaciones de **todos los estudiantes de su curso**
- Puede crear anotaciones para estudiantes de su curso
- Acceso a estadísticas de comportamiento de su curso

### 👨‍🎓 Profesor de Asignatura
- Puede ver y gestionar anotaciones de **estudiantes en los cursos donde tiene asignaturas**
- Puede crear anotaciones relacionadas con sus asignaturas
- Acceso limitado a sus cursos asignados

### 🎓 Estudiante
- Puede ver **únicamente sus propias anotaciones**
- Acceso de solo lectura a su historial de comportamiento
- Puede ver su puntaje de comportamiento y estadísticas personales

## 📊 Sistema de Puntuación

### Tipos de Anotaciones y Puntos
- **Anotaciones Positivas**: +3 a +5 puntos
- **Anotaciones Negativas**: -2 a -5 puntos
- **Anotaciones Neutras**: 0 puntos
- **Anotaciones Graves**: Puntos negativos duplicados

### Niveles de Comportamiento
- **Excelente**: 20+ puntos (🟢 Verde)
- **Bueno**: 10-19 puntos (🟡 Verde claro)
- **Regular**: 0-9 puntos (🟡 Amarillo)
- **Malo**: -1 a -10 puntos (🟠 Naranja)
- **Muy Malo**: -11 o menos puntos (🔴 Rojo)

## 🎯 Categorías de Anotaciones

1. **Comportamiento**: Conducta general en el aula
2. **Rendimiento Académico**: Desempeño en estudios
3. **Disciplina**: Cumplimiento de normas
4. **Participación**: Involucramiento en actividades
5. **Puntualidad**: Asistencia y llegada a tiempo
6. **Responsabilidad**: Cumplimiento de deberes
7. **Colaboración**: Trabajo en equipo
8. **Actitud**: Disposición hacia el aprendizaje
9. **Otro**: Otras observaciones

## 🛠️ Funcionalidades Principales

### 📋 Lista de Anotaciones
- **Filtros avanzados**: Por estudiante, curso, tipo, categoría, fecha
- **Búsqueda**: Por nombre de estudiante o contenido
- **Ordenamiento**: Por fecha, estudiante, tipo, puntos
- **Estadísticas**: Resumen de anotaciones por tipo

### ➕ Crear Anotación
- **Selección de estudiante**: Por curso (carga dinámica)
- **Clasificación**: Tipo, categoría, gravedad
- **Puntuación**: Automática según tipo o manual
- **Comunicación**: Marcar si requiere contacto con apoderado

### ✏️ Editar/Eliminar Anotaciones
- **Permisos**: Solo el autor o administradores
- **Historial**: Registro de modificaciones
- **Validaciones**: Controles de integridad

### 📈 Detalle de Comportamiento
- **Perfil del estudiante**: Información completa
- **Gráfico de evolución**: Puntuación a lo largo del tiempo
- **Estadísticas detalladas**: Por categoría y período
- **Historial completo**: Todas las anotaciones

## 🔑 Usuarios de Prueba

### Administrador
- **Usuario**: `danie`
- **Contraseña**: [Tu contraseña configurada]

### Profesores
- **Usuario**: `prof_maria` | **Contraseña**: `123456`
- **Usuario**: `prof_carlos` | **Contraseña**: `123456`
- **Usuario**: `prof_ana` | **Contraseña**: `123456`

### Estudiantes
- **Usuario**: `est_est001` | **Contraseña**: `123456`
- **Usuario**: `est_est002` | **Contraseña**: `123456`
- *(Patrón: est_est### donde ### es el código del estudiante)*

## 🌐 Navegación del Sistema

### URLs Principales
- **Inicio**: `http://127.0.0.1:8000/`
- **Login**: `http://127.0.0.1:8000/login/`
- **Libro de Anotaciones**: `http://127.0.0.1:8000/anotaciones/`
- **Crear Anotación**: `http://127.0.0.1:8000/anotaciones/crear/`
- **Detalle Comportamiento**: `http://127.0.0.1:8000/anotaciones/estudiante/{id}/`

### Navegación por Tipo de Usuario

#### Como Administrador:
1. Accede a `/anotaciones/` para ver todas las anotaciones
2. Usa los filtros para encontrar información específica
3. Crea nuevas anotaciones desde el botón "Nueva Anotación"
4. Accede a detalles de comportamiento haciendo clic en nombres de estudiantes

#### Como Profesor:
1. Accede a `/anotaciones/` para ver anotaciones de tus cursos
2. Filtra por tu curso específico
3. Crea anotaciones para estudiantes de tus cursos
4. Revisa estadísticas de comportamiento

#### Como Estudiante:
1. Accede a `/anotaciones/` para ver solo tus anotaciones
2. Revisa tu puntaje de comportamiento
3. Consulta tu historial de anotaciones
4. Ve tu progreso a lo largo del tiempo

## 🔍 Funcionalidades Avanzadas

### Filtros Dinámicos
- **Por Curso**: Selecciona un curso específico
- **Por Estudiante**: Busca por nombre o código
- **Por Tipo**: Positivas, negativas, neutras
- **Por Categoría**: Comportamiento, disciplina, etc.
- **Por Fecha**: Rango de fechas personalizado
- **Por Gravedad**: Solo anotaciones graves

### Estadísticas en Tiempo Real
- **Contadores**: Total de anotaciones por tipo
- **Gráficos**: Evolución del comportamiento
- **Alertas**: Estudiantes que requieren atención
- **Reportes**: Exportación de datos

### Sistema de Notificaciones
- **Anotaciones Graves**: Alertas automáticas
- **Comunicación con Apoderados**: Seguimiento
- **Recordatorios**: Tareas pendientes

## 📱 Características Técnicas

### Tecnologías Utilizadas
- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de Datos**: SQLite (desarrollo)
- **Estilos**: Bootstrap 5
- **Gráficos**: Chart.js

### Características de Seguridad
- **Autenticación**: Sistema de login seguro
- **Autorización**: Permisos por tipo de usuario
- **Validaciones**: Controles de integridad de datos
- **Auditoría**: Registro de cambios

### Rendimiento
- **Consultas Optimizadas**: Uso eficiente de la base de datos
- **Carga Dinámica**: AJAX para mejor experiencia
- **Filtros Eficientes**: Búsquedas rápidas
- **Caching**: Optimización de consultas frecuentes

## 🚀 Próximas Mejoras

### Funcionalidades Planificadas
- **Exportación**: PDF y Excel de reportes
- **Notificaciones**: Email automático a apoderados
- **Mobile**: Aplicación móvil
- **Integración**: Con sistema de notas y asistencia

### Mejoras de UX
- **Dashboard**: Panel de control mejorado
- **Reportes**: Visualizaciones avanzadas
- **Automatización**: Reglas de comportamiento
- **Configuración**: Personalización por institución

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema:
- **Documentación**: Consulta este archivo
- **Logs**: Revisa la consola de Django para errores
- **Base de Datos**: Usa el admin de Django para gestión avanzada

---

**¡El Sistema de Libro de Anotaciones está listo para usar! 🎉**

*Desarrollado para la gestión eficiente del comportamiento estudiantil.*
