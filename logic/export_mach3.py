from PIL import Image

def export_image_to_mach3(image: Image.Image, output_path: str, mm_per_pixel: float = 0.15, max_power: int = 1000, feedrate: int = 1200):
    """
    Exportuje obrázek do G-code pro Mach3.
    mm_per_pixel: velikost bodu laseru v mm (průměr jednoho pixelu)
    """
    grayscale = image.convert("L")
    width, height = grayscale.size
    lines = []
    first_g1 = True
    for y in range(height):
        ypos = y * mm_per_pixel
        for x in range(width):
            xpos = x * mm_per_pixel
            pixel = grayscale.getpixel((x, y))
            power = int(max_power * (1 - pixel / 255))
            if first_g1:
                lines.append(f"G1 X{xpos:.3f} Y{ypos:.3f} F{feedrate} M3 S{power} ; px({x},{y})")
                first_g1 = False
            else:
                lines.append(f"G1 X{xpos:.3f} Y{ypos:.3f} M3 S{power} ; px({x},{y})")
    # Info o kroku a rozměrech na začátek souboru
    import datetime
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = [
        f"; Autor: Jaroslav Prichystal",
        f"; Datum: {now}",
        "; Mach3 G-code header",
        "G21 ; jednotky v mm",
        "G90 ; absolutni polohovani",
        "M5  ; vypnout laser",
        "G0 X0 Y0 ; navrat na pocatek",
        "",
        f"; mm_per_pixel: {mm_per_pixel}",
        f"; width: {width} px, height: {height} px",
        f"; physical size: {width * mm_per_pixel:.3f} x {height * mm_per_pixel:.3f} mm",
        f"; max_power: {max_power}",
        ""
    ]
    with open(output_path, "w") as f:
        f.write("\n".join(header + lines))
