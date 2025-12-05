# pdf_diff

Aplicación profesional en Python para comparar dos archivos PDF a nivel de **texto**, detectando diferencias por **párrafos** y reportando también diferencias de **presencia de imágenes** (si en una página hay imagen en un documento y en el otro no).  
Diseñada con arquitectura modular y orientada a objetos para facilitar una futura integración con Flask.

## Características

- Comparación de PDFs **solo a nivel de texto** (no compara contenido de imágenes).
- Detección de párrafos por heurística (bloques separados por líneas en blanco).
- Identificación de:
  - Párrafos reemplazados
  - Párrafos insertados
  - Párrafos eliminados
- Manejo natural de **resincronización** mediante alineación basada en `difflib.SequenceMatcher`.
- Reporte de **presencia de imágenes por página**:
  - Ejemplo: “Página 4: En archivo A hay una imagen; en archivo B no hay imagen”.
- Salida:
  - Consola (humana y estructurada)
  - Archivo de texto opcional `--output`
  - Exportación JSON opcional `--json`
- Normalización de espacios y saltos de línea antes de comparar.
- Manejo robusto de PDFs con extracción de texto imperfecta (por ejemplo, derivados de OCR).
- Logging configurable.

## Arquitectura

El proyecto usa un layout moderno con `src/`:

- `PDFLoader`: 
  - Extrae texto por página.
  - Construye párrafos con metadatos de ubicación.
  - Detecta presencia de imágenes por página.
- `ParagraphComparator`:
  - Alinea listas de párrafos.
  - Genera un conjunto de diferencias estructuradas.
- `DiffReport`:
  - Formatea salida humana.
  - Serializa a JSON.
- `CLIApp`:
  - Orquesta el flujo.
  - Expone la interfaz de línea de comandos.

La lógica central está desacoplada del CLI para permitir una futura capa API/Flask sin cambios disruptivos.

## Instalación (macOS, Python 3.11)

```bash
cd pdf_diff
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
