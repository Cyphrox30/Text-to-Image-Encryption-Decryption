from flask import Flask, request, render_template, send_file
from cryptography.fernet import Fernet
from PIL import Image
import os

# Generate encryption key (save this securely for decryption)
key = Fernet.generate_key()
cipher = Fernet(key)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Encrypt text
def encrypt_text(message):
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

# Convert encrypted text to an image
def text_to_image(encrypted_text, output_image="encrypted.png"):
    data = list(encrypted_text)  # Convert bytes to list of integers
    size = int(len(data) ** 0.5) + 1  # Image size calculation

    img = Image.new("RGB", (size, size), "white")
    pixels = img.load()

    idx = 0
    for y in range(size):
        for x in range(size):
            if idx < len(data):
                pixels[x, y] = (data[idx], data[idx], data[idx])  # Store in grayscale
                idx += 1
            else:
                break

    img.save(output_image)
    return output_image

# Extract text from image
def image_to_text(image_path):
    img = Image.open(image_path)
    pixels = list(img.getdata())

    data = bytearray([p[0] for p in pixels if p[0] != 255])  # Extract non-white pixels
    return bytes(data)

# Decrypt text
def decrypt_text(encrypted_text):
    decrypted_message = cipher.decrypt(encrypted_text).decode()
    return decrypted_message

# Flask routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["message"]
        encrypted_text = encrypt_text(text)
        image_path = text_to_image(encrypted_text)

        return send_file(image_path, as_attachment=True)

    return render_template("index2.html")

@app.route("/decode", methods=["POST"])
def decode():
    file = request.files["file"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    encrypted_text = image_to_text(file_path)
    decrypted_text = decrypt_text(encrypted_text)

    return render_template("result.html", decrypted_text=decrypted_text)


if __name__ == "__main__":
    app.run(debug=True)

