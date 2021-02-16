from PIL import Image, ImageDraw, ImageFont, ImageFile
import qrcode
import png
import re
from tempfile import NamedTemporaryFile


def jrm_unbake(image_stream):
    """
    Return the openbadges content contained in a baked PNG file.
    If this doesn't work, return None.

    I uses the iTXt chunk.
    """

    reader = png.Reader(file=image_stream)
    for chunktype, content in reader.chunks():
        if chunktype == b'iTXt' and content.startswith(b'openbadges\x00'):
            return re.sub(b'openbadges[\x00]+', b'', content).decode('utf8')


def jrm_bake_streams(image_stream, assertion_string, newfile_stream=None):

    # Get the input stream from the image
    reader = png.Reader(file=image_stream)

    # Create a temporary file if no output file specified
    if newfile_stream is None:
        newfile_stream = NamedTemporaryFile(suffix='.png')

    # Build the chunk content with the assertion data
    chunkheader = "openbadges\x00\x00\x00\x00\x00"
    chunk_content = chunkheader + assertion_string

    # We are going to write the chunk in the "iTXt" chunk
    badge_chunk = (b'iTXt', chunk_content)

    # Insert our chunk as the second chunk in the image
    original_chunks = reader.chunks()
    final_chunks = []

    # Insert the first original chunk
    final_chunks.append(next(original_chunks))

    # Insert our chunk
    final_chunks.append(badge_chunk)

    # Insert the rest of the original chunks
    for t,c in original_chunks:
        final_chunks.append((t,c))

    # Write the new chunks into a new PNG file
    png.write_chunks(newfile_stream, final_chunks)

    newfile_stream.seek(0)
    return newfile_stream


def jrm_bake(input_file: str, assertion: str, output_file: str):

    with open(input_file, "rb") as inputs:
        with open(output_file, "wb") as outs:
            output = jrm_bake_streams(inputs, assertion, outs)


def create_image():

    # create an image
    out = Image.new("RGB", (500, 400), "#003000")

    # get a font
    fntSmall = ImageFont.truetype("arial.ttf", 20)
    fntBig = ImageFont.truetype("arial.ttf", 26)
    fntHuge = ImageFont.truetype("arial.ttf", 45)
    # get a drawing context
    d = ImageDraw.Draw(out)


    orgX = 60
    orgY = 110
    smallLineHeight = 30
    bigLineHeight = 90

    d.text((130, 20), "Safe Island", font=fntHuge, fill=(255, 255, 255))

    d.text((orgX,orgY), "Name", font=fntSmall, fill=(255, 255, 255))
    d.text((orgX,orgY + 0*bigLineHeight + smallLineHeight), "USOBIAGA/VICTOR", font=fntBig, fill=(255, 255, 255))

    d.text((orgX,orgY + bigLineHeight), "Date", font=fntSmall, fill=(255, 255, 255))
    d.text((orgX,orgY + 1*bigLineHeight + smallLineHeight), "2020-10-07 11:05:47", font=fntBig, fill=(255, 255, 255))

    d.text((orgX,orgY + 2*bigLineHeight), "Result", font=fntSmall, fill=(255, 255, 255))
    d.text((orgX,orgY + 2*bigLineHeight + smallLineHeight), "FREE", font=fntBig, fill=(255, 255, 255))

    d.text((orgX + 150,orgY + 2*bigLineHeight), "Test ID", font=fntSmall, fill=(255, 255, 255))
    d.text((orgX + 150,orgY + 2*bigLineHeight + smallLineHeight), "VRL1234567890", font=fntBig, fill=(255, 255, 255))

    out.show()
    out.save()


input_name = "template.png"
output_name = "perico2.png"

jrm_bake(input_name, "Este es el segundo Hola que tal", output_name)
