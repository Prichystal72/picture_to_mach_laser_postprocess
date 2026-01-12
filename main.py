from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QSlider, QCheckBox, QFontDialog, QSpinBox, QComboBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PIL import Image, ImageEnhance, ImageOps
import io
from PySide6.QtGui import QImage
import logic.export_mach3 as export_mach3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bitmap Editor and Laser Code Generator")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("assets/icon.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout: horizontal (left: controls, right: image)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Controls (left panel)
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        main_layout.addWidget(controls_widget, 0)

        self.load_button = QPushButton("Načíst obrázek")
        self.load_button.setStyleSheet("padding: 10px; font-size: 16px;")
        controls_layout.addWidget(self.load_button)

        self.export_button = QPushButton("Export do Mach3")
        self.export_button.setStyleSheet("padding: 10px; font-size: 16px;")
        controls_layout.addWidget(self.export_button)

        controls_layout.addSpacing(20)

        controls_layout.addWidget(QLabel("Jas"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setStyleSheet("padding: 10px;")
        controls_layout.addWidget(self.brightness_slider)

        controls_layout.addWidget(QLabel("Kontrast"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setStyleSheet("padding: 10px;")
        controls_layout.addWidget(self.contrast_slider)

        # Checkboxes for stepwise edits
        self.cb_grayscale = QCheckBox("Převod na odstíny šedi")
        self.cb_bw = QCheckBox("Převod na černobílý (prahování)")
        self.cb_dither = QCheckBox("Novinový (dithering)")
        self.cb_ascii = QCheckBox("ASCII art")
        self.cb_invert = QCheckBox("Invertovat barvy")
        controls_layout.addWidget(self.cb_grayscale)
        controls_layout.addWidget(self.cb_bw)
        controls_layout.addWidget(self.cb_dither)
        controls_layout.addWidget(self.cb_ascii)
        controls_layout.addWidget(self.cb_invert)
        self.cb_grayscale.stateChanged.connect(self.on_slider_change)
        self.cb_bw.stateChanged.connect(self.on_slider_change)
        self.cb_dither.stateChanged.connect(self.on_slider_change)
        self.cb_ascii.stateChanged.connect(self.on_slider_change)
        self.cb_invert.stateChanged.connect(self.on_slider_change)

        # ASCII font/size controls
        ascii_font_layout = QHBoxLayout()
        self.ascii_font_button = QPushButton("Nastavit font")
        self.ascii_font_button.setStyleSheet("font-size: 10pt;")
        self.ascii_font_button.clicked.connect(self.choose_ascii_font)
        ascii_font_layout.addWidget(self.ascii_font_button)
        ascii_font_layout.addWidget(QLabel("Velikost písma:"))
        self.ascii_font_size = QSpinBox()
        self.ascii_font_size.setRange(6, 32)
        self.ascii_font_size.setValue(10)
        self.ascii_font_size.valueChanged.connect(self.on_slider_change)
        ascii_font_layout.addWidget(self.ascii_font_size)
        controls_layout.addLayout(ascii_font_layout)
        self.ascii_font_family = 'Consolas'

        # Pixel size for newspaper effect
        self.pixel_size_combo = QComboBox()
        self.pixel_size_combo.addItems(["1", "2", "4", "8", "16"])
        self.pixel_size_combo.setCurrentIndex(0)
        self.pixel_size_combo.setEditable(False)
        self.pixel_size_combo.setMaximumWidth(60)
        self.pixel_size_combo.currentIndexChanged.connect(self.on_slider_change)
        pixel_layout = QHBoxLayout()
        pixel_layout.addWidget(QLabel("Velikost bodu:"))
        pixel_layout.addWidget(self.pixel_size_combo)
        controls_layout.addLayout(pixel_layout)

        # Výsledný rozměr X (mm)
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Výsledná šířka X (mm):"))
        self.target_width_spin = QDoubleSpinBox()
        self.target_width_spin.setRange(1, 1000)
        self.target_width_spin.setValue(40.0)
        self.target_width_spin.setSingleStep(1.0)
        self.target_width_spin.valueChanged.connect(self.on_slider_change)
        size_layout.addWidget(self.target_width_spin)
        controls_layout.addLayout(size_layout)
        # Práh výkonu
        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Max. výkon (S):"))
        self.max_power_spin = QDoubleSpinBox()
        self.max_power_spin.setRange(1, 1000)
        self.max_power_spin.setValue(1000)
        self.max_power_spin.setSingleStep(10)
        self.max_power_spin.valueChanged.connect(self.on_slider_change)
        power_layout.addWidget(self.max_power_spin)
        controls_layout.addLayout(power_layout)

        controls_layout.addStretch(1)

        # Image display (right panel)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background: #222; border: 1px solid #444;")
        main_layout.addWidget(self.label, 1)

        # State
        self.original_image = None  # PIL.Image
        self.current_image = None   # PIL.Image
        self.brightness = 0
        self.contrast = 0

        # Connections
        self.load_button.clicked.connect(self.load_image)
        self.export_button.clicked.connect(self.export_laser_code)
        self.brightness_slider.valueChanged.connect(self.on_slider_change)
        self.contrast_slider.valueChanged.connect(self.on_slider_change)

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.bmp)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.original_image = Image.open(file_path).convert("RGB")
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(0)
            self.brightness = 0
            self.contrast = 0
            self.update_image()

    def display_image(self):
        if self.current_image:
            buffer = io.BytesIO()
            self.current_image.save(buffer, format="PNG")
            qimage = QImage.fromData(buffer.getvalue(), "PNG")
            pixmap = QPixmap.fromImage(qimage)
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)
        else:
            self.label.setText("Načtěte obrázek...")

    def on_slider_change(self):
        self.brightness = self.brightness_slider.value()
        self.contrast = self.contrast_slider.value()
        self.update_image()

    def choose_ascii_font(self):
        font, ok = QFontDialog.getFont()
        if ok and hasattr(font, 'family'):
            self.ascii_font_family = font.family()
            self.on_slider_change()

    def update_image(self):
        if self.original_image:
            img = self.original_image.copy()
            if self.brightness != 0:
                img = ImageEnhance.Brightness(img).enhance(1 + self.brightness / 100)
            if self.contrast != 0:
                img = ImageEnhance.Contrast(img).enhance(1 + self.contrast / 100)
            # Apply grayscale
            if self.cb_grayscale.isChecked():
                img = img.convert("L")
            # Apply B/W threshold
            if self.cb_bw.isChecked():
                img = img.convert("L")
                img = img.point(lambda x: 0 if x < 128 else 255, '1')
            # Apply dithering (novinový)
            if self.cb_dither.isChecked():
                pixel_size = int(self.pixel_size_combo.currentText())
                img = self.pixelate(img, pixel_size)
            # Invert colors
            if self.cb_invert.isChecked():
                if img.mode == "1":
                    img = img.convert("L")
                img = ImageOps.invert(img.convert("RGB") if img.mode != "RGB" else img)
            # ASCII art preview (show as text in label)
            if self.cb_ascii.isChecked():
                ascii_str = self.image_to_ascii(img)
                self.label.setPixmap(QPixmap())
                font_css = f"font-family: '{self.ascii_font_family}', monospace; font-size: {self.ascii_font_size.value()}pt;"
                self.label.setText(f"<pre style='background:#222; color:#fff; {font_css}'>" + ascii_str + "</pre>")
                self.label.setStyleSheet("background: #222; color: #fff; border: 1px solid #444;")
                return
            # Zobrazit PIL obrázek v QLabel
            self.current_image = img.convert("RGB") if img.mode != "RGB" else img
            self.display_image()
            self.label.setStyleSheet("background: #222; border: 1px solid #444;")

    def image_to_ascii(self, img, width=80):
        chars = "@%#*+=-:. "
        img = img.convert("L")
        w, h = img.size
        aspect = h / w
        new_h = max(1, int(width * aspect * 0.5))
        img = img.resize((width, new_h))
        # Use get_flattened_data for Pillow >= 10.3.0
        try:
            pixels = list(img.get_flattened_data())
        except AttributeError:
            pixels = list(img.getdata())
        ascii_str = ""
        for i in range(len(pixels)):
            if i % width == 0 and i != 0:
                ascii_str += "\n"
            ascii_str += chars[pixels[i] * (len(chars)-1) // 255]
        return ascii_str

    def export_laser_code(self):
        if self.current_image:
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("G-code (*.nc)")
            file_dialog.setDefaultSuffix("nc")
            if file_dialog.exec():
                output_path = file_dialog.selectedFiles()[0]
                # Výpočet mm na pixel podle cílové šířky
                width, height = self.current_image.size
                target_width_mm = self.target_width_spin.value()
                mm_per_pixel = target_width_mm / width
                physical_width = width * mm_per_pixel
                physical_height = height * mm_per_pixel
                max_power = int(self.max_power_spin.value())
                export_mach3.export_image_to_mach3(self.current_image, output_path, mm_per_pixel, max_power)
                self.label.setText(f"Export hotov: {output_path}\nRozměr: {physical_width:.2f} x {physical_height:.2f} mm\nMax. výkon: S{max_power}")

    def setup_export_button(self):
        self.export_button.clicked.connect(self.export_laser_code)

    def pixelate(self, img, pixel_size):
        # Convert to grayscale and dither
        img = img.convert("1")
        w, h = img.size
        if pixel_size <= 1:
            return img
        # Downsample and upsample to create pixel blocks
        img_small = img.resize((w // pixel_size, h // pixel_size), resample=Image.NEAREST)
        img_pixel = img_small.resize((w, h), Image.NEAREST)
        return img_pixel

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()