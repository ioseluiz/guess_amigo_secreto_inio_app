# Guess Amigo Secreto App

## Contexto

Considerate un experto programador en python y el framework django el cual ha sido contrato para crear una aplicacion con el objetivo de adivinar el amigo secreto.

## Requerimientos

### Requerimientos Funcionales

La aplicacion debe tener las siguientes features:

- Cada usuario debe contestar una pregunta sobre quien cree que es la persona que le regala a otra. Las respuestas seran de opcion multiple sin incluir a la persona sobre la que estan preguntando y al mismo usuario. Ejemplo: Quien crees que le regala a Juan? El usuario debe tener una pregunta por cada participante si incluirlo a el.

- cada usuario debe autenticarse para ingresar a la aplicacion. Tambien debe hacer logout y registrarse (signup).

- Cada usuario debe cargar en el sistema a quien le regala el. Esta informacion debe estar encriptada y no debe poder verla ningun otro usuario ni siquiera el administrador.

- Todas las respuestas deben estar encriptadas y solo debe poder verlas el mismo usuario. El administrador no debe poder ver ninguna respuesta de ningun usuario (encriptadas).

- Toda la informacion encriptada debe desencriptarse a una fecha y hora programada por el administrador.

- Se debe contar con una pantalla que muestre los resultados de las preguntas y en base al usuario que tiene la mayor cantidad de aciertos determinar un ganador. Debe contarse con un dashboard que presente graficas de resultados por preguntas. y Graficas por respuestas de cada usuario.

### Tecnologias

Se deben usar las siguientes tecnologias:
- Python
- Django
- html
- tailwind
- javascript
- base de datos postgresql
- git
- nginx
- gunicorn
- github actions

### Requerimientos No Funcionales

- La aplicacion se debe desplegar en una maquina virtual de azure (VM).
- La aplicacion debe ser responsive (ajustarse para visualizar correctamente sus pantallas de dispositivos moviles).
- Usa proceso de CI/CD.

## Tarea

Crear una aplicacion web con base de datos usando el framework django y python. Por favor generar todo el codigo requerido tanto para desarrollo como para producccion. Adicionalmente, crear una guia paso a paso con lo que se requiere hacer de forma detallada (instalaciones, codigo, etc) para crear la aplicacion.

