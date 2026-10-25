# Auditoría y evolución de DataConnect

Method: dual-agent (A: /root/dataconnect_design · B: /root/dataconnect_integrity)

Fecha: 25 de octubre de 2026. Alcance: estructura, comportamiento, integridad de los contactos, formularios, navegación, adaptación y detalles visuales. El usuario autorizó la revisión independiente con dos agentes y la corrección y publicación integral del proyecto.

## Método y procedencia

A realizó la crítica visual y de experiencia sin consultar el informe B ni resultados del detector. B revisó código y reprodujo defectos con datos desechables sin consultar A. El informe A quedó cerrado antes de liberar B para la síntesis. El agente principal implementó las correcciones y ejecutó la verificación final. Las puntuaciones corresponden al original: **17/40 en heurísticas de UX** y **8/20 en calidad técnica**; no se asigna una puntuación final sin una nueva evaluación independiente.

Se preservó la paleta y el propósito del producto. Las decisiones rutinarias se resolvieron dentro de la autorización del usuario, sin entrevistas adicionales. Las pruebas emplearon datos ficticios y libros temporales; el Excel personal original no se abrió ni se publicó.

El contexto y detector Impeccable no pudieron ejecutarse: el motor 0.1.5 no estaba instalado y la creación de su caché fue rechazada. No se generó un resultado JSON ni un overlay utilizable; **no se afirma que el detector haya aprobado el proyecto**. Las observaciones proceden de inspección manual, lectura de código y pruebas reproducibles.

Informes originales completos, conservados como evidencia histórica:

- [A: diseño y experiencia](reviews/design-original.md).
- [B: integridad y calidad técnica](reviews/integrity-original.md).

Las rutas y líneas citadas en esos dos documentos describen la versión anterior y no la estructura nueva. El script de reproducción original y sus resultados se conservan en `reviews/`; no es parte de la suite del código nuevo.

## Hallazgos y resolución

| Hallazgo original | Resultado en esta versión |
|---|---|
| Rutas accesibles sin autenticación y cierre de sesión aparente | Sesión real y comprobación común de acceso; logout mediante POST |
| Credenciales y secreto fijos | Separación explícita entre acceso demo público y configuración privada; hash de contraseña |
| IDs basados en número de fila, con edición de la persona equivocada tras borrar | UUID persistente por contacto; regresión automatizada |
| IDs manipulados corrompían encabezados o creaban filas vacías | Búsqueda por ID estable y respuesta 404 si no existe |
| Pérdida de escrituras solapadas | Bloqueo dentro de un proceso y reemplazo atómico; prueba de 20 escrituras concurrentes |
| Favorito y eliminación mediante GET, sin CSRF | Mutaciones mediante POST con token; GET sólo muestra confirmación |
| Entradas interpretadas como fórmulas Excel | Persistencia explícita como texto |
| Archivo ausente o corrupto causaba error opaco o reinicio vacío | Error 503 comprensible, sin sustituir los datos existentes |
| Reglas de validación contradictorias y pérdida del formulario | Validación del servidor, mensajes por campo y conservación de valores |
| Correos con dominios largos rechazados | Eliminada la restricción arbitraria de 2–4 caracteres del dominio |
| Teléfonos ignorados al buscar un solo dígito | Búsqueda de todas las cadenas, incluidos teléfonos y consultas cortas |
| Filtros y favoritos perdían contexto | Parámetros de filtro y retorno local conservados |
| Estado “Conectado” y crecimiento inventados | Eliminados; estadísticas calculadas desde los contactos |
| Login sin viewport móvil | Meta viewport y composición real de una columna |
| Encabezados del directorio desplazados | Tabla semántica con cuatro encabezados correspondientes a sus datos |
| Navegación móvil demasiado alta y formularios estrechos | Cabecera compacta; navegación consistente; campos apilados |
| Controles de icono de 36 px | Objetivos de 44 px y nombres accesibles |
| Login y búsqueda sin etiquetas asociadas | Labels y referencias comprobadas en todas las vistas de prueba |
| Diálogo sin gestión de foco ni salida con Escape | Diálogo nativo, Cancelar con foco inicial, Escape y restauración del foco |
| Iconos y tipografía dependientes de recursos externos | SVG e Inter locales con licencia incluida |
| Estilos duplicados y diferencias entre páginas | Plantilla base, macros y sistema CSS compartidos |
| Carga completa del Excel y de todo el listado | Límite conservado y documentado; siguiente paso: base de datos y paginación |

## Detalles visuales corregidos

Se unificaron títulos, distancias, bordes, navegación activa, botones, etiquetas, mensajes, pie de página y tarjetas. La búsqueda mantiene el mismo punto de entrada en los listados. Las categorías tienen una presentación compartida, los nombres y correos permanecen agrupados, y los enlaces de teléfono/correo están disponibles en la ficha.

Los campos opcionales se identifican; las confirmaciones nombran al contacto; los estados vacíos ofrecen una acción pertinente. El acceso identifica un usuario, sin etiquetarlo como correo. Los formularios muestran el propósito antes de los campos y evitan repetir rótulos innecesarios.

La primera inspección del código nuevo detectó un desbordamiento a 320 px, botones de formulario con salto de línea y cifras móviles desalineadas. Se corrigieron en un único lote y se ejecutó una ronda final de confirmación. No se continuó con ciclos abiertos de retoques.

## Verificación final

| Prueba | Evidencia |
|---|---|
| 42 pruebas de integración aprobadas | `tests/test_app.py`: autenticación, CSRF, CRUD, IDs estables, filtros, estadísticas, validación, escape, fórmulas, escrituras, errores y configuración |
| 37 vistas en cinco tamaños aprobadas | [browser-report.json](browser-report.json); 320, 390, 768, 1024 y 1440 px |
| Flujos de escritorio y móvil | Crear → editar → favorito → cancelar eliminación → confirmar eliminación |
| Formularios inválidos | Valores conservados, errores asociados y resumen enfocado |
| Sin JavaScript | Login y confirmación HTML funcionando |
| Estructura de las vistas | Sin desbordamiento, IDs duplicados, labels faltantes ni referencias ARIA rotas en el conjunto comprobado |
| Recursos | Inter cargada localmente; sin solicitudes externas ni errores de ejecución en la ronda final |

Capturas de demostración: [escritorio](images/directorio-desktop.png), [móvil](images/directorio-mobile.png), [acceso](images/acceso.png) y [estadísticas](images/estadisticas.png).

## Límites de la evaluación

Se probó un navegador Chromium/Edge y cinco tamaños, sin usuarios reales ni lector de pantalla. No se realizaron pruebas con todos los navegadores, miles de contactos, dispositivos físicos, auditoría externa de seguridad o certificación WCAG. No se probó alojamiento productivo, correo saliente ni recuperación de cuenta, porque no forman parte del proyecto.

El bloqueo protege solicitudes de una sola instancia Python; no coordina procesos o servidores diferentes. Excel debe permanecer cerrado durante las escrituras. La última edición válida de un contacto prevalece. No hay paginación, límites de intentos de login, permisos por usuario ni respaldo programado. Estas capacidades corresponden a una siguiente etapa de producto.

## Conservación y publicación

El proyecto académico y sus documentos se conservan en una carpeta local `archive/` ignorada por Git, además del respaldo del historial. La nueva publicación contiene código organizado, documentación y datos ficticios generados al iniciar. No incorpora el Excel original, el documento académico, secretos, `.venv`, cachés ni el historial anterior con archivos personales.
