# DataConnect original — Assessment A: revisión de diseño independiente

Fecha: 25 de octubre de 2026. Modo: Operate. Objetivo estable: `original-app` en esta carpeta, servido en http://127.0.0.1:5081. Evaluación A aislada: no se consultaron detectores ni el informe B. Este documento es una entrada para la síntesis del agente principal, no el informe dual completo.

## Método y límites

Inspección propia en Brave, una pestaña de revisión aislada. Se comprobó el acceso con las credenciales de prueba autorizadas y se recorrieron listado, creación y edición. Se observaron ficha y estadísticas mediante DOM, fuente y capturas complementarias. No se guardó, actualizó, marcó favorito ni eliminó ningún contacto. Solamente se leyeron los dos registros ficticios proporcionados.

La captura nativa falló después del ajuste móvil; se restableció el viewport y se capturaron las siete vistas en un contexto Chrome headless independiente, a 1440×1000 y 390×844, con el Chrome ya instalado, sin instalaciones. Evidencias en `design-evidence/`: 14 PNG y `observations.json`. Los iconos de Font Awesome sí aparecieron en Brave; no cargaron en las capturas headless. **No interpretar los botones vacíos de esas capturas como ausencia permanente de iconos.** Su dependencia de un recurso remoto y la falta de texto visible sí hacen el producto frágil ante esa situación.

El comando de contexto de Impeccable se intentó y falló por motor no instalado y permisos del caché. Los PRODUCT.md/DESIGN.md de cwd pertenecen a una obra editorial distinta, por lo que no se aplicaron. No se fabricaron personas ni objetivos comerciales específicos. No hubo pruebas con lector de pantalla, guardado real, latencia, miles de registros o interrupciones; las observaciones de esos comportamientos se distinguen como lectura de fuente o preguntas pendientes.

## Veredicto de especificidad

La paleta oliva, fondo crema, títulos marrón y monograma circular tienen una voz tranquila y reconocible. Los formularios y la barra lateral mantienen bastante continuidad. Sin embargo, la composición corresponde a un panel administrativo genérico: las oportunidades específicas de una agenda —encontrar a alguien, reconocer su categoría y llamarlo o escribirle— reciben menos atención que la marca repetida y el contenedor. Hay identidad cromática, pero todavía poca identidad de interacción.

La prioridad consiste en hacer confiable y legible el recorrido antes de sumar ornamentos: hay una contradicción de acceso, un encabezado de datos incorrecto y estados que afirman información que el sistema no mide.

## Fortalezas que conviene conservar

1. **Acción inicial localizable.** En escritorio, “Agregar Nuevo Contacto” se distingue, la búsqueda está arriba del listado y nombre/correo permanecen juntos. Hay un camino corto entre listado, alta y ficha.
2. **Lenguaje visual estable.** Fondos suaves, controles claros y radios coherentes conectan las vistas principales. El oliva funciona como color de navegación y acción principal sin llenar cada bloque de colores intensos.
3. **Salidas explícitas.** Crear y editar incluyen “Cancelar”; la ficha tiene “Volver al Menú”. Los formularios usan controles nativos y labels que envuelven sus campos; eso constituye una base aprovechable para teclado y móvil.

## Cinco prioridades

### 1. P1 — El acceso móvil queda reducido como una página de escritorio

**Evidencia:** `design-evidence/mobile-login.png`, `observations.json` (móvil/login: `innerWidth=980`, frente a 390 en las otras seis vistas); `templates/login.html` carece de meta viewport, aunque `login.css` define reglas móviles.

El teléfono recibe un lienzo de 980 px y lo reduce, conservando la barra lateral de escritorio. La pantalla de entrada exige ampliar o acertar sobre texto y controles muy pequeños. Es una dificultad seria en el comienzo del recorrido, aunque técnicamente se pueda hacer zoom.

**Cambio propuesto:** viewport correcto y composición de acceso móvil de una columna; mostrar marca compacta, título “Iniciar sesión”, campos y acción en el primer tramo. Verificar también 320/360 px y zoom. No hace falta una barra lateral completa para un único destino “Inicio de Sesión”.

### 2. P1 — Las etiquetas de la lista describen columnas equivocadas

**Evidencia:** Brave escritorio y `desktop-list.png`; `templates/index.html` contiene cuatro spans de cabecera; `static/css/styles.css` define cinco columnas y oculta el primer span con `.table-labels span:first-child { visibility: hidden; }`.

“CONTACTO” desaparece; “TELÉFONO” queda encima de los nombres, “INFORMACIÓN” sobre los números y “ACCIONES” sobre los controles de información. El lector tiene que ignorar activamente el encabezado y reconstruir el significado por el contenido. Con dos contactos se puede compensar; con una lista larga la señal incorrecta se repite en cada lectura.

**Cambio propuesto:** hacer coincidir cabecera y fila en la misma estructura, dejando una celda real para avatar o integrándolo en la celda de contacto. Usar una tabla semántica si la interacción es tabular; en móvil, tarjetas con datos y acciones agrupados expresamente. Validar la alineación con una fila larga y tamaños intermedios.

### 3. P1 — Parte del contenido transmite hechos que no están respaldados

**Evidencia:** login etiqueta “CORREO ELECTRÓNICO” pero placeholder “Escribe Tu Usuario” y el acceso de prueba usa un identificador; `app.py:324` asigna siempre `estado: 'Conectado'`; ficha lo llama “Estado de Disponibilidad”. `templates/estadistica.html` imprime “Incremento exponencial de contactos” bajo un simple total.

Son problemas de confianza, no solo de redacción. El usuario puede intentar su correo donde se espera un usuario, interpretar que otra persona está en línea o inferir crecimiento sin comparación temporal.

**Cambio propuesto:** elegir “Usuario” para el acceso actual; retirar el estado en línea hasta contar con una fuente real, o explicar un estado administrativo real si existe; sustituir la afirmación de crecimiento por descripción literal del total. Revisar también singular/plural (“1 destacados”) y “Etiqueta laboral” cuando las opciones incluyen Familia y Amigos.

### 4. P1 — El formulario explica las reglas tarde y la recuperación es frágil

**Evidencia:** capturas create/edit y `templates/Crear_contactos.html:70–99`, `Editar.html:68–96`: todos los campos y categoría son required, sin explicación visible. `validaciones.js` exige teléfono de ocho dígitos y presenta errores mediante alert; limita dominios a 2–4 letras. `app.py:231–249` y `414–429` redirige al formulario ante errores de backend, sin devolver un error visible ni los valores enviados. La edición termina en una confirmación nativa que dice que la acción no se puede revertir.

No se conoce de antemano el formato telefónico ni por qué una dirección es necesaria para guardar una persona. Un correo válido con dominio más largo puede ser rechazado. El error del backend borra el contexto enviado; el usuario ve la pantalla otra vez y debe deducir qué ocurrió. Esto último se confirma por fuente, sin enviar datos para provocar el fallo.

**Cambio propuesto:** texto breve sobre obligatoriedad; ejemplo local de ocho dígitos junto al teléfono; validación en el campo con mensaje que diga cómo corregirlo; conservar valores tras el error. Revisar si dirección y categoría realmente deben ser obligatorias. Reservar confirmaciones para la eliminación y otras operaciones con riesgo real; un guardado normal necesita un resultado claro y, si es viable, posibilidad de corregirlo después.

### 5. P2 — Las acciones y la cabecera móvil consumen atención sin ayudar a reconocer tareas

**Evidencia:** captura móvil/list, create, edit, detail y stats; acciones de listado 36×36 px en `observations.json` y styles.css; ficha usa iconos con title, sin texto visible. La cabecera móvil ocupa aproximadamente 280–318 px, entre un tercio y algo más del primer viewport. En crear/editar nombre y teléfono conservan dos columnas: se cortan placeholders y labels saltan de línea. En detalle aparecen cinco enlaces de navegación y tres acciones contextualizadas solo por iconos.

El engranaje significa “ver detalles”, aunque su convención más habitual es configuración. Editar y eliminar están próximos y ambos son llamativos. La navegación expandida deja el formulario bajo el primer tercio de pantalla, y se repite la marca en una segunda franja de 78 px. Para una tarea breve, hay demasiada interfaz antes de los datos.

**Cambio propuesto:** enlace de nombre a la ficha y texto “Ver contacto”; acciones secundarias agrupadas, eliminación menos prominente y controles táctiles de al menos 44 px. Cabecera móvil compacta con ubicación y navegación desplegable. Apilar nombre y teléfono cuando las dos columnas ya no ofrecen espacio útil. Mantener una jerarquía de una acción principal por vista.

## Observaciones granulares adicionales

| Prioridad | Superficie / evidencia | Observación y mejora concreta |
|---|---|---|
| P2 | login, `login.html` | “OU” entre líneas no conduce a ninguna alternativa; parece otro idioma o un flujo incompleto. Retirarlo si no existe segunda vía de acceso. |
| P2 | login, AX Brave | Las dos etiquetas no están asociadas mediante for/id ni envolviendo el input. El árbol las presenta separadas y los campos sin nombre. Asociar labels y añadir autocomplete adecuado. |
| P2 | listado, DOM | El envío de búsqueda está oculto; se depende de Enter. Mostrar un botón Buscar o una búsqueda automática con feedback; conservar label accesible aunque se recorte el placeholder. |
| P2 | listado vacío, `desktop-empty.png` | Explica que no hay coincidencias y mantiene “Limpiar”, lo cual ayuda. Falta una acción junto al propio mensaje y un estado distinto para una agenda inicialmente vacía. No se borraron registros para probar el cero real; la plantilla usa el mismo else para ambos casos. |
| P2 | estadísticas, captura/source | No hay indicador activo en el enlace Estadísticas. Tampoco lo hay en editar; la ficha añade “Editar Usuario” solamente en esa vista. Mantener navegación estable y ubicación inequívoca. |
| P2 | detalle, captura/source | Teléfono y correo son strong, no enlaces tel/mailto. La ficha informa, pero no acelera contactar. Confirmar si llamar/escribir está dentro del objetivo antes de agregarlo. |
| P2 | modal de eliminar, source JS/HTML | Mensaje genérico sin nombre del contacto, sin gestión de foco/Escape observable en el código. Añadir nombre y foco explícito; la ficha usa confirm nativo, otro patrón para la misma acción. No se ejecutó eliminación. |
| P2 | iconos, comparación Brave/headless | El fallback remoto produce controles sin signo visible y sin texto. Usar recursos locales y nombres accesibles; la identificación de una acción no debe depender solo de que cargue la tipografía de iconos. |
| P2 | tipografía/source | Lato y Playfair se declaran globalmente, pero la importación Google Fonts solo aparece en estadísticas; otras páginas pueden renderizar fallback serif/sans. Unificar carga local y verificar la fuente realmente disponible. |
| P2 | listado y labels | Correo a 0.76 rem y gris #888, labels a ~0.7–0.8 rem en mayúsculas espaciadas: legibilidad secundaria débil. Aumentar tamaño y oscuridad, especialmente datos de contacto. No se afirma conformidad de contraste sin medición técnica. |
| P3 | formularios | Repetir “EDITAR” en cada label recarga la lectura; el título ya proporciona el contexto. Usar “Nombre completo”, “Teléfono”, etc. |
| P3 | títulos | “Panel Principal: Crear Contactos / Editar Contactos” es largo y redundante. “Nuevo contacto” / “Editar contacto” resulta más preciso. |
| P3 | tarjetas de formulario | La marca DC/DataConnect se repite en sidebar, título de acceso y/o franja del formulario. Sustituir la franja por contexto útil o reducirla. |
| P3 | estadísticas | El uso de address produce nombres y correos en cursiva; no aporta una distinción semántica útil a esta lista y altera el sistema tipográfico. |
| P3 | detalle, captura | Los botones del pie se apoyan directamente contra el borde de la tarjeta. Añadir padding coherente con los campos. |
| P3 | cabecera móvil de estadísticas | DC y DataConnect quedan apilados, mientras en otras vistas comparten fila. Unificar el componente. |

## Diez heurísticas de Nielsen

Escala: 0 ausente/roto, 4 excelente. Las diez son aplicables a este gestor; ninguna es n/a. Puntuación orientativa de la evidencia disponible, no certificación técnica.

| Heurística | /4 | Razón principal |
|---|---:|---|
| 1. Visibilidad del estado | 2 | Hay selección en listado/crear y favoritos visuales; falta ubicación en estadísticas/editar y feedback de guardado explícito por fuente. |
| 2. Correspondencia con mundo real | 2 | Español y campos familiares; acceso usuario/correo, “laboral”, estado conectado y crecimiento no corresponden a datos reales. |
| 3. Control y libertad | 2 | Cancelar, Volver y Limpiar existen; no hay deshacer ni preservación de entrada fallida; no se verificó recuperación de borrado. |
| 4. Consistencia y estándares | 2 | Buena paleta común; tabla desalineada, dos confirmaciones distintas, navegación y fuentes variables. |
| 5. Prevención de errores | 2 | Required, tipos tel/email y confirmación de eliminación ayudan; reglas no anticipadas, etiquetas ambiguas y edición con alerta excesiva. |
| 6. Reconocer antes que recordar | 2 | Nombres y menús visibles; engranaje, iconos sin texto, reglas implícitas y navegación cambiante exigen aprendizaje. |
| 7. Flexibilidad y eficiencia | 2 | Búsqueda y A-Z; no se ven atajos, acciones masivas, filtro de favoritos/categoría ni contacto directo. Valorar necesidad según escala real. |
| 8. Estética y minimalismo | 2 | Apariencia tranquila y coherente; espacio de marca repetido, navegación móvil grande y contenido ficticio restan utilidad. |
| 9. Diagnóstico y recuperación de errores | 1 | Alertas frontend con algo de guía; backend redirige sin explicación/preservación por fuente. |
| 10. Ayuda y documentación | 0 | No se encontró ayuda visible ni orientación contextual para formatos/reglas. |

**Total: 17/40 — banda “Poor” de la guía.** Describe brechas de experiencia en varios estados, no una ausencia de base visual. No se puntúa un flujo de guardado como probado: se observó su implementación y se evitó modificar datos.

## Carga cognitiva

Checklist por tarea: fragmentación en grupos ≤4, agrupación, jerarquía, una decisión a la vez, elecciones mínimas, memoria de trabajo, revelación progresiva.

| Tarea | Fallos | Nivel | Explicación |
|---|---:|---|---|
| Entrar | 2/7 | Moderada | Contradicción usuario/correo y alternativa “OU” inexistente; decisión simple pero información contradictoria. |
| Encontrar y operar contacto | 3/7 | Moderada | Cabecera de columnas equivocada, cuatro iconos por fila sin texto y comandos globales compitiendo. |
| Crear/editar | 2/7 | Moderada | Reglas recordadas/descubiertas al fallar y falta de anticipación de requisitos. Cinco campos no son cinco elecciones simultáneas si se completan en secuencia. |
| Consultar ficha móvil | 3/7 | Moderada | Cinco opciones de navegación, tres acciones de icono y estado redundante/ficticio; excesiva cabecera retrasa lo relevante. |
| Leer estadísticas | 1/7 | Baja | Dos métricas y contactos recientes se comprenden; la validez de la interpretación, no la cantidad, es el problema. |

Puntos con más de cuatro opciones: ficha con cinco enlaces de navegación sin agrupación contextual suficiente; listado con búsqueda, A-Z, alta y cuatro acciones por fila (siete clases de acción si se consideran todas juntas). No se penaliza por contar indiscriminadamente las ocho acciones repetidas de dos contactos: la fila es una agrupación perceptual válida. La categoría ofrece exactamente cuatro opciones y satisface el límite.

## Recorrido emocional

**Entrada:** colores suaves y pocos campos tranquilizan; “correo” frente a “usuario” introduce la primera duda. En móvil la reducción a escritorio profundiza el valle inicial.

**Listado:** dos nombres familiares y un alta visible dan sensación de control. El encabezado incorrecto y los iconos obligan a reaprender el espacio.

**Alta:** la tarjeta ordenada invita a completar; no se informa qué formatos se esperan. Una alerta tardía o redirección muda puede convertir una tarea pequeña en frustración. La repetición de marca tiene más presencia que la asistencia.

**Edición/detalle:** ver los valores existentes da seguridad. El aviso de irreversibilidad para editar aumenta la gravedad percibida; “Conectado” promete una certeza inexistente. El final del guardado debería confirmar la persona y el cambio, con un regreso claro al contexto; esto se propone y no se afirma como validado.

**Estadísticas:** las cifras grandes permiten una lectura rápida; “Incremento exponencial” genera una conclusión engañosa como recuerdo final. Un cierre honesto con totales y fecha/contexto de medición fortalecería confianza.

## Personas: señales concretas

- **Jordan, primera vez:** puede introducir correo en vez de usuario; interpretar “Etiqueta laboral” como obligatoria incluso para familiares; no descubrir que el engranaje abre la ficha. No hay ayuda contextual para resolverlo.
- **Sam, teclado/baja visión:** labels de login no asociados; iconos de fila con nombre accesible basado en glifos en la captura DOM, labels pequeños; modal sin gestión de foco/Escape en fuente. No se probó NVDA, por lo que son riesgos verificables de estructura, no un resultado de lector de pantalla inventado.
- **Casey, móvil interrumpido:** acceso reducido, menú alto, nombre/teléfono estrechos y acciones de 36 px. La lectura de fuente muestra que un error backend no conserva su entrada; no se probó recuperación tras cambiar de app.

## Preguntas sugeridas para la síntesis final

1. ¿El objetivo principal es guardar contactos para una entrega académica o usar la agenda habitualmente para llamar y escribir? Cambia qué mejoras de eficiencia justifican complejidad.
2. ¿El acceso debe aceptar nombre de usuario o correo, y debe existir alguna disponibilidad real del contacto?
3. ¿Dirección y categoría tienen que ser obligatorias para registrar a alguien, o basta con nombre y un medio de contacto?
4. ¿Se prioriza corregir primero el recorrido móvil y los mensajes de confianza, conservando oliva/crema y la identidad actual?

Preguntas no formuladas al usuario por este subagente: se entregan al agente principal para el cierre único de la revisión dual.
