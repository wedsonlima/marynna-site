#!/usr/bin/env python3
"""Gera os ícones do site: favicon.svg, favicon.ico e apple-touch-icon.png.

    python3 _fonte/icones.py

Roda separado do build, como og.py: a marca só muda quando alguém decide
mudá-la. O build apenas escreve as tags <link> que apontam para estes arquivos.

A marca é a mesma do cabeçalho (.mono no styles.css) e a mesma do cartão de
compartilhamento, em dois estados de tamanho:

    16-48 px   M sozinho, a sangria, sobre o quadrado de tinta
    180 px     MP dentro da moldura de fio, como no .mono e no og.py

O M sozinho não é um segundo desenho: é o mesmo selo com uma letra a menos.
"MP" a 16 px vira mancha — as duas letras ficam com sete pixels de largura
cada e os serifas da Fraunces somem. Medido antes de decidir. A 180 px, onde
a moldura e as duas letras cabem, a marca volta inteira.

As letras saem em contorno, extraídas do woff2 do próprio repositório, e não
como <text font-family="…">: favicon com nome de fonte depende da fonte
instalada na máquina de quem visita, e a Fraunces não está instalada em
lugar nenhum. Contorno renderiza igual em todo lugar.
"""
import io
import struct
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
DIST = ROOT.parent

# Mesmas variáveis do styles.css.
INK = "#0F1D18"
PAPER = "#F6F4EE"
BRASS = "#5C4A18"          # acento sobre papel — 7,8:1
BRASS_SOFT = "#D6C599"     # acento sobre escuro — 10:1

# A Fraunces do site anda de 300 a 500. O ícone pequeno usa 600 porque peso
# maior é compensação óptica de tamanho pequeno, não outra tipografia: é o que
# o eixo opsz faria se este recorte da fonte o expusesse. A 16 px o peso 400
# acinzenta e o 700 fecha os contra-formas do M — 600 é o ponto entre os dois.
PESO_PEQUENO = 600
PESO_GRANDE = 500          # 180 px: o peso do .mono no cabeçalho

# Altura de maiúscula sobre o lado do quadrado. 0,70 encosta nas bordas e
# 0,54 deixa o selo vazio; 0,62 é o ar do .mono sem a moldura.
ALTURA_M = 0.62

SUPER = 8                  # fator de supersampling dos PNG


def fraunces(peso):
    """Fraunces fixada num peso, pronta para desenhar contorno ou rasterizar."""
    f = TTFont(ROOT / "fraunces-latin-wght-normal.woff2")
    f.flavor = None
    return instancer.instantiateVariableFont(f, {"wght": peso})


def ttf(font):
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def contorno(font, texto):
    """Path SVG do texto e a caixa da tinta, em unidades da fonte (y p/ cima).

    A caixa é a da tinta, não a da largura de avanço: o M tem lateral
    inclinada e sobra de avanço dos dois lados, então centralizar pelo avanço
    deixa a letra visivelmente fora do meio num quadrado de 16 px.

    As coordenadas saem arredondadas para inteiro. Interpolar a fonte variável
    num peso intermediário devolve casas decimais até a décima sexta — 3,5 KB
    de path para uma letra só. A fonte tem 2000 unidades por em e o desenho
    ocupa 32: uma unidade vale 0,014 px, ou seja, o arredondamento acontece
    duas ordens de grandeza abaixo do pixel.
    """
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    pen = SVGPathPen(gs, ntos=lambda v: str(round(v)))
    x = 0.0
    caixa = None
    for ch in texto:
        gn = cmap[ord(ch)]
        gs[gn].draw(TransformPen(pen, (1, 0, 0, 1, x, 0)))
        bp = BoundsPen(gs)
        gs[gn].draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            caixa = (bx0 + x, by0, bx1 + x, by1) if caixa is None else (
                min(caixa[0], bx0 + x), min(caixa[1], by0),
                max(caixa[2], bx1 + x), max(caixa[3], by1))
        x += hmtx[gn][0]
    return pen.getCommands(), caixa


def selo_svg(lado=32):
    """O selo pequeno: M a sangria no quadrado, com o par claro/escuro.

    O <style> troca as cores quando a moldura do navegador é escura — sobre
    barra de abas escura, um quadrado quase preto vira buraco. Os dois estados
    já existem no site: .mono é latão sobre papel, .on-dark .mono é latão
    claro sobre tinta. Aqui é a mesma inversão, escolhida pelo navegador.

    As cores também ficam em atributo de apresentação, que tem precedência
    menor que a regra CSS: renderizador que ignore o <style> — Safari antigo —
    cai no estado claro em vez de ficar sem cor nenhuma.
    """
    font = fraunces(PESO_PEQUENO)
    d, (x0, y0, x1, y1) = contorno(font, "M")
    s = (lado * ALTURA_M) / (y1 - y0)
    tx = (lado - (x1 - x0) * s) / 2 - x0 * s
    ty = (lado + (y1 - y0) * s) / 2 + y0 * s
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {lado} {lado}'>"
        "<style>@media(prefers-color-scheme:dark){"
        f".fundo{{fill:{PAPER}}}.letra{{fill:{BRASS}}}}}</style>"
        f"<rect class='fundo' width='{lado}' height='{lado}' fill='{INK}'/>"
        f"<path class='letra' fill='{BRASS_SOFT}'"
        f" transform='translate({tx:.3f} {ty:.3f}) scale({s:.6f} {-s:.6f})'"
        f" d='{d}'/></svg>\n")


def _fonte_pil(dados, alvo_px, texto):
    """Tamanho em px que faz a tinta do texto ter a altura pedida."""
    ref = 400
    f = ImageFont.truetype(io.BytesIO(dados), ref)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    _, a0, _, a1 = d.textbbox((0, 0), texto, font=f, anchor="ls")
    px = max(1, round(ref * alvo_px / (a1 - a0)))
    return ImageFont.truetype(io.BytesIO(dados), px)


def _desenha_centrado(draw, texto, fnt, lado, cor, entreletra=0.0):
    """Escreve o texto com a caixa de tinta no centro do quadrado.

    A entreletra é aplicada letra a letra, como o tracked() do og.py, porque
    o Pillow não tem letter-spacing. Ela não entra depois da última letra: o
    letter-spacing do CSS entra, e é por isso que o .mono parece deslocado
    um fio para a esquerda no cabeçalho. Aqui a caixa manda, não o avanço.
    """
    larguras = [draw.textlength(c, font=fnt) for c in texto]
    passos = [sum(larguras[:i]) + entreletra * i for i in range(len(texto))]

    x0 = y0 = float("inf")
    x1 = y1 = float("-inf")
    for c, dx in zip(texto, passos):
        a0, b0, a1, b1 = draw.textbbox((dx, 0), c, font=fnt, anchor="ls")
        x0, y0, x1, y1 = min(x0, a0), min(y0, b0), max(x1, a1), max(y1, b1)

    ox = lado / 2 - (x0 + x1) / 2
    oy = lado / 2 - (y0 + y1) / 2
    for c, dx in zip(texto, passos):
        draw.text((ox + dx, oy), c, font=fnt, fill=cor, anchor="ls")


def selo_png(lado):
    """O mesmo selo em bitmap, para o .ico. Desenha grande e reduz."""
    L = lado * SUPER
    dados = ttf(fraunces(PESO_PEQUENO))
    img = Image.new("RGB", (L, L), INK)
    d = ImageDraw.Draw(img)
    _desenha_centrado(d, "M", _fonte_pil(dados, L * ALTURA_M, "M"), L,
                      BRASS_SOFT)
    return img.resize((lado, lado), Image.LANCZOS)


def touch_png(lado=180):
    """Ícone de tela de início do iOS: a marca inteira, como no cartão og.

    Sem transparência — o iOS descarta o canal alfa e compõe sobre preto — e
    com a moldura recuada o bastante para sobreviver ao recorte de cantos
    arredondados que o sistema aplica por cima.
    """
    L = lado * SUPER
    dados = ttf(fraunces(PESO_GRANDE))
    img = Image.new("RGB", (L, L), INK)
    d = ImageDraw.Draw(img)

    recuo = round(L * 0.145)          # 26 px em 180: dentro da máscara do iOS
    fio = max(1, round(L * 0.011))
    d.rectangle([recuo, recuo, L - recuo - 1, L - recuo - 1],
                outline=BRASS_SOFT, width=fio)

    interno = L - 2 * recuo
    fnt = _fonte_pil(dados, interno * 0.36, "MP")
    _desenha_centrado(d, "MP", fnt, L, BRASS_SOFT,
                      entreletra=fnt.size * 0.06)   # letter-spacing do .mono
    return img.resize((lado, lado), Image.LANCZOS)


def escreve_ico(destino, imagens):
    """Monta o .ico à mão, com um PNG por tamanho.

    O Pillow, ao salvar .ico, reamostra uma imagem só para todos os tamanhos.
    Aqui cada tamanho é rasterizado do contorno no seu próprio tamanho, que é
    a diferença entre serifa legível e serifa borrada a 16 px.
    """
    quadros = []
    for img in imagens:
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        quadros.append(buf.getvalue())

    cabecalho = struct.pack("<HHH", 0, 1, len(quadros))
    deslocamento = len(cabecalho) + 16 * len(quadros)
    diretorio, corpo = b"", b""
    for img, dados in zip(imagens, quadros):
        lado = 0 if img.width >= 256 else img.width
        diretorio += struct.pack("<BBBBHHII", lado, lado, 0, 0, 1, 32,
                                 len(dados), deslocamento)
        deslocamento += len(dados)
        corpo += dados
    destino.write_bytes(cabecalho + diretorio + corpo)


def kb(p):
    return f"{p.stat().st_size / 1024:.1f} KB"


if __name__ == "__main__":
    print("Gerando ícones:")

    svg = DIST / "favicon.svg"
    svg.write_text(selo_svg(), encoding="utf-8")
    print(f"  ✓ favicon.svg   ({kb(svg)})")

    ico = DIST / "favicon.ico"
    escreve_ico(ico, [selo_png(n) for n in (16, 32, 48)])
    print(f"  ✓ favicon.ico   ({kb(ico)}, 16/32/48)")

    touch = DIST / "apple-touch-icon.png"
    touch_png().save(touch, "PNG", optimize=True)
    print(f"  ✓ apple-touch-icon.png   ({kb(touch)}, 180x180)")
