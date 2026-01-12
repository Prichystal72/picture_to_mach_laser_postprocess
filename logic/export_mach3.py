from PIL import Image

def export_image_to_mach3(image: Image.Image, output_path: str, mm_per_pixel: float = 0.15, max_power: int = 1000):
    grayscale = image.convert("L")
    width, height = grayscale.size
    lines = []
    for y in range(height):
        ypos = f"{y * mm_per_pixel:.3f}"
        for x in range(width):
            xpos = f"{x * mm_per_pixel:.3f}"
            pixel = grayscale.getpixel((x, y))
            power = int(max_power * (1 - pixel / 255))
            lines.append(f"G1 X{xpos} Y{ypos} M3 S{power} ; px({x},{y})")
    # Info o kroku a rozměrech na začátek souboru
    header = [
        f"; mm_per_pixel: {mm_per_pixel}",
        f"; width: {width} px, height: {height} px",
        f"; physical size: {width * mm_per_pixel:.3f} x {height * mm_per_pixel:.3f} mm",
        f"; max_power: {max_power}",
        ""
    ]
    with open(output_path, "w") as f:
        f.write("\n".join(header + lines))
