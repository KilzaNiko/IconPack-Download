<h1 align="center">⬇️ IconPack-Downloader ⬇️ </h1>

<h1 align="center">Descargador de Iconos desde <a href="https://icon-icons.com/">icon-icons.com</a></h1>

<p align="justify">
Este programa, desarrollado en <img src="https://img.shields.io/badge/PYTHON-3.12.3-blue" alt="version" style="pointer-events: none; cursor: default;">, permite descargar pack de iconos de la página <a href="https://icon-icons.com/">icon-icons.com</a>. Proporciona opciones para seleccionar el formato y la resolución de los iconos, así como las páginas específicas del pack de las que se desea descargar los iconos.
</p>

## Descripción
<p align="justify">
El programa es simple y básico: recibe una URL de un pack de iconos de la página "icon-icons.com" y permite elegir el formato y resolución de los iconos, así como las páginas específicas del pack de las que se desea descargar los iconos.
</p>

### Formatos de URL permitidos

El programa admite URLs de packs de iconos en los siguientes formatos:
- `https://icon-icons.com/es/pack/MacOs-Big-Sur/3053`
- `https://icon-icons.com/pack/MacOs-Big-Sur/3053`
- `icon-icons.com/es/pack/MacOs-Big-Sur/3053`
- `icon-icons.com/pack/MacOs-Big-Sur/3053`

## Formas de Uso

El programa se puede utilizar de dos maneras:

### 1. Ejecutable (EXE) 🚀
<p align="justify">
Con el programa compilado, se puede ejecutar sin necesidad de tener Python instalado ni otros programas adicionales.
</p>

### 2. Script de Python (.py) 🛠️
<p align="justify">
Para ejecutar el script en formato `.py`, se requiere tener Python y algunas librerías instaladas.
</p>

#### Requisitos 
- **Python**: Asegúrese de tener Python instalado en su sistema.
- **Librerías necesarias**:
  - `requests`: Para realizar solicitudes HTTP.
  - `beautifulsoup4`: Para el análisis y manipulación de HTML.
  - `aiohttp`: Para realizar solicitudes HTTP asíncronas.
  - `tqdm`: Para mostrar barras de progreso en loops y tareas asíncronas.

Estas librerías se pueden instalar con el siguiente comando:
```bash
pip install requests beautifulsoup4 aiohttp tqdm
```

#### Ejecucion 
<p align="justify">
Una vez instalados Python y las librerías necesarias, ejecute el script desde la consola (PowerShell / CMD) en el directorio donde se encuentra el archivo:
</p>

```bash
python .\download_iconpacks.py
```

## Capturas

<details>
  <summary>Haz clic aquí para ver las capturas 📷</summary>
  <p align="center"> </p>
  <p align="center">Ingreso de URL</p>
  <img src="https://i.imgur.com/KxE7HGE.png" alt="#1"/>
  <p align="center"> </p>
  <p align="center">Selección de formato disponible</p>
  <img src="https://i.imgur.com/AM5nWWQ.png" alt="#2"/>
  <p align="center"> </p>
  <p align="center">Selección de resoluciones disponibles</p>
  <img src="https://i.imgur.com/GHOOR8X.png" alt="#3"/>
  <p align="center"> </p>
  <p align="center">Selección de páginas</p>
  <img src="https://i.imgur.com/sPqpInI.png" alt="#4"/>
  <p align="center"> </p>
  <p align="center">Barras de carga de procesos</p>
  <img src="https://i.imgur.com/KPRbm6b.png" alt="#5"/>
  <p align="center"> </p>
  <p align="center">Resultado de la descarga del pack de iconos ❤️</p>
  <img src="https://i.imgur.com/mI8B0cJ.png" alt="#6"/>
</details>

<p align="center">❤️ [KilzaNiko] ❤️</p>
