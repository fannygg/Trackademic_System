# Integrantes
- Oscar Suarez
- Maria Fanny Giraldo - A00399948
- Carlos Tafur
- Willian 

# Trackademic - Sistema de Gestión Académica Estudiantil

**Trackademic** es una aplicación web colaborativa desarrollada para estudiantes universitarios que buscan registrar, consultar y proyectar sus calificaciones por semestre. La aplicación permite gestionar planes de evaluación personalizados, ingresar notas por actividad y colaborar con otros estudiantes mediante comentarios y sugerencias.

## Tecnologías utilizadas

- **Backend:** Django
-  **Base de datos relacional (SQL):** Oracle Database
- **Base de datos NoSQL:** MongoDB
- **Frontend:** HTML5, CSS3, JavaScript 
- **Autenticación:** Django Auth

---

## Funcionalidades principales

### Módulo Oracle (Datos institucionales)
- Gestión de estudiantes, cursos, profesores y grupos
- Visualización de materias por semestre
- Validación de matrícula para ingreso de notas

### Módulo MongoDB (Datos colaborativos y dinámicos)
- Ingreso y edición de planes de evaluación por curso
- Registro de calificaciones por actividad
- Comentarios entre estudiantes sobre los planes
- Validación de que los porcentajes del plan sumen 100%

### Informes académicos
- Proyección de nota final por materia
- Alertas de bajo rendimiento por tipo de evaluación
- Consolidado de notas por semestre

---
## Instalación y configuración

### 1. Clonar el repositorio
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

### 3. Configurar conexiones a bases de datos

#### Oracle
Configura tu archivo `settings.py`:

####MongoDB
Crea un archivo `.env` con tu URI de MongoDB Atlas:

Y conéctalo desde Django usando `pymongo`:

```python
from pymongo import MongoClient
import os

mongo_client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["trackademic"]
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





