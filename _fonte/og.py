#!/usr/bin/env python3
"""Gera os cartões Open Graph (1200x630) em /og/, com as fontes da marca.

Roda separado do build: as imagens só mudam quando o herói de alguma página muda.

    python3 _fonte/og.py
"""
import io
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT.parent / "og"

W, H = 1200, 630

# Mesmas variáveis do styles.css, na superfície escura.
INK = "#0F1D18"
PAPER = "#F6F4EE"
BRASS_SOFT = "#D6C599"
ON_DARK_2 = "#A9B4AD"
LINE_DARK = (246, 244, 238, 36)   # rgba(246,244,238,.14)

MARGIN = 76


def _ttf(woff2):
    """Descomprime a fonte variável para um TTF que o FreeType aceita."""
    f = TTFont(ROOT / woff2)
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    return buf.read()


FRAUNCES = _ttf("fraunces-latin-wght-normal.woff2")
INTER = _ttf("inter-latin-wght-normal.woff2")


def font(data, size, weight):
    f = ImageFont.truetype(io.BytesIO(data), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass   # fonte estática: o peso nominal já serve
    return f


def wrap(draw, text, fnt, max_w):
    linhas, atual = [], ""
    for palavra in text.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=fnt) <= max_w or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def tracked(draw, xy, text, fnt, fill, tracking):
    """Caixa alta com entreletra — o mesmo efeito do .eyebrow no CSS."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def card(destino, eyebrow, headline):
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")

    f_mono = font(FRAUNCES, 26, 400)
    f_nome = font(FRAUNCES, 31, 500)
    f_papel = font(INTER, 15, 500)
    f_eyebrow = font(INTER, 17, 500)
    f_head = font(FRAUNCES, 64, 400)
    f_rodape = font(INTER, 19, 400)

    # --- marca, no alto ---------------------------------------------------
    box = 56
    d.rectangle([MARGIN, MARGIN, MARGIN + box, MARGIN + box],
                outline=BRASS_SOFT, width=1)
    mw = d.textlength("MP", font=f_mono)
    d.text((MARGIN + (box - mw) / 2, MARGIN + box / 2), "MP",
           font=f_mono, fill=BRASS_SOFT, anchor="lm")

    tx = MARGIN + box + 20
    d.text((tx, MARGIN + 6), "Marynna Pereira", font=f_nome, fill=PAPER)
    tracked(d, (tx + 1, MARGIN + 40), "ADVOGADA · CONSULTORA JURÍDICA",
            f_papel, ON_DARK_2, 1.4)

    # --- assunto da página ------------------------------------------------
    y = 268
    tracked(d, (MARGIN, y), eyebrow.upper(), f_eyebrow, BRASS_SOFT, 2.6)

    d.line([MARGIN, y + 40, MARGIN + 46, y + 40], fill=BRASS_SOFT, width=1)

    y += 68
    for linha in wrap(d, headline, f_head, W - 2 * MARGIN - 40):
        d.text((MARGIN, y), linha, font=f_head, fill=PAPER)
        y += 76

    # --- rodapé -----------------------------------------------------------
    d.line([MARGIN, H - 108, W - MARGIN, H - 108], fill=LINE_DARK, width=1)
    d.text((MARGIN, H - 78), "OAB/CE nº 39.602", font=f_rodape, fill=ON_DARK_2)
    direita = "marynnapereira.adv.br"
    d.text((W - MARGIN - d.textlength(direita, font=f_rodape), H - 78),
           direita, font=f_rodape, fill=ON_DARK_2)

    OUT.mkdir(exist_ok=True)
    img.save(OUT / destino, "PNG", optimize=True)
    print(f"  ✓ og/{destino}  ({(OUT / destino).stat().st_size // 1024} KB)")


CARDS = [
    ("home.png", "Advocacia e consultoria jurídica",
     "Patrimônio, estrutura societária e sucessão."),
    ("empresas.png", "Consultoria jurídica para empresas",
     "A estrutura da empresa é uma decisão jurídica — e financeira."),
    ("patrimonio-e-sucessao.png", "Planejamento patrimonial e sucessório",
     "O que se constrói numa vida se transmite segundo regras."),
]


if __name__ == "__main__":
    print("Gerando cartões Open Graph:")
    for destino, eyebrow, headline in CARDS:
        card(destino, eyebrow, headline)
