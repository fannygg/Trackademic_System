
# Trackademic - Sistema de Gestión Académica Estudiantil

## Integrantes

* Oscar Suarez
* Maria Fanny Giraldo 


---

## Descripción general

**Trackademic** es una aplicación web colaborativa creada para estudiantes universitarios que necesitan llevar control exacto, claro y colaborativo de sus calificaciones por semestre. Permite registrar, consultar y proyectar notas, gestionar planes de evaluación personalizados y fomentar la interacción entre estudiantes a través de comentarios y sugerencias.

---

## Tecnologías utilizadas

* **Backend:** Django + Django REST Framework
* **Base de datos relacional:** PostgreSQL (Supabase) con Transaction Pooler (Shared Pooler) — ideal para aplicaciones sin estado (serverless, funciones breves e independientes)
* **Base de datos NoSQL:** MongoDB Atlas (para datos colaborativos y dinámicos)
* **Frontend:** HTML5, CSS3, JavaScript
* **Autenticación:** Django REST Framework Token Authentication

---

## Funcionalidades principales

### Módulo relacional (PostgreSQL - Supabase)

* Gestión de estudiantes, cursos, profesores y grupos
* Visualización de materias por semestre y grupo
* Validación de matrícula para ingreso de notas

### Módulo NoSQL (MongoDB Atlas)

* Gestión y edición de planes de evaluación por curso
* Registro, edición y eliminación de calificaciones por actividad
* Validación de que la suma de porcentajes en el plan sea 100%
* Comentarios colaborativos entre estudiantes sobre los planes

### Informes académicos

* Proyección de nota final por materia
* Alertas de bajo rendimiento por tipo de evaluación
* Consolidado de notas por semestre

---

## Instalación y configuración

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/trackademic.git
cd trackademic
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
```
---

### Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Ejecutar servidor

```bash
python manage.py runserver
```

---


### Requerimientos Funcionales

1. Registro y autenticación de estudiantes mediante cuenta personal.
2. Visualización de cursos disponibles por semestre (datos relacionales).
3. Consulta y edición de planes de evaluación (MongoDB).
4. Gestión completa de calificaciones por actividad.
5. Validación que los planes sumen 100% en porcentaje.
6. Comentarios colaborativos sobre los planes.
7. Consolidado y proyección de notas, con alertas de riesgo académico.
8. Informes personalizados para seguimiento académico.

### Requerimientos No Funcionales

* Rendimiento: respuestas en menos de 2 segundos.
* Escalabilidad para crecer sin cambios estructurales.
* Usabilidad clara e intuitiva.
* Seguridad robusta: autenticación, cifrado y validaciones.
* Alta disponibilidad (>95%).
* Compatibilidad con navegadores modernos y móviles.

---

## Sustentación Técnica – Arquitectura Híbrida (MongoDB + PostgreSQL)

### ¿Por qué híbrido?

* **Datos institucionales (estructurados):** se almacenan en PostgreSQL, gracias a su integridad y estructura relacional.
* **Datos colaborativos y dinámicos:** como notas personales y comentarios, se gestionan en MongoDB por su flexibilidad y escalabilidad.

### Ventajas de MongoDB

* Modelo de documentos flexible para estructuras variables.
* Actualizaciones parciales para modificar solo lo necesario.
* Escalabilidad horizontal.
* Integración con plataformas modernas.
* MongoDB Atlas ofrece infraestructura gestionada y segura.
