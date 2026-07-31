#!/usr/bin/env python3
"""Gera os HTMLs autocontidos do site a partir dos fragmentos em src/."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT.parent   # publica na raiz do repositório
DIST.mkdir(exist_ok=True)

CSS = (SRC / "styles.css").read_text(encoding="utf-8")


def _font_face(family, path, weights="100 900"):
    """Embute a fonte variável em base64 para a página não depender de rede."""
    import base64
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-display:swap;"
            f"font-weight:{weights};src:url(data:font/woff2;base64,{data}) format('woff2');"
            "unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
            "U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;}")


FONTS = (
    _font_face("Fraunces", ROOT / "fraunces-latin-wght-normal.woff2")
    + _font_face("Inter", ROOT / "inter-latin-wght-normal.woff2")
)
CSS = FONTS + "\n" + CSS

WA = ("https://wa.me/5585991090253?text="
      "Ol%C3%A1%2C%20Marynna.%20Cheguei%20pelo%20seu%20site%20e%20gostaria%20de%20conversar.")
MAIL = "marynnalqp@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/marynna-pereira"
LATTES = "http://lattes.cnpq.br/7021509895045643"
OAB = "OAB/CE n&ordm; [inserir]"

PAGES = {
    "index.html": dict(
        body="index",
        title="Marynna Pereira | Advogada — Patrimônio, Societário e Governança",
        desc=("Advogada e consultora jurídica em Fortaleza/CE. Estruturação societária, "
              "planejamento patrimonial, sucessório e tributário, governança, compliance e "
              "proteção de dados."),
        dark_head=True,
    ),
    "empresas.html": dict(
        body="empresas",
        title="Consultoria jurídica para empresas | Marynna Pereira",
        desc=("Estruturação societária, holding, planejamento tributário, governança "
              "corporativa, compliance e LGPD para empresas. Fortaleza/CE e atendimento remoto."),
        dark_head=True,
    ),
    "patrimonio-e-sucessao.html": dict(
        body="pessoal",
        title="Planejamento patrimonial e sucessório | Marynna Pereira",
        desc=("Planejamento sucessório, holding familiar, proteção patrimonial, testamento e "
              "doações para pessoas físicas e famílias. Fortaleza/CE e atendimento remoto."),
        dark_head=True,
    ),
}

NAV_ITEMS = [
    ("empresas.html", "Para empresas"),
    ("patrimonio-e-sucessao.html", "Para você e sua família"),
]


def header(current, dark):
    parts = []
    for href, label in NAV_ITEMS:
        aria = ' aria-current="page"' if href == current else ""
        parts.append(f'<a href="{href}" class="nav-hide"{aria}>{label}</a>')
    links = "".join(parts)
    cls = "site-head on-dark" if dark else "site-head"
    return f"""<header class="{cls}" id="siteHead">
  <div class="wrap head-in">
    <a class="brand" href="index.html" aria-label="Marynna Pereira &mdash; p&aacute;gina inicial">
      <span class="mono" aria-hidden="true">MP</span>
      <span>
        <span class="brand-name">Marynna Pereira</span>
        <span class="brand-role">Advogada &middot; Consultora jur&iacute;dica</span>
      </span>
    </a>
    <nav class="nav">
      {links}
      <a href="#contato" class="btn btn-sm {'btn-outline-light' if dark else 'btn-ghost'}">Contato</a>
    </nav>
  </div>
</header>"""


def footer():
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-top">
      <div>
        <div class="idn">Marynna Pereira</div>
        <div style="margin-top:8px">Advogada &middot; {OAB}</div>
        <div style="margin-top:4px">Rua Monsenhor Bruno, 2220 &mdash; Fortaleza/CE, 60115-046</div>
      </div>
      <nav class="foot-nav">
        <a href="index.html">In&iacute;cio</a>
        <a href="empresas.html">Para empresas</a>
        <a href="patrimonio-e-sucessao.html">Para voc&ecirc; e sua fam&iacute;lia</a>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="{LATTES}" target="_blank" rel="noopener">Lattes</a>
      </nav>
    </div>
    <p class="disclaimer">
      Conte&uacute;do de car&aacute;ter exclusivamente informativo, publicado nos termos do Provimento n&ordm; 205/2021
      do Conselho Federal da Ordem dos Advogados do Brasil. As informa&ccedil;&otilde;es desta p&aacute;gina n&atilde;o
      constituem consulta, parecer ou orienta&ccedil;&atilde;o jur&iacute;dica para caso concreto, n&atilde;o
      configuram oferta de servi&ccedil;os e n&atilde;o veiculam promessa de resultado. Cada situa&ccedil;&atilde;o
      exige an&aacute;lise individual. As refer&ecirc;ncias legislativas citadas remetem &agrave; norma vigente na data
      de publica&ccedil;&atilde;o.
    </p>
    <p class="disclaimer" style="margin-top:14px">
      &copy; <span id="yr">2026</span> Marynna Pereira. Todos os direitos reservados.
    </p>
  </div>
</footer>
<a class="wa" href="{WA}" target="_blank" rel="noopener" aria-label="Conversar pelo WhatsApp">
  <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm0 18.15h-.01a8.23 8.23 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.23 8.25-8.23 2.2 0 4.27.86 5.83 2.41a8.19 8.19 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.14.16-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.43.13-.15.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43-.14 0-.31-.01-.47-.01-.17 0-.43.06-.66.31-.23.25-.86.85-.86 2.07 0 1.21.89 2.39 1.01 2.55.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.06-.1-.23-.17-.48-.29Z"/></svg>
  Falar comigo
</a>"""


SHELL = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Marynna Pereira">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="Marynna Pereira &mdash; Advocacia e Consultoria Jur&iacute;dica">
<style>
{css}
</style>
</head>
<body>
{header}
<main>
{body}
</main>
{footer}
<script>
(function () {{
  var y = document.getElementById('yr');
  if (y) y.textContent = new Date().getFullYear();

  var els = document.querySelectorAll('.rv');
  if (!('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    els.forEach(function (e) {{ e.classList.add('in'); }});
    return;
  }}
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (en) {{
      if (en.isIntersecting) {{ en.target.classList.add('in'); io.unobserve(en.target); }}
    }});
  }}, {{ rootMargin: '0px 0px -8% 0px', threshold: 0.06 }});
  els.forEach(function (e) {{ io.observe(e); }});
}})();
</script>
</body>
</html>
"""


OUT_PATH = {
    "index.html": "index.html",
    "empresas.html": "empresas/index.html",
    "patrimonio-e-sucessao.html": "patrimonio-e-sucessao/index.html",
}

# href relativo de cada página para cada destino (URLs sem .html)
LINKS = {
    "index.html": {
        "index.html": "./",
        "empresas.html": "empresas/",
        "patrimonio-e-sucessao.html": "patrimonio-e-sucessao/",
    },
    "empresas.html": {
        "index.html": "../",
        "empresas.html": "./",
        "patrimonio-e-sucessao.html": "../patrimonio-e-sucessao/",
    },
    "patrimonio-e-sucessao.html": {
        "index.html": "../",
        "empresas.html": "../empresas/",
        "patrimonio-e-sucessao.html": "./",
    },
}

_HREF = re.compile(r'href="(index|empresas|patrimonio-e-sucessao)\.html"')


def rewrite_links(html, page):
    table = LINKS[page]
    return _HREF.sub(lambda m: 'href="%s"' % table[m.group(1) + ".html"], html)


def build():
    for out, cfg in PAGES.items():
        frag = (SRC / f"{cfg['body']}.body.html").read_text(encoding="utf-8")
        frag = (frag.replace("{{WA}}", WA)
                    .replace("{{MAIL}}", MAIL)
                    .replace("{{LINKEDIN}}", LINKEDIN)
                    .replace("{{LATTES}}", LATTES))
        html = SHELL.format(
            title=cfg["title"], desc=cfg["desc"], css=CSS,
            header=header(out, cfg["dark_head"]), body=frag, footer=footer(),
        )
        html = rewrite_links(html, out)
        dest = DIST / OUT_PATH[out]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        print(f"  ✓ {OUT_PATH[out]}  ({len(html)//1024} KB)")


if __name__ == "__main__":
    print("Gerando páginas:")
    build()
