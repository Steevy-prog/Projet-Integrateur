from PIL import Image
def extract_data(image_path):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    binary_data = ''
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    # Split into 8-bit chunks
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ''
    for char in chars:
        if char == '11111110':  # delimiter
            break
        message += chr(int(char, 2))
    return message

# Usage:
hidden_key = extract_data("output.png")
print("Hidden Key:", hidden_key)