# DataConnect original — Assessment B: evidencia e integridad

Método: evaluación independiente B, aislada de Assessment A. No se consultaron hallazgos del otro evaluador. Objetivo: `original-app/app.py`, sus seis plantillas y siete archivos CSS/JS; navegador de revisión `http://127.0.0.1:5081`. Fecha: 25 de octubre de 2026. Modo: Operate.

## Veredicto

**La implementación permite el recorrido básico, pero no ofrece una frontera de acceso real ni garantiza la identidad y conservación de los contactos.** Las pruebas reproducen lectura y modificación sin login, sobrescritura de otro contacto por un ID desplazado, corrupción de encabezados y pérdida de una creación durante dos solicitudes solapadas. Son defectos de implementación comprobados, independientes del aspecto visual.

No se aplicó ningún cambio a fuentes ni al Excel compartido del servidor. El navegador sólo leyó páginas y abrió/canceló la confirmación de eliminación. Todas las mutaciones de prueba ocurrieron en libros desechables creados por el script dentro de un directorio temporal. No se abrió el Excel original de escritorio.

## Puntuación técnica de Impeccable

| Dimensión | Puntos / 4 | Evidencia principal |
|---|---:|---|
| Accesibilidad | 1 | Login y búsqueda sin nombre accesible fiable; modal sin gestión de foco; etiquetas con contraste insuficiente |
| Rendimiento | 2 | Cliente ligero, pero lectura completa del XLSX y renderizado de todas las filas por solicitud |
| Responsive | 2* | Hay breakpoints; el `display:flex` inline impide el apilado previsto de los campos; login sin viewport |
| Tematización | 2 | Variables CSS reales, duplicadas por página y mezcladas con valores inline; sin sistema central compartido |
| Integridad de implementación | 1 | Acceso aparente, IDs inestables, escrituras sin coordinación y estado de disponibilidad inventado |
| **Total** | **8/20** | **Deficiente: requiere correcciones importantes** |

*Responsive es una valoración provisional por código y escritorio a 1280 × 720; no se realizó una prueba visual en un viewport móvil. La ausencia de modo oscuro no se considera por sí sola un defecto: no existe un requisito que lo exija.*

## Hallazgos priorizados

### 1. [P1] El login no protege ninguna operación

**Localización:** `app.py:75–93`, rutas `102–491`; credenciales y secreto en `19`, `56–57`; enlaces “Cerrar Sesión” en las plantillas.

Un cliente nuevo, sin autenticación, recibe 200 en `/principal`, `/crear_contacto`, `/editar/2`, `/mas_informacion/2` y `/estadisticas`. También crea, edita, elimina y alterna favoritos. El login correcto sólo redirige: no escribe sesión ni devuelve cookie. “Cerrar Sesión” vuelve al formulario y `/principal` sigue disponible. El secreto configurado no crea autenticación por sí mismo.

**Impacto:** cualquiera que alcance la aplicación puede consultar y cambiar el libro. No debe presentarse como un sistema con control de acceso. **Recomendación:** sesión autenticada real, comprobación común en todas las rutas protegidas, logout que invalide sesión, credenciales fuera del código y contraseña almacenada mediante hash. El secreto literal debe sustituirse cuando se introduzcan sesiones. **Comando:** `$impeccable harden`.

### 2. [P1] El número de fila no es un identificador estable y actualizar no valida el rango

**Localización:** `app.py:124`, `174`, `336–351`, `396–444`.

Caso reproducido: se abre edición de Luis en fila 3; otra solicitud elimina Ana en fila 2; Zoe pasa a fila 3; guardar la edición original sobrescribe a Zoe con los datos de Luis. Además, POST válido a `/actualizar_contacto/1` reemplaza seis encabezados; a `/actualizar_contacto/20` crea una fila inexistente y deja huecos; ID 0 genera 500.

**Impacto:** una pestaña antigua puede editar o borrar a otra persona sin aviso; un ID manipulado daña el archivo. **Recomendación:** identificador persistente por contacto, comprobación de existencia antes de escribir y control de versión para detectar ediciones obsoletas. Responder con error recuperable ante IDs inválidos. **Comando:** `$impeccable harden`.

### 3. [P1] Dos creaciones solapadas producen una pérdida silenciosa

**Localización:** `app.py:253–257`, mismo patrón en `274–288`, `344–351`, `433–444`.

Se coordinó una prueba con dos clientes Flask y dos hilos: ambos cargaron la misma revisión; A guardó “Primero Temporal”; B guardó después “Segundo Temporal”. Ambas respuestas fueron 302 de éxito. El libro final sólo contenía Ana y Segundo: Primero desapareció. La instrumentación controla el orden para volver reproducible la ventana de carrera; no inventa una ruta de guardado alternativa.

**Impacto:** dos usuarios o pestañas pueden perder registros que la interfaz acaba de aceptar. No hay bloqueo, transacción, versión ni escritura atómica. **Recomendación:** persistencia transaccional, por ejemplo SQLite, o como mínimo coordinación de lectura/escritura y reemplazo atómico del archivo. **Comando:** `$impeccable harden`.

### 4. [P1] Eliminar y marcar favorito usan GET y carecen de protección contra solicitudes forjadas

**Localización:** `app.py:266`, `336`; `templates/index.html:133`, `150`, `184`; `static/js/validaciones.js:86–115`.

Un GET anónimo a `/eliminar_contacto/2` elimina el contacto; un GET a `/toggle_favorito/2` cambia el estado. La confirmación es sólo una interacción cliente y no protege el endpoint. Tampoco se exige token en los POST.

**Impacto:** navegación directa, enlaces externos y automatismos que sigan enlaces pueden modificar datos; corregir el login no solucionará este defecto. **Recomendación:** POST/DELETE para mutaciones, validación CSRF en el servidor y confirmación asociada al contacto concreto. **Comando:** `$impeccable harden`.

### 5. [P1] Los campos se almacenan como fórmulas de Excel

**Localización:** `app.py:257`, `437–442`.

Crear un contacto con nombre `=1+1` y dirección `=2+2` pasa las validaciones y produce celdas `A4` y `E4` de tipo `f`, no texto. No se abrió el archivo en Excel ni se ejecutaron fórmulas externas.

**Impacto:** los valores dejan de conservarse literalmente y Excel puede interpretar entradas como fórmulas. **Recomendación:** escribir estos campos explícitamente como texto y validar límites y contenido antes de persistir; verificar también el proceso de edición. **Comando:** `$impeccable harden`.

### 6. [P1] Los fallos de almacenamiento no tienen recuperación de usuario

**Localización:** `app.py:114`, `253`, `307`, `367`, `433`, `463`; inicialización `39–46`.

Un libro corrupto produce 500 en la lista. Si falta el archivo, detalle produce 500, mientras que lista lo recrea vacío y devuelve 200. El código tampoco captura fallos de permisos o libro abierto en Excel. Se comprobaron ausencia y corrupción; bloqueo por Excel es un riesgo inferido de la falta de manejo, no un fallo ejecutado.

**Impacto:** el usuario pierde acceso o puede interpretar un archivo desaparecido como una agenda vacía válida, sin camino de recuperación. **Recomendación:** capturar errores esperados, distinguir agenda nueva de archivo perdido, avisar sin sobrescribir y ofrecer restauración/respaldo. Evitar `debug=True` fuera de desarrollo (`app.py:498`); el test se ejecutó con debug desactivado, por lo que no se afirma exposición del depurador en el servidor revisado. **Comando:** `$impeccable harden`.

### 7. [P1] Accesibilidad: etiquetas, contraste y confirmación por teclado

**Localización:** `templates/login.html:38–44`, `templates/index.html:73`, `170–187`; `static/js/validaciones.js:86–132`; `static/css/crear_contacto.css:238–240` y estilos equivalentes.

El árbol accesible muestra los dos campos de login y la búsqueda como “text field” sin un nombre asociado. Los `label` de login carecen de `for` y no contienen su input. Los enlaces con iconos exponen caracteres de Font Awesome como nombre, con el texto útil relegado a Help/title. Favorito no expone su estado con `aria-pressed`.

En el modal, abrirlo deja el foco en el enlace de papelera, no hay `role=dialog`, `aria-modal`, enfoque inicial, retorno de foco o tratamiento de Escape. Se probó Escape y el modal permaneció abierto. Los campos de crear sí tienen etiquetas asociadas por envoltura: esto debe conservarse.

Se midieron etiquetas de crear en el DOM: `#888888` sobre `#ffffff`, 12.48 px y peso 700. Su relación de contraste es aproximadamente **3.54:1**, inferior a 4.5:1 para ese tamaño (WCAG 1.4.3). Las asociaciones afectan 1.3.1/3.3.2 y la identificación de controles 4.1.2; la gestión del diálogo debe cumplir operación comprensible por teclado y orden de foco.

**Recomendación:** nombres accesibles explícitos, iconos decorativos ocultos al lector, botón con estado para favoritos, diálogo nativo o gestión completa del foco y colores de texto con contraste AA. **Comandos:** `$impeccable harden`, `$impeccable colorize`.

### 8. [P2] Las reglas de datos difieren entre cliente y servidor

**Localización:** `app.py:26`, `221–250`, `405–429`; `static/js/validaciones.js:10–33`, `52–75`; formularios de crear/editar.

El servidor acepta dirección vacía y categoría “Inventada” aunque el formulario las exige y sólo ofrece cuatro categorías. También acepta ocho dígitos Unicode de ancho completo; no hay normalización. El JS utiliza `isNaN`, que comprueba conversión a número, no ocho caracteres ASCII: puede aceptar notación numérica que luego rechaza Python. El correo limita el último dominio a 2–4 letras; `caso@example.technology` fue rechazado, sin que esa restricción sea explicada al usuario.

**Impacto:** datos inconsistentes y rechazos inesperados entre canales. **Recomendación:** esquema de validación común, lista cerrada de categorías, política explícita de teléfono y correo razonable que no restrinja dominios por esa longitud. **Comando:** `$impeccable harden`.

### 9. [P2] La validación de servidor borra el formulario y oculta la causa

**Localización:** `app.py:229–250`, `412–429`.

Teléfono corto y correo malformado no se guardan, lo cual es correcto. Pero el servidor sólo imprime el error en consola y redirige a un GET vacío; no muestra el motivo ni conserva valores. El script registró redirección a crear sin mensaje visible en los tres rechazos. Crear/guardar tampoco produce confirmación persistente de éxito.

**Impacto:** el usuario debe reintroducir datos y no sabe qué corregir; las discrepancias con JS resultan especialmente confusas. **Recomendación:** respuesta con errores por campo y valores conservados, aviso de éxito accesible y salida segura cuando el guardado falla. **Comandos:** `$impeccable harden`, `$impeccable clarify`.

### 10. [P2] Buscar un dígito excluye los teléfonos

**Localización:** `app.py:160–170`.

Con los teléfonos `00000001`, `00000002`, `00000003`, buscar `0` devuelve cero contactos. Buscar `00000001` devuelve Ana. El caso especial de un solo dígito restringe la búsqueda a nombre/apellido, pese al placeholder “por nombre, teléfono...”. Categoría no forma parte de la búsqueda; no se trata como promesa incumplida porque el placeholder no la promete.

**Recomendación:** una regla de búsqueda consistente para todas las longitudes y pruebas sobre teléfono parcial. **Comando:** `$impeccable harden`.

### 11. [P2] Las acciones pierden el contexto de búsqueda y orden

**Localización:** `app.py:294–295`, `352–354`; `templates/index.html:70–87`.

El enlace de ordenar conserva la consulta, pero favorito y eliminar vuelven a `/principal` sin `q` ni `ordenar`. Enviar una nueva búsqueda tampoco conserva el orden actual. No se representa si A–Z ya está activo.

**Impacto:** quien gestiona una lista filtrada debe rehacer su búsqueda después de una acción; puede confundir el retorno a todos los registros con el resultado de la acción. **Recomendación:** transportar sólo parámetros de retorno permitidos y mantener estado visible. **Comando:** `$impeccable harden`.

### 12. [P2] La interfaz afirma información que no calcula

**Localización:** `app.py:324`, `477–491`; `templates/mas_informacion.html:85–88`, `templates/estadistica.html:82`.

El estado “Conectado” se asigna literalmente a todos los contactos: no existe consulta de presencia. “Incremento exponencial de contactos” es texto fijo; no hay fechas ni cálculo de crecimiento. “Últimos” es simplemente el orden inverso de las filas, sin fecha ni límite. Los totales y favoritos sí resultaron correctos para tres contactos (3 y 1) y para libro vacío (0 y 0).

**Impacto:** una decoración se presenta como dato operativo y puede orientar decisiones erróneas. **Recomendación:** retirar esas afirmaciones o respaldarlas con datos; explicar el criterio de recientes y limitar la lista. **Comando:** `$impeccable clarify`.

### 13. [P2] La adaptación de formularios a móvil contiene una regla ineficaz

**Localización:** `templates/Crear_contactos.html:66`, `templates/Editar.html:72`; `static/css/crear_contacto.css:388–390`, `static/css/editar.css:388–390`; `templates/login.html:3–8`.

La fila de nombre/teléfono tiene `style="display:flex; gap:15px"`. En el breakpoint móvil sólo cambia `grid-template-columns:1fr`: esa propiedad no apila elementos de un contenedor flex. El login omite la etiqueta viewport pese a tener media queries. Las acciones de lista miden 36 × 36 px (`styles.css:333–334`), inferiores al objetivo de comodidad táctil de 44 × 44; **esto por sí solo no prueba una violación WCAG 2.5.8**, cuyo mínimo y excepciones son distintos.

**Impacto:** campos comprimidos y adaptación poco predecible; tamaño táctil mejorable. **Recomendación:** eliminar la contradicción flex/grid, viewport coherente y pruebas reales a 320/390 px y con texto ampliado. **Comando:** `$impeccable adapt`. Hallazgo móvil por inspección de código; no se afirma overflow visual medido.

### 14. [P2] El costo crece con todos los contactos en cada visita

**Localización:** `app.py:114–195`, `463–491`; bucles de las plantillas principal/estadísticas.

Cada búsqueda abre y recorre el XLSX completo; estadísticas recorre todos y muestra todos los “recientes”; no hay paginación. Cada modificación reescribe el libro. No se ejecutó carga masiva ni se atribuye una latencia medida. El cliente usa CSS y un pequeño JS, sin un framework o paquete pesado innecesario, lo cual es positivo.

**Impacto:** escala de forma poco favorable y agrava las ventanas de escritura concurrente. **Recomendación:** consultar y paginar en una persistencia indexada, limitar recientes y medir con un volumen representativo. **Comando:** `$impeccable optimize`.

### 15. [P2] Cabecera y tarjetas no comparten la misma estructura de columnas

**Localización:** `templates/index.html:97–102`, `static/css/styles.css:37`, `227–237`, `264`.

El grid define cinco columnas (avatar, contacto, teléfono, información, acciones). La cabecera sólo contiene cuatro spans y `span:first-child` oculta “CONTACTO” como si fuera una celda vacía adicional. En la captura de escritorio “TELÉFONO” queda sobre la columna nombre/correo, no sobre los teléfonos.

**Impacto:** el encabezado orienta hacia una columna distinta y omite la etiqueta Contacto. **Recomendación:** estructura de encabezados alineada con los datos, preferiblemente una tabla semántica si se conserva la presentación tabular. **Comando:** `$impeccable layout`.

**Conteo:** 0 P0, 7 P1, 8 P2, 0 P3. P1 significa corregir antes de uso con datos reales o publicación; no implica que todas las pantallas estén bloqueadas para una demostración local.

## Patrones, fortalezas y dependencias

Los riesgos se concentran en asumir que la interfaz es una frontera de confianza y que una fila de Excel es una entidad estable. La corrección visual no resolvería ninguno de esos dos supuestos.

Hay validación de teléfono/correo en backend además del cliente; GET inválido de detalle/editar redirige a la lista; el patrón POST→redirect evita reenvíos accidentales por recarga; el cero de estadísticas funciona; Jinja escapa HTML: un nombre con `<script>alert(1)</script>` se muestra como texto escapado. Los formularios crear/editar sí usan labels envolventes y controles nativos. Los colores, radios y fuentes ya están parcialmente expresados como variables CSS, una base útil que conviene consolidar.

El artefacto revisado no contiene `requirements.txt`, lockfile ni `pyproject.toml`. El entorno de pruebas tiene Flask 3.1.3, Werkzeug 3.1.9 y openpyxl 3.1.5; esto describe el entorno, **no** certifica ausencia de vulnerabilidades ni fija las dependencias de la aplicación. Font Awesome depende de CDN (6.0.0 en la mayoría de vistas, 6.5.0 en estadísticas); sólo estadísticas solicita a Google las fuentes Lato/Playfair que el resto del CSS nombra, por lo que puede haber fuentes efectivas diferentes por página. No se instaló software ni se hizo un escaneo de CVE.

## Evidencia y reproducibilidad

- `integrity-tests.py`: ejecuta la app importada con `EXCEL_FILE` dirigido a un directorio temporal; registra salidas de HTTP y estado real del libro; no usa datos del servidor.
- `integrity-test-results.json`: resultados completos, versiones y métodos registrados por Flask. Son pruebas de caracterización, no una suite que declare saludable la aplicación.
- `integrity-test-errors.log`: trazas esperadas para ID 0, archivo corrupto y detalle con archivo ausente. Ejecución final del script: código de salida 0.
- Comando: `python -X utf8 <directorio-del-informe>/integrity-tests.py`.
- Navegador: pestaña nueva e independiente en segundo plano. Inspeccionó login, lista, crear, detalle y estadísticas; capturas de escritorio vistas y árbol accesible; abrir/cancelar modal y Escape sin borrar ningún registro. No se midió comportamiento con lector de pantalla real, red lenta, móvil, zoom 200% ni Excel abierto.

## Detector y notas de ejecución

Se intentó **una vez** `impeccable.cmd detect --json <original-app/templates>`. Salida 1, sin JSON ni conteo utilizable: `engine 0.1.5 is not installed; cannot create cache directory: "<cache-local>/impeccable/0.1.5"`. El launcher exige red/escritura para instalar el motor. Se registró la indisponibilidad sin instalar ni solicitar permisos. No debe presentarse como “detector limpio” ni atribuirle los hallazgos manuales. Falsos positivos del detector: no evaluables porque no corrió.

`context` también se intentó y falló por el mismo motivo. No hay PRODUCT.md/DESIGN.md propios en el artefacto DataConnect. Los de la raíz de workspace pertenecen a otra obra editorial, por lo que no se aplicaron. No había ignore list propia identificada en el árbol recibido. No se obtuvo slug de almacenamiento con el motor indisponible; este archivo es el archivo independiente solicitado, no una instantánea generada por critique-storage.

La API de navegador disponible permite inspección DOM de sólo lectura y no expone capacidad de inyección de scripts; no se intentó falsificar esa capacidad. No se inyectó overlay, no se cambió el título de página, no se inició live-server de Impeccable y no se afirma que exista visualización [Human]. Fallback: lectura de código, árbol accesible, propiedades computadas y capturas de escritorio. No se inició servidor adicional; el puerto 5081 es el servidor compartido provisto para revisión. No corresponde detenerlo desde esta evaluación.

Los libros temporales se eliminaron al finalizar. Una primera ejecución del arnés falló por resolver mal la ruta de templates durante importación; se corrigió el arnés registrando el módulo y se repitió la ejecución completa. También se retiró el directorio temporal vacío que quedó bloqueado por ser el cwd de esa primera ejecución. El fallo inicial no se atribuye a DataConnect. La ejecución final conserva sólo script, JSON y trazas de prueba en la carpeta del informe.

## Orden recomendado

1. `$impeccable harden`: acceso, sesiones, métodos/CSRF, IDs, concurrencia, contenido de Excel, validación, errores y accesibilidad de controles/diálogo.
2. `$impeccable clarify`: feedback, reglas de formulario y eliminación de presencia/crecimiento ficticios.
3. `$impeccable adapt`: corregir flex/grid y comprobar móvil y zoom con el flujo completo.
4. `$impeccable colorize` y `$impeccable layout`: contraste y encabezados correctamente asociados.
5. `$impeccable optimize`: paginación y costo de persistencia con datos representativos.
6. `$impeccable audit`: repetir pruebas contra las correcciones.
7. `$impeccable polish`: acabado final una vez resuelta la integridad.

Preguntas omitidas: este Assessment B alimenta la síntesis del evaluador principal; el cierre y las preguntas al usuario corresponden a esa síntesis.
