"""
prep_photo.py
Prepara uma foto para virar ASCII art legível:
  1. Remove o fundo (rembg) para isolar o sujeito.
  2. Aplica CLAHE (OpenCV) para dar contraste local real (luz/sombra).
  3. Compõe sobre fundo branco puro (o branco mapeia para o espaço em branco
     na rampa de caracteres ASCII).
  4. Salva em escala de cinza: source-prepped.png

Uso:
    python scripts/prep_photo.py caminho/para/foto.jpg
"""
import sys
import io
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png") -> None:
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 1. Remove o fundo -> PNG com canal alfa
    result_bytes = remove(input_bytes)
    rgba = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # 2. Compõe sobre fundo branco puro usando o canal alfa como máscara
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. Converte para escala de cinza e aplica CLAHE (contraste local)
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    # 4. Salva o resultado
    Image.fromarray(contrasted).save(output_path)
    print(f"[prep_photo] salvo em {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python scripts/prep_photo.py <foto.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
