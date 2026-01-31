import sys
import os
import shutil
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit,
    QProgressBar, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

class ImageProcessorThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, input_paths, output_directory, sizes, move_original):
        super().__init__()
        self.input_paths = input_paths
        self.output_directory = output_directory
        self.sizes = sizes
        self.move_original = move_original

    def run(self):
        total_images = len(self.input_paths)
        for idx, input_path in enumerate(self.input_paths):
            self.process_image(input_path)
            self.progress.emit(int((idx + 1) / total_images * 100))
        self.finished.emit()

    def process_image(self, input_path):
        try:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_subdir = os.path.join(self.output_directory, base_name)

            if not os.path.exists(output_subdir):
                os.makedirs(output_subdir)

            img = Image.open(input_path)

            resized_images = []
            for size in self.sizes:
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                output_png_path = os.path.join(output_subdir, f"{base_name}_{size}.png")
                resized_img.save(output_png_path, "PNG")
                self.log.emit(f"Generada PNG: {output_png_path}")
                resized_images.append(resized_img)

            if resized_images:
                ico_path = os.path.join(output_subdir, f"{base_name}.ico")
                resized_images[0].save(
                    ico_path,
                    format='ICO',
                    append_images=resized_images[1:],
                    sizes=[(size, size) for size in self.sizes]
                )
                self.log.emit(f"Generado ICO: {ico_path}")

            if self.move_original:
                original_output_path = os.path.join(output_subdir, os.path.basename(input_path))
                shutil.move(input_path, original_output_path)
                self.log.emit(f"Movida original: {original_output_path}")
            else:
                original_output_path = os.path.join(output_subdir, os.path.basename(input_path))
                shutil.copy(input_path, original_output_path)
                self.log.emit(f"Copiada original: {original_output_path}")

        except Exception as e:
            self.log.emit(f"Error al procesar {input_path}: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        VERSION = "1.0.0"
        self.setWindowTitle(f"ImageToICO v{VERSION} - Generador de iconos Windows")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Input selection
        self.input_layout = QHBoxLayout()
        self.input_label = QLabel("Archivos/Directorio de Entrada:")
        self.input_field = QLineEdit()
        self.input_field.setReadOnly(True)
        self.input_browse_btn = QPushButton("Seleccionar Archivos/Directorio")
        self.input_browse_btn.clicked.connect(self.browse_input)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.input_browse_btn)
        self.layout.addLayout(self.input_layout)

        # Output directory
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel("Directorio de Salida:")
        self.output_field = QLineEdit()
        self.output_field.setText(os.path.abspath("output"))
        self.output_browse_btn = QPushButton("Seleccionar Directorio")
        self.output_browse_btn.clicked.connect(self.browse_output)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_field)
        self.output_layout.addWidget(self.output_browse_btn)
        self.layout.addLayout(self.output_layout)

        # Sizes configuration
        self.sizes_layout = QHBoxLayout()
        self.sizes_label = QLabel("Tamaños (pixels):")
        self.sizes_combo = QComboBox()
        self.sizes_combo.addItems(["512", "256", "128", "64", "48", "32", "24", "16"])
        self.sizes_combo.setEditable(True)
        self.add_size_btn = QPushButton("Añadir Tamaño")
        self.add_size_btn.clicked.connect(self.add_size)
        self.remove_size_btn = QPushButton("Eliminar Seleccionado")
        self.remove_size_btn.clicked.connect(self.remove_size)
        self.sizes_layout.addWidget(self.sizes_label)
        self.sizes_layout.addWidget(self.sizes_combo)
        self.sizes_layout.addWidget(self.add_size_btn)
        self.sizes_layout.addWidget(self.remove_size_btn)
        self.layout.addLayout(self.sizes_layout)

        # Move or copy original
        self.move_checkbox = QCheckBox("Mover imagen original")
        self.move_checkbox.setChecked(True)
        self.layout.addWidget(self.move_checkbox)

        # Start button
        self.start_btn = QPushButton("Iniciar Procesamiento")
        self.start_btn.clicked.connect(self.start_processing)
        self.layout.addWidget(self.start_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.input_paths = []
        self.sizes = [512, 256, 128, 64, 48, 32, 24, 16]

        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def browse_input(self):
        choice = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Entrada") or QFileDialog.getOpenFileNames(self, "Seleccionar Archivos de Imagen", "", "Images (*.png *.bmp *.jpeg *.jpg)")[0]
        if isinstance(choice, str) and choice:  # Directory selected
            valid_extensions = ('.png', '.bmp', '.jpeg', '.jpg')
            self.input_paths = [os.path.join(choice, f) for f in os.listdir(choice) if f.lower().endswith(valid_extensions)]
            self.input_field.setText(choice)
            self.input_field.setToolTip("Directorio seleccionado")
        elif isinstance(choice, list) and choice:  # Files selected
            self.input_paths = choice
            count = len(choice)
            text = f"{count} imagen{'es' if count != 1 else ''} seleccionada{'s' if count != 1 else ''}"
            self.input_field.setText(text)
            self.input_field.setToolTip("\n".join(choice))
        if not self.input_paths:
            QMessageBox.warning(self, "Advertencia", "No se encontraron imágenes válidas.")

    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Salida")
        if directory:
            self.output_field.setText(directory)

    def add_size(self):
        size_text = self.sizes_combo.currentText().strip()
        if size_text.isdigit():
            size = int(size_text)
            if size not in self.sizes:
                self.sizes.append(size)
                self.sizes.sort(reverse=True)
                self.sizes_combo.addItem(size_text)
                self.sizes_combo.setCurrentText("")
            else:
                QMessageBox.warning(self, "Advertencia", "El tamaño ya existe.")
        else:
            QMessageBox.warning(self, "Advertencia", "Ingrese un número válido.")

    def remove_size(self):
        index = self.sizes_combo.currentIndex()
        if index >= 0:
            size = int(self.sizes_combo.currentText())
            self.sizes.remove(size)
            self.sizes_combo.removeItem(index)

    def start_processing(self):
        if not self.input_paths:
            QMessageBox.warning(self, "Advertencia", "Seleccione archivos o directorio de entrada.")
            return

        # Filtrado adicional para validar imágenes
        valid_paths = []
        for path in self.input_paths:
            try:
                with Image.open(path) as img:
                    img.verify()  # Verifica sin cargar toda la imagen
                valid_paths.append(path)
            except Exception as e:
                self.log_text.append(f"Archivo omitido (no válido): {os.path.basename(path)} - Error: {e}")

        if not valid_paths:
            QMessageBox.warning(self, "Error", "Ninguna imagen válida encontrada.")
            return

        self.input_paths = valid_paths

        output_dir = self.output_field.text()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear directorio de salida: {e}")
                return
        if not self.sizes:
            QMessageBox.warning(self, "Advertencia", "Añada al menos un tamaño.")
            return

        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.start_btn.setEnabled(False)

        self.thread = ImageProcessorThread(self.input_paths, output_dir, self.sizes, self.move_checkbox.isChecked())
        self.thread.progress.connect(self.update_progress)
        self.thread.log.connect(self.update_log)
        self.thread.finished.connect(self.processing_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_text.append(message)

    def processing_finished(self):
        self.start_btn.setEnabled(True)
        QMessageBox.information(self, "Completado", "Procesamiento finalizado.")

# Función para obtener la ruta correcta tanto en desarrollo como en .exe
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, funciona en dev y en PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # En modo desarrollo (python main.qt6.py), usa el directorio actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Carga el icono con la ruta segura
    icon_path = resource_path("app_icon.ico")
    app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec())