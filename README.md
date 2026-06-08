# quick-board

Un pequeño tablero lateral para guardar textos, links, comandos, snippets o notas temporales que necesitás copiar varias veces durante el día.

quick-board es una app local de escritorio, pensada para productividad diaria en Windows.

---

## Índice

- [Qué hace](#qué-hace)
- [Herramientas utilizadas](#herramientas-utilizadas)
- [Alcance del MVP](#alcance-del-mvp)
- [Cómo usarla](#cómo-usarla)
- [Crear ejecutable para Windows](#crear-ejecutable-para-windows)
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

La app guarda la información localmente en archivos JSON, por lo que las tarjetas y la configuración se mantienen al cerrar y volver a abrir el programa.

---

## Herramientas utilizadas

| Herramienta | Uso |
|---|---|
| `Python` | Lenguaje principal del proyecto |
| `PySide6` | Interfaz gráfica de escritorio |
| `Qt Clipboard API` | Copiado de texto al portapapeles |
| `JSON` | Persistencia local de tarjetas y configuración |
| `ctypes` | Lectura del atajo global en Windows |
| `PyInstaller` | Generación del ejecutable `.exe` |
| `PowerShell` | Script de build para Windows |
| `Git` | Control de versiones |

Etiquetas del proyecto:

`Python` · `PySide6` · `Desktop App` · `Windows` · `Clipboard` · `JSON` · `PyInstaller` · `Productivity`

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
- Scripts simples para generar un ejecutable de Windows.

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

## Crear ejecutable para Windows

El proyecto incluye scripts para generar un ejecutable `.exe` de forma simple.

### Opción simple

Hacé doble click en:

```text
build_exe.bat
```

El script se encarga de ejecutar el build usando PowerShell.

### Opción desde PowerShell

También podés abrir PowerShell en la carpeta del proyecto y ejecutar:

```powershell
.\build_exe.ps1
```

El ejecutable se generará en:

```text
dist\quick-board.exe
```

### Si PowerShell bloquea el script

En algunos equipos, PowerShell puede bloquear la ejecución de scripts. En ese caso, ejecutá:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_exe.ps1
```

Este permiso aplica solo a la sesión actual de PowerShell.

### Qué hace el script de build

El script:

- verifica que estés en la raíz del proyecto
- crea el entorno virtual si no existe
- instala las dependencias de `requirements.txt`
- limpia builds anteriores
- genera el ejecutable con PyInstaller
- deja el archivo final en `dist\quick-board.exe`

---

## Estructura del proyecto

```text
quick-board/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── build_exe.ps1
├── build_exe.bat
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
- instalador formal para Windows
- inicio automático con Windows

Estas decisiones mantienen el MVP simple y posible de mantener.

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
- Si distribuís el `.exe`, probalo primero en una carpeta limpia para confirmar que crea y guarda los datos correctamente.

---

## Mejoras futuras

Ideas posibles para próximas versiones:

- Agregar instalador para Windows.
- Guardar los datos en `%APPDATA%\quick-board`.
- Agregar inicio automático con Windows.
- Permitir reordenar tarjetas.
- Agregar buscador rápido.
- Agregar modo oscuro completo.
- Permitir importar y exportar tarjetas.
- Agregar backup local.
- Agregar soporte opcional de cifrado.
- Agregar icono personalizado para el `.exe`.

---

## Estado del proyecto

MVP funcional.

La app ya puede usarse como un tablero rápido local para copiar contenido frecuente durante el día.
