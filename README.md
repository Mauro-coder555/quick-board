# quick-board

Un pequeño tablero lateral para guardar textos, links, comandos, snippets o notas temporales que necesitás copiar varias veces durante el día.

quick-board es una app local de escritorio, pensada para productividad diaria en Windows.

---

## Índice

- [Qué hace](#qué-hace)
- [Herramientas utilizadas](#herramientas-utilizadas)
- [Alcance del MVP](#alcance-del-mvp)
- [Cómo usarla](#cómo-usarla)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Limitaciones](#limitaciones)
- [Consejos de seguridad](#consejos-de-seguridad)
- [Mejoras futuras](#mejoras-futuras)

---

## Qué hace

quick-board muestra un panel lateral ocultable en el borde derecho de la pantalla.

Desde ese panel podés guardar hasta 10 tarjetas con contenido útil para copiar rápidamente, como:

- textos frecuentes
- links
- comandos
- snippets
- fechas
- notas temporales

Cada tarjeta permite copiar su contenido al portapapeles, editarla o borrarla.

La app guarda la información localmente en archivos JSON, por lo que las tarjetas se mantienen al cerrar y volver a abrir el programa.

---

## Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| `Python` | Lenguaje principal del proyecto |
| `PySide6` | Interfaz gráfica de escritorio |
| `Qt Clipboard API` | Copiado de texto al portapapeles |
| `JSON` | Persistencia local de tarjetas y configuración |
| `ctypes` | Lectura del atajo global en Windows |
| `PowerShell` | Comandos de setup y ejecución |
| `Git` | Control de versiones |

Etiquetas del proyecto:

`Python` · `PySide6` · `Desktop App` · `Windows` · `Clipboard` · `JSON` · `Productivity`

---

## Alcance del MVP

Esta versión incluye:

- Panel lateral ocultable.
- Atajo global para abrir y cerrar.
- Botón lateral visible para abrir manualmente.
- Hasta 10 tarjetas.
- Creación, edición y borrado de tarjetas.
- Copiado rápido al portapapeles.
- Persistencia local en JSON.
- Selector de idioma: español o inglés.
- Selector de color de fondo.
- Fondo tipo madera por defecto.
- Botón para cerrar definitivamente la app.

El objetivo del MVP es ser simple, útil y fácil de mantener.

---

## Cómo usarla

### 1. Crear entorno virtual

```powershell
python -m venv .venv
```

### 2. Activar entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Ejecutar la app

```powershell
python main.py
```

### 5. Usar el tablero

Al iniciar, la app aparece como un panel lateral.

Podés:

- agregar una tarjeta
- escribir un título corto
- escribir el contenido útil para copiar
- elegir un color para la tarjeta
- copiar el contenido con el botón de copiar
- editar o borrar tarjetas
- cambiar el idioma de la interfaz
- cambiar el color de fondo
- cerrar definitivamente la app con el botón de salida

---

## Estructura del proyecto

```text
quick-board/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── slots.json
│   └── settings.json
│
└── src/
    ├── __init__.py
    ├── storage.py
    ├── clipboard.py
    ├── hotkeys.py
    ├── settings.py
    └── ui.py
```

---

## Limitaciones

Esta versión no incluye:

- cifrado de datos
- contraseña maestra
- sincronización en la nube
- múltiples tableros
- búsqueda interna
- reordenamiento de tarjetas
- empaquetado automático como `.exe`
- inicio automático con Windows

Estas decisiones mantienen el MVP simple y posible de terminar rápido.

---

## Consejos de seguridad

quick-board no está pensada como gestor de contraseñas.

Aunque técnicamente podés guardar contraseñas, tokens o datos sensibles, no es recomendable hacerlo en esta versión porque la información se guarda localmente en archivos JSON sin cifrado.

Para información sensible, usá un password manager dedicado.

Recomendaciones:

- No guardes contraseñas importantes.
- No guardes claves de API privadas.
- No compartas tu carpeta `data/` si contiene información personal.
- Revisá el contenido de `data/slots.json` antes de subir el proyecto a un repositorio público.

---

## Mejoras futuras

Ideas posibles para próximas versiones:

- Empaquetar como `.exe` con PyInstaller.
- Agregar inicio automático con Windows.
- Permitir reordenar tarjetas.
- Agregar buscador rápido.
- Agregar modo oscuro completo.
- Permitir importar y exportar tarjetas.
- Agregar backup local.
- Agregar soporte opcional de cifrado.
- Crear instalador para Windows.

---

## Estado del proyecto

MVP funcional.

La app ya puede usarse como un tablero rápido local para copiar contenido frecuente durante el día.
