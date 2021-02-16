from PIL import Image
import qrcode

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
    template = Image.open("templateRGB.png")

    # The postion of the upper-left corner of QR in the template image
    x = 512
    y = 85
    box = (x, y, x + QRsize, y + QRsize)

    # Paste the resized QR in the white space of the template
    template.paste(resized, box)

    return template


qr = genQR_DECONFIANZA(
    'https://ipfs.hesusruiz.org/'
)

# Show the final image
qr.show()
