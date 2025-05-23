#  Trackademic – Documento de Requerimientos

## Descripción General

**Trackademic** es una aplicación diseñada para solucionar una necesidad habitual entre estudiantes universitarios: tener control, claridad y precisión sobre sus calificaciones a lo largo del semestre.

A menudo, los criterios de evaluación no son claros desde el comienzo del curso, pueden variar durante el semestre o simplemente no se entienden por completo. Asimismo, determinar cuántas calificaciones se requieren para mejorar o cuál es la calificación mínima necesaria en las próximas tareas se vuelve un proceso complicado.

El objetivo de la aplicación es brindar una herramienta **amigable y colaborativa** donde los estudiantes puedan:

- Consultar cursos y planes de evaluación establecidos.
- Registrar sus propias calificaciones.
- Ajustar actividades según las modificaciones del profesor.
- Diseñar planes desde cero si no han sido establecidos.
- Interactuar con otros compañeros sobre los planes.
- Proyectar calificaciones finales y recibir informes útiles para el seguimiento académico.

##  Requerimientos Funcionales

1. **Registro y autenticación de estudiantes**  
   Cada usuario debe tener una cuenta personal para ingresar y consultar sus notas.

2. **Visualización de cursos disponibles en cada semestre**  
   Mostrar asignaturas activas por grupo y profesor (datos desde Oracle/PostgreSQL).

3. **Consulta del plan de evaluación de un curso**  
   Visualizar por curso y grupo las actividades, porcentaje y descripción.

4. **Ingreso, edición y eliminación de notas por actividad**  
   Los estudiantes pueden gestionar sus calificaciones. Se almacena en MongoDB.

5. **Ingreso y edición de un plan de evaluación si no existe**  
   Estudiantes pueden crear y modificar planes si aún no están definidos.

6. **Modificación de actividades validando el 100%**  
   El sistema debe validar que la suma total de actividades sea 100%.

7. **Comentarios sobre planes de evaluación de otros estudiantes**  
   Trackademic fomenta la colaboración con sugerencias y comentarios.

8. **Visualización del consolidado de notas por semestre**  
   Promedios por curso, alertas de riesgo académico, etc.

9. **Informes de Valor para el Estudiante**
   - ¿Qué nota necesitas en la última actividad para aprobar?
   - ¿En qué tipo de actividades tienes peor rendimiento?
   - ¿Cuál ha sido tu evolución por semestre o curso?

##  Requerimientos No Funcionales

1. **Rendimiento**  
   Las consultas como "ver promedio" deben tardar menos de 2 segundos.

2. **Escalabilidad**  
   El sistema debe poder crecer con más usuarios y semestres sin rediseñar las bases.

3. **Usabilidad**  
   Interfaz clara, con validaciones y flujos intuitivos.

4. **Seguridad**  
   Autenticación, cifrado de contraseñas, validación de entradas.

5. **Disponibilidad**  
   Disponible al menos el 95% del tiempo, idealmente 24/7.

6. **Compatibilidad**  
   Funcional en navegadores modernos y dispositivos móviles.

---

# Sustentación Técnica – Elección de Arquitectura Híbrida (MongoDB + Relacional)

## ¿Por qué una Arquitectura Híbrida?

El sistema **Trackademic** requiere manejar dos tipos de información claramente diferenciados:

1. **Datos institucionales y estructurados**: como la lista oficial de profesores, cursos, semestres, grupos y sedes. Esta información es estable, altamente relacional y sujeta a reglas estrictas de integridad.
2. **Datos colaborativos y flexibles**: como las notas personalizadas de cada estudiante, comentarios, planes de evaluación creados por usuarios y modificaciones dinámicas.

Por esta razón, se propone una **arquitectura híbrida** que combine:

| Tipo de Datos                    | Base de Datos Sugerida      | Tecnología |
|----------------------------------|------------------------------|------------|
| Institucional, estructurado     | Relacional (Oracle/PostgreSQL) | Supabase u Oracle |
| Flexible, colaborativo, editable | NoSQL                        | MongoDB Atlas |

---

##  Sustentación de la Elección: MongoDB como BD NoSQL

###  Ventajas clave de MongoDB para este caso

1. **Modelo flexible de documentos**  
   MongoDB permite almacenar estructuras anidadas y cambiar la forma de los documentos sin afectar a otros registros. Ideal para representar planes de evaluación que pueden variar por curso o grupo.

2. **Escalabilidad horizontal**  
   MongoDB soporta grandes volúmenes de datos y crecimiento en usuarios de manera eficiente.

3. **Actualizaciones parciales**  
   Permite actualizar partes específicas de un documento sin sobrescribirlo todo, útil para editar una sola calificación o actividad.

4. **Soporte para comentarios y colaboración**  
   La funcionalidad de comentarios, edición colaborativa y aportes entre estudiantes encaja naturalmente en un esquema sin esquema rígido.

5. **Integración fácil con plataformas modernas**  
   MongoDB tiene SDKs y conectores listos para trabajar con Node.js, React, Python, entre otros.

6. **MongoDB Atlas (en la nube)**  
   Proporciona una capa de infraestructura gestionada, con respaldo, seguridad y disponibilidad de alta calidad sin necesidad de instalaciones locales.

---

##  Conclusión

La arquitectura híbrida con **PostgreSQL (Supabase)** para datos estructurados y **MongoDB Atlas** para datos dinámicos y colaborativos es la opción óptima.

- Ofrece lo mejor de ambos mundos: consistencia y estructura, junto con flexibilidad y escalabilidad.
- Permite una integración fluida, fácil desarrollo y alta disponibilidad.
- Reduce la complejidad lógica en el backend al especializar cada tipo de dato en su mejor motor de almacenamiento.
