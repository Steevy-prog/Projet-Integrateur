from PIL import Image

def to_bin(data):
    return ''.join(format(ord(char), '08b') for char in data)

def hide_data(image_path, output_path, secret_key):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    binary_key = to_bin(secret_key) + '1111111111111110'  # delimiter
    data_index = 0
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if data_index < len(binary_key):
                r = (r & ~1) | int(binary_key[data_index])
                data_index += 1
            if data_index < len(binary_key):
                g = (g & ~1) | int(binary_key[data_index])
                data_index += 1
            if data_index < len(binary_key):
                b = (b & ~1) | int(binary_key[data_index])
                data_index += 1
            pixels[x, y] = (r, g, b)
            if data_index >= len(binary_key):
                img.save(output_path)
                print(f"[+] Key hidden in {output_path}")
                return

    print("[-] Image not big enough to hold the key.")

# Usage:
hide_data("image.png", "output.png", "Steevy 15 the MFKN GOAT")