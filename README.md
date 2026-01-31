# ImageToICO

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aplicación con interfaz gráfica moderna (PyQt6) para convertir imágenes (PNG, JPG, JPEG, BMP) a formato **.ico** con múltiples tamaños, ideal para iconos de aplicaciones Windows.

## Características
- Selección de carpeta o múltiples archivos
- Tamaños personalizables (por defecto: 16×16 hasta 512×512)
- Genera PNGs individuales + archivo .ico combinado
- Opción de mover o copiar la imagen original
- Validación de imágenes antes de procesar
- Barra de progreso y log en tiempo real
- Ventana centrada + icono personalizado en taskbar

## Requisitos
- Python 3.9+
- Pillow
- PyQt6

```
pip install Pillow PyQt6
```

## Uso
- Ejecuta python main.py
- Selecciona imágenes o carpeta
- Elige directorio de salida
- Configura tamaños deseados
- ¡Inicia el procesamiento!


## Licencia
Este proyecto está bajo la licencia **MIT** - ver archivo [LICENSE](LICENSE) para detalles.