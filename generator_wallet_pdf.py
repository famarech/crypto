import os
import ecdsa
import hashlib
import base58
import qrcode
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image




# Fonction pour formater les clés et l'adresse
def format_with_spaces(data):
    return ' '.join(data[i:i+4] for i in range(0, len(data), 4))




# Générer les QR codes
def create_qr(data, filename):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)
    return filename




# Générer les codes-barres
def create_barcode(data, filename):
    barcode = Code128(data, writer=ImageWriter())
    barcode.save(filename)
    return filename





# Générer une clé privée
private_key = os.urandom(32)
# Créer une clé publique à partir de la clé privée
sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
vk = sk.get_verifying_key()
public_key = b'\x04' + vk.to_string()

# Générer une adresse Bitcoin à partir de la clé publique
sha256_1 = hashlib.sha256(public_key).digest()
ripemd160 = hashlib.new('ripemd160')
ripemd160.update(sha256_1)
hashed_public_key = ripemd160.digest()
mainnet_public_key = b'\x00' + hashed_public_key
checksum = hashlib.sha256(hashlib.sha256(mainnet_public_key).digest()).digest()[:4]
address = base58.b58encode(mainnet_public_key + checksum).decode()

# Formater les clés et l'adresse
formatted_private_key = private_key.hex()
formatted_public_key = public_key.hex()
formatted_address = address

# qr_private_key = create_qr(formatted_private_key, "private_key_qr.png")
# qr_public_key = create_qr(formatted_public_key, "public_key_qr.png")
qr_address = create_qr(formatted_address, "address_qr.png")

# barcode_private_key = create_barcode(formatted_private_key, "private_key_barcode")
# barcode_public_key = create_barcode(formatted_public_key, "public_key_barcode")
barcode_address = create_barcode(formatted_address, "address_barcode")

# Créer un PDF en mode paysage et ajouter les informations
pdf_filename = "bitcoin_wallet.pdf"
c = canvas.Canvas(pdf_filename, pagesize=landscape(letter))
width, height = landscape(letter)

# Ajouter les clés et l'adresse au PDF
c.drawString(72, height - 72, "Clé Privée:")
c.drawString(72, height - 90, format_with_spaces(formatted_private_key))

c.drawString(72, height - 130, "Clé Publique:")
c.drawString(72, height - 148, format_with_spaces(formatted_public_key))

c.drawString(72, height - 188, "Adresse Bitcoin:")
c.drawString(72, height - 206, format_with_spaces(formatted_address))

# Ajouter les QR codes au PDF
qr_size = 2 * inch  # Taille des QR codes
# c.drawImage(qr_private_key, 72, height - 250, width=qr_size, height=qr_size)
# c.drawImage(qr_public_key, 72, height - 350, width=qr_size, height=qr_size)
c.drawImage(qr_address, 72, height - 450, width=qr_size, height=qr_size)

# Ajouter les codes-barres au PDF
barcode_width = 4 * inch  # Largeur des codes-barres
barcode_height = 1 * inch  # Hauteur des codes-barres
# c.drawImage(barcode_private_key + ".png", 72, height - 550, width=barcode_width, height=barcode_height)
# c.drawImage(barcode_public_key + ".png", 72, height - 650, width=barcode_width, height=barcode_height)
c.drawImage(barcode_address + ".png", 72, height - 750, width=barcode_width, height=barcode_height)

c.save()

print(f"PDF created: {pdf_filename}")
