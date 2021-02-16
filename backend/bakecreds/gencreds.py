import os
import io
import csv
import json

#from unidecode import unidecode

from PIL import Image
import qrcode

import codecs
import hashlib
from io import BytesIO, StringIO
import itertools
import os.path
import png
import re
from tempfile import NamedTemporaryFile

from settings import settings

base_name = "promociones"
output_dir = "baked/"

def genQR_DECONFIANZA(data="Hola"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#3241B4", back_color="white")

    # Get the underlying PIL image content
    qrimg = img._img

    # Resize the QR image
    QRsize = 410
    resized = qrimg.resize((QRsize, QRsize), resample=Image.LANCZOS)

    # Open the template image
    template = Image.open(base_name + ".png")

    # The postion of the upper-left corner of QR in the template image
    x = 512
    y = 85
    box = (x, y, x + QRsize, y + QRsize)

    # Paste the resized QR in the white space of the template
    template.paste(resized, box)

    return template

def unbake(imageFile):
    """
    Return the openbadges content contained in a baked PNG file.
    If this doesn't work, return None.

    If there is both an iTXt and tEXt chunk with keyword openbadges,
    the iTXt chunk content will be returned.
    """

    reader = png.Reader(file=imageFile)
    for chunktype, content in reader.chunks():
        if chunktype == b'iTXt' and content.startswith(b'openbadges\x00'):
            return re.sub(b'openbadges[\x00]+', b'', content).decode('utf8')
        elif chunktype == b'tEXt' and content.startswith(b'openbadges\x00'):
            return content.split('\x00')[1].decode('utf8')


def bake(image_stream, assertion_string, newfile=None):
    """
    Embeds a serialized representation of a badge instance in a PNG image file.
    """
    encoded_assertion_string = codecs.getwriter('utf-8')(assertion_string)
    reader = png.Reader(file=image_stream)

    if newfile is None:
        newfile = NamedTemporaryFile(suffix='.png')

    chunkheader = b'openbadges\x00\x00\x00\x00\x00'
    chunk_content = chunkheader + encoded_assertion_string.stream.encode('utf-8')
    badge_chunk = (b'iTXt', chunk_content)
    png.write_chunks(newfile, baked_chunks(reader.chunks(), badge_chunk))

    newfile.seek(0)
    return newfile


def baked_chunks(original_chunks, badge_chunk):
    """
    Returns an iterable of chunks that places the Open Badges baked chunk
    and filters out any previous Open Badges chunk that may have existed.
    """
    def is_not_previous_assertion(chunk):
        if chunk[1].startswith(b'openbadges\x00'):
            return False
        return True

    first_slice = next(original_chunks)
    last_slice = list(filter(
        is_not_previous_assertion,
        original_chunks
    ))

    return itertools.chain([first_slice], [badge_chunk], last_slice)


def bake_promocion(promocion, nombre, input_image_stream):


    # We use the field "Nombre" as the name of the file, stripped from blanks and lowercase
    output_imagefile = output_dir + nombre + ".png"
    output_jsonfile = output_dir + nombre + ".json"

    assertions = json.dumps(promocion, skipkeys=False, ensure_ascii=False,
            indent=2, separators=None, sort_keys=False)

    # Bake the assertions inside the image file
    with open(output_imagefile, "wb") as baked_file:
        output = bake(input_image_stream, assertions, baked_file)

    # Also write the JSON file for reference
    with open(output_jsonfile, "w", encoding="utf-8") as jsonfile:
        jsonfile.write(assertions)

def get_full_credential(promocion):
    with open(base_name + ".json") as template_file:
        template = json.load(template_file)
    # Replace the "Promocion" field with our concrete value
    template["vc"]["credentialSubject"]["Promocion"] = promocion
    return template

def add_fields(fields):
    promocion = {}
    promocion["Nombre"] = fields[1]

    promocion["Ayuntamiento"] = fields[2]
    promocion["AyuntamientoDID"] = ""

    promocion["Arquitecto"] = fields[3]
    promocion["ArquitectoDID"] = ""

    promocion["Comercializadora"] = fields[4]
    promocion["ComercializadoraDID"] = ""

    promocion["Constructora"] = fields[5]
    promocion["ConstructoraDID"] = ""

    promocion["Banco"] = fields[6]
    promocion["BancoDID"] = ""

    promocion["Link"] = fields[0]

    return promocion

fieldnames = ["Link", "Nombre", "Ayuntamiento", "Arquitecto", "Comercializadora", "Constructora", "Banco"]

# Open the CSV file, making sure that the encoding it UTF-8
with open(base_name + '.csv', mode="r", encoding='utf-8') as csvfile:

    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)

    # Skip the first line with the headers
    first = True
    for line in csvfile:
        if first == True:
            first = False
            continue
        fields = line.split(sep=",", maxsplit=7)
        promocion = add_fields(fields)

        # We use the field "Nombre" as the name of the file, stripped from blanks and lowercase
        nombre = promocion["Nombre"].replace(" ", "").lower()
#        nombre = unidecode(nombre)

        promocion = get_full_credential(promocion)

        # Pre-generate the image with the QR for the promotion
        qr = genQR_DECONFIANZA(
            'https://ipfs.hesusruiz.org/prom/' + nombre
        )

        # Get the compressed image data in memory in bytes format
        image_stream = io.BytesIO()
        qr.save(image_stream, format="png")

        # Reset to the beginning of the stream
        image_stream.seek(0)

        bake_promocion(promocion, nombre, image_stream)
        print(f"Created Verifiable Credential QR image for: {nombre}")



