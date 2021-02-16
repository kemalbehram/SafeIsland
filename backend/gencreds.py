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

# For the data models
from typing import Dict, Optional, Union, cast
from pydantic import BaseModel, BaseSettings

# The settings
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

def unbake(image):
    """
    Return the SafeIsland content contained in a baked PNG file.
    If this doesn't work, return None.
    """

    # Prepare to read from the image (could be a file name, a stream or a byte array)
    reader = png.Reader(image)

    # Iterate over all chunks in the image and return the iTXt one starting with "safeisland"
    for chunktype, content in reader.chunks():
        if chunktype == b'iTXt' and content.startswith(b'openbadges\x00'):
#            return re.sub(b'safeisland[\x00]+', b'', content).decode('utf8')
            chunk = re.sub(b'openbadges[\x00]+', b'', content)
            decoded = json.loads(chunk)
            return decoded


def bake(image, assertion_string: str, newfile=None):
    """
    Embeds a serialized representation of a badge instance in a PNG image file.
    """
#    encoded_assertion_string = codecs.getwriter('utf-8')(assertion_string)

    # Prepare to read from the image (could be a file name, a stream or a byte array)
    reader = png.Reader(image)

    if newfile is None:
        newfile = "baked.png"

    chunkheader = b'openbadges\x00\x00\x00\x00\x00'
    chunk_content = chunkheader + bytes(assertion_string, encoding="utf-8")
    badge_chunk = (b'iTXt', chunk_content)

    with open(newfile, "wb") as newFileStream:
        png.write_chunks(newFileStream, baked_chunks(reader.chunks(), badge_chunk))

    return


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



assertion = json.dumps({"key": "Fantastico, eso parece"})
bake("baked.png", assertion, newfile="baked2.png")
res = unbake("baked2.png")
print(res)