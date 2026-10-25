# DataConnect — sistema visual

## Superficie y modo

Aplicación de contactos: **Operate**. La claridad del directorio y de los formularios tiene prioridad. Se conserva la identidad oliva y crema del proyecto anterior.

## Fundamentos

| Función | Token |
|---|---|
| Fondo | `--canvas: #f5f3ed` |
| Superficie | `--surface: #fffefa` |
| Texto principal | `--ink: #293029` |
| Texto secundario | `--muted: #666c61` |
| Marca y acción principal | `--olive: #394536` |
| Acento y foco | `--clay: #854d3d` |
| Error y eliminación | `--danger: #a33832` |
| Bordes | `--line: #dedfd4` |

Inter local, base de 15 px, controles móviles de 16 px, radio de 12 px. Las acciones tienen un objetivo táctil mínimo de 44 px. Los iconos provienen de un único sprite SVG.

## Composición

Navegación lateral de 232 px en escritorio y cabecera compacta con cuatro destinos en móvil. Tabla con encabezados correctos en escritorio; fichas apiladas en móvil. Formularios de dos columnas cuando hay espacio y una columna en pantallas pequeñas. El acceso utiliza dos paneles en escritorio y una columna en móvil.

## Comportamiento compartido

Un título principal por vista, foco visible, enlace para saltar al contenido, labels asociados, ayuda junto al campo y resumen de errores enfocable. El color acompaña texto o iconos identificables. Las acciones destructivas se confirman con el nombre del contacto. El diálogo conserva y restaura el foco; dispone de alternativa HTML.

## Criterios de mantenimiento

Usar `base.html`, macros y `app.css` para elementos compartidos. Mantener el vocabulario: Contactos, Favoritos, Nuevo contacto y Estadísticas. No agregar cifras, estados de conexión ni afirmaciones que el backend no mida. Servir recursos localmente y respetar preferencias de movimiento reducido.
