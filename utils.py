import qrcode
from io import BytesIO


def gerar_imagem_qrcode(url):
    """Gera um QR Code a partir de uma URL e retorna os bytes da imagem."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()