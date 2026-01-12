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
        # Rychlost pohybu (feedrate)
        feed_layout = QHBoxLayout()
        feed_layout.addWidget(QLabel("Rychlost (mm/min):"))
        self.feedrate_spin = QDoubleSpinBox()
        self.feedrate_spin.setRange(10, 10000)
        self.feedrate_spin.setValue(1200)
        self.feedrate_spin.setSingleStep(10)
        feed_layout.addWidget(self.feedrate_spin)
        controls_layout.addLayout(feed_layout)
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


        # Velikost bodu laseru v mm
        laser_dot_layout = QHBoxLayout()
        laser_dot_layout.addWidget(QLabel("Velikost bodu laseru (mm):"))
        self.laser_dot_size_spin = QDoubleSpinBox()
        self.laser_dot_size_spin.setRange(0.01, 10.0)
        self.laser_dot_size_spin.setValue(0.15)
        self.laser_dot_size_spin.setSingleStep(0.01)
        laser_dot_layout.addWidget(self.laser_dot_size_spin)
        controls_layout.addLayout(laser_dot_layout)

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

        # Nastavení bodu laseru (počátek X, Y v mm)
        laser_origin_layout = QHBoxLayout()
        laser_origin_layout.addWidget(QLabel("Počátek X (mm):"))
        self.laser_origin_x_spin = QDoubleSpinBox()
        self.laser_origin_x_spin.setRange(-1000, 1000)
        self.laser_origin_x_spin.setValue(0.0)
        self.laser_origin_x_spin.setSingleStep(0.1)
        laser_origin_layout.addWidget(self.laser_origin_x_spin)
        laser_origin_layout.addWidget(QLabel("Y (mm):"))
        self.laser_origin_y_spin = QDoubleSpinBox()
        self.laser_origin_y_spin.setRange(-1000, 1000)
        self.laser_origin_y_spin.setValue(0.0)
        self.laser_origin_y_spin.setSingleStep(0.1)
        laser_origin_layout.addWidget(self.laser_origin_y_spin)
        controls_layout.addLayout(laser_origin_layout)
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
                # Použijeme velikost bodu laseru v mm převedenou na pixely podle aktuálního rozlišení
                width, target_width_mm = img.size[0], self.target_width_spin.value()
                mm_per_pixel = target_width_mm / width if width > 0 else 1
                pixel_size = max(1, int(round(self.laser_dot_size_spin.value() / mm_per_pixel)))
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
                dot_size_mm = self.laser_dot_size_spin.value()
                # Převzorkování obrázku podle velikosti bodu laseru
                new_width = int(target_width_mm / dot_size_mm)
                new_height = int((height / width) * new_width)
                resampled_img = self.current_image.resize((new_width, new_height), Image.NEAREST)
                feedrate = int(self.feedrate_spin.value())
                export_mach3.export_image_to_mach3(
                    resampled_img, output_path, dot_size_mm, max_power, feedrate
                )
                # Simulace výsledného obrázku (náhled laserování)
                # Po exportu načíst G-code a vykreslit simulaci vypálení
                info_text = f"Export hotov: {output_path}<br>Rozměr: {physical_width:.2f} x {physical_height:.2f} mm<br>Max. výkon: S{max_power}<br>Velikost bodu: {dot_size_mm} mm"
                self.display_preview_image(resampled_img.convert('RGB'), info_text=info_text)

    def simulate_from_gcode(self, gcode_path, dot_size_mm):
        # Načte G-code a vykreslí simulaci vypálení (černé body tam, kde S > 0)
        import re
        width = height = None
        mm_per_pixel = None
        try:
            with open(gcode_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('; width:'):
                    m = re.search(r'width: (\d+)', line)
                    if m:
                        width = int(m.group(1))
                if line.startswith('; height:'):
                    m = re.search(r'height: (\d+)', line)
                    if m:
                        height = int(m.group(1))
                if line.startswith('; mm_per_pixel:'):
                    m = re.search(r'mm_per_pixel: ([\d\.]+)', line)
                    if m:
                        mm_per_pixel = float(m.group(1))
                if width and height and mm_per_pixel:
                    break
            if not (width and height and mm_per_pixel):
                raise ValueError('Nepodařilo se načíst rozměry z G-code.')
            from PIL import Image, ImageDraw
            img = Image.new('L', (width, height), 255)
            draw = ImageDraw.Draw(img)
            for line in lines:
                if line.startswith('G1'):
                    m = re.search(r'X([\d\.]+) Y([\d\.]+) M3 S(\d+)', line)
                    if m:
                        x_mm = float(m.group(1))
                        y_mm = float(m.group(2))
                        s = int(m.group(3))
                        if s > 0:
                            x = int(round(x_mm / mm_per_pixel))
                            y = int(round(y_mm / mm_per_pixel))
                            if 0 <= x < width and 0 <= y < height:
                                draw.point((x, y), fill=0)
            return img.convert('RGB')
        except Exception as e:
            from PIL import Image
            # Vytvořit malý obrázek s chybovou hláškou
            img = Image.new('RGB', (400, 100), (255, 255, 255))
            try:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.text((10, 40), f'Chyba simulace G-code: {e}', fill=(255,0,0))
            except Exception:
                pass
            return img

    def display_preview_image(self, img, info_text=None):
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qimage = QImage.fromData(buffer.getvalue(), "PNG")
        pixmap = QPixmap.fromImage(qimage)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        # Pokud je info_text, zobrazit pod obrázkem (jako tooltip)
        if info_text:
            self.label.setToolTip(info_text)
        # Kontrola, zda je obrázek prázdný (vše bílé)
        if hasattr(img, 'getbbox') and img.getbbox() is None:
            self.label.setToolTip("Výsledek je prázdný (žádné body k vypálení).")

    def simulate_laser_result(self, img, max_power):
        # Simulace: tmavší = více vypáleno, světlejší = méně
        # Výsledek bude v odstínech šedi, invertovaný (černá = plný výkon)
        gray = img.convert("L")
        # Simulace: invertovat a zvýraznit kontrast podle výkonu
        result = ImageOps.invert(gray)
        result = ImageEnhance.Contrast(result).enhance(2.0)
        return result.convert("RGB")

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