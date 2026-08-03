#!/usr/bin/env python3
"""Gera os HTMLs do site a partir dos fragmentos em src/."""
import datetime
import hashlib
import html as html_mod
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT.parent   # publica na raiz do repositório
DIST.mkdir(exist_ok=True)

CSS = (SRC / "styles.css").read_text(encoding="utf-8")

# Recorte latino. Declarado no @font-face e repetido aqui porque é ele que
# define de quais caracteres a fonte responde — fora dele o navegador cai
# para a família seguinte da pilha.
UNICODE_RANGE = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
    "U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,"
    "U+2212,U+2215,U+FEFF,U+FFFD"
)

FONT_FILES = [
    ("Fraunces", ROOT / "fraunces-latin-wght-normal.woff2"),
    ("Inter", ROOT / "inter-latin-wght-normal.woff2"),
]

# ---------------------------------------------------------------------------
# Fontes de recurso com métrica corrigida
#
# Com a fonte em arquivo, o texto aparece primeiro na fonte do sistema e troca
# quando a real chega. Se as duas ocupam larguras diferentes, o bloco de texto
# muda de tamanho na troca — e um bloco maior conta como novo candidato a LCP,
# que passa a ser cronometrado na troca em vez da primeira pintura.
#
# A correção é declarar a fonte de recurso com as métricas da fonte real:
# `size-adjust` iguala a largura, `ascent/descent-override` igualam a caixa de
# linha. O bloco fica do mesmo tamanho antes e depois, o LCP fecha na primeira
# pintura e não sobra deslocamento de layout.
#
# `razao` é medida, não estimada: é quanto o texto do site ocupa na fonte real
# dividido pelo que ocupa na fonte de recurso, no mesmo corpo. A medição está
# em _fonte/medir.html e precisa do document.fonts.load() explícito que há lá —
# sem ele o navegador nunca busca a fonte e mede recurso contra recurso.
FALLBACKS = {
    "Fraunces": dict(
        nome="Fraunces Fallback",
        # Georgia erra por 2%; Times, por 13%. A razão é a do peso 300, que é
        # o do h1 — o bloco cuja altura empurra o resto do herói.
        locais=["Georgia", "Times New Roman", "Liberation Serif", "Noto Serif"],
        razao=1.0221, upem=2000, asc=1956, desc=510, gap=0,
    ),
    "Inter": dict(
        nome="Inter Fallback",
        locais=["Arial", "Helvetica", "Liberation Sans", "Roboto"],
        razao=1.0657, upem=2048, asc=1984, desc=494, gap=0,
    ),
}


def face_de_recurso(cfg):
    """@font-face que veste a fonte do sistema com as métricas da fonte real.

    Os override são resolvidos sobre o corpo já ajustado por size-adjust — daí
    a divisão pela razão.
    """
    r = cfg["razao"]
    src = ", ".join("local('%s')" % n for n in cfg["locais"])
    pct = lambda v: ("%.2f" % (v * 100)).rstrip("0").rstrip(".")
    return (f"@font-face{{font-family:'{cfg['nome']}';font-style:normal;"
            f"src:{src};"
            f"size-adjust:{pct(r)}%;"
            f"ascent-override:{pct(cfg['asc'] / cfg['upem'] / r)}%;"
            f"descent-override:{pct(cfg['desc'] / cfg['upem'] / r)}%;"
            f"line-gap-override:{pct(cfg['gap'] / cfg['upem'] / r)}%;}}")


def emit_fonts():
    """Publica as fontes como arquivo próprio e devolve (@font-face, preloads).

    Elas já foram embutidas em base64 dentro do <style>. Eram 82 KB que
    entravam no caminho crítico de renderização de cada página, não
    comprimiam (woff2 já vem comprimido, e base64 ainda infla um terço) e
    não se reaproveitavam entre as três páginas. Como arquivo, baixam em
    paralelo com o HTML, ficam em cache e valem para o site inteiro.

    O hash no nome permite cache longo: se a fonte mudar, o nome muda.
    """
    out_dir = DIST / "fonts"
    out_dir.mkdir(parents=True, exist_ok=True)
    faces, preloads, publicados = [], [], set()

    for family, path in FONT_FILES:
        data = path.read_bytes()
        nome = "%s.%s.woff2" % (path.stem.replace("-wght-normal", ""),
                                hashlib.sha256(data).hexdigest()[:8])
        alvo = out_dir / nome
        if not alvo.exists() or alvo.read_bytes() != data:
            alvo.write_bytes(data)
        publicados.add(nome)
        url = "/fonts/" + nome
        # crossorigin não é opcional: fonte é sempre buscada em modo CORS
        # anônimo, e sem o atributo o navegador baixa o arquivo duas vezes.
        preloads.append(f'<link rel="preload" href="{url}" as="font" '
                        f'type="font/woff2" crossorigin>')
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:normal;font-display:swap;"
            f"font-weight:100 900;src:url({url}) format('woff2');"
            f"unicode-range:{UNICODE_RANGE};}}")
        if family in FALLBACKS:
            faces.append(face_de_recurso(FALLBACKS[family]))

    # A fonte antiga só sai depois que o HTML que a citava saiu de cache: um
    # visitante que pegou a página antes do deploy ainda pede o nome antigo.
    for antigo in sorted(out_dir.glob("*.woff2")):
        if antigo.name not in publicados:
            print(f"  · {antigo.name} não é mais referenciado — apague à mão "
                  f"depois que o HTML antigo tiver saído de cache")

    return "".join(faces), "\n".join(preloads) + "\n"


FONT_FACES, FONT_PRELOAD = emit_fonts()
CSS = FONT_FACES + "\n" + CSS

WA = ("https://wa.me/5585991090253?text="
      "Ol%C3%A1%2C%20Marynna.%20Cheguei%20pelo%20seu%20site%20e%20gostaria%20de%20conversar.")
TEL = "+5585991090253"
MAIL = "oi@marynnapereira.adv.br"
LINKEDIN = "https://www.linkedin.com/in/marynna-pereira"
LATTES = "https://lattes.cnpq.br/7021509895045643"
OAB = "OAB/CE nº 39.602"

# Praça de atuação. O endereço de rua não é publicado: só cidade e UF, e apenas
# nos dados estruturados, para sinalizar a região atendida.
END_CIDADE = "Fortaleza"
END_UF = "CE"

# Domínio final. Vazio = canonical, og:url, og:image e o sitemap são omitidos,
# porque URL relativa não serve para nenhum deles.
SITE_URL = "https://marynnapereira.adv.br"

NOME = "Marynna Pereira"
BANCA = "Marynna Pereira — Advocacia e Consultoria Jurídica"
ATUA_EM = [
    "Direito societário", "Planejamento patrimonial",
    "Planejamento sucessório", "Direito tributário",
    "Governança corporativa", "Compliance", "LGPD",
]
IDIOMAS = ["pt-BR", "en", "es", "fr", "zh"]

# max-image-preview:large libera a miniatura grande no resultado de busca —
# é o que faz o cartão de compartilhamento aparecer em tamanho útil.
ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"

ANO = datetime.date.today().year

PAGES = {
    "index.html": dict(
        body="index",
        title="Marynna Pereira | Advogada — Patrimônio, Societário e Governança",
        desc=("Advocacia e consultoria jurídica preventiva: estruturação societária, "
              "planejamento patrimonial e sucessório, governança e compliance. "
              "Risco e custo lado a lado."),
        og="home.png",
        og_alt=("Cartão do site de Marynna Pereira, advogada: Patrimônio, estrutura "
                "societária e sucessão."),
        dark_head=True,
    ),
    "empresas.html": dict(
        body="empresas",
        title="Consultoria jurídica para empresas | Marynna Pereira",
        desc=("Estruturação societária, holding, planejamento tributário, governança, "
              "compliance e LGPD. Cada alternativa com o risco jurídico e o custo à vista."),
        og="empresas.png",
        og_alt=("Cartão da página para empresas: a estrutura da empresa é uma decisão "
                "jurídica — e financeira."),
        dark_head=True,
    ),
    "patrimonio-e-sucessao.html": dict(
        body="pessoal",
        title="Planejamento patrimonial e sucessório | Marynna Pereira",
        desc=("Planejamento sucessório, holding familiar, proteção patrimonial, testamento, "
              "doações e regime de bens. O custo tributário de cada via, comparado."),
        og="patrimonio-e-sucessao.png",
        og_alt=("Cartão da página de patrimônio e sucessão: o que se constrói numa vida "
                "se transmite segundo regras."),
        dark_head=True,
    ),
}

NAV_ITEMS = [
    ("empresas.html", "Para empresas"),
    ("patrimonio-e-sucessao.html", "Para você e sua família"),
]

# Trilha de cada página interna. Alimenta ao mesmo tempo o rastro visível no
# herói e o BreadcrumbList dos dados estruturados — os dois não podem divergir.
# A home é a raiz e não tem trilha.
#
# O rótulo final é curto e espelha o endereço (/empresas/, /patrimonio-e-sucessao/),
# que é a forma corrente de trilha. Medido em 360 px: a frase descritiva inteira
# ocupava três linhas, e a sobrancelha que havia antes dela ocupava duas; assim
# fica em uma, em qualquer largura. A frase inteira continua no title, na
# description e no h1.
CRUMBS = {
    "empresas.html": [
        ("index.html", "Início"),
        (None, "Empresas"),
    ],
    "patrimonio-e-sucessao.html": [
        ("index.html", "Início"),
        (None, "Patrimônio e sucessão"),
    ],
}


def crumbs(page):
    """Rastro visível. Ocupa a linha da sobrancelha, sem custar altura nova."""
    trilha = CRUMBS.get(page)
    if not trilha:
        return ""
    itens = []
    for href, label in trilha:
        if href is None:
            itens.append(f'<li aria-current="page">{label}</li>')
        else:
            itens.append(f'<li><a href="{href}">{label}</a></li>')
    lista = "\n            ".join(itens)
    return ('<nav class="eyebrow crumbs" aria-label="Trilha de navegação">\n'
            '          <ol>\n            '
            f'{lista}\n'
            '          </ol>\n'
            '        </nav>')


def header(current, dark):
    parts = []
    for href, label in NAV_ITEMS:
        aria = ' aria-current="page"' if href == current else ""
        parts.append(f'<a href="{href}"{aria}>{label}</a>')
    links = "\n      ".join(parts)
    cls = "site-head on-dark" if dark else "site-head"
    return f"""<a class="pular" href="#conteudo">Ir para o conteúdo</a>
<header class="{cls}">
  <div class="wrap head-in">
    <a class="brand" href="index.html">
      <span class="mono" aria-hidden="true">MP</span>
      <span>
        <span class="brand-name">Marynna Pereira</span>
        <span class="brand-role">Advogada<span class="brand-role-x"> · Consultora jurídica</span></span>
      </span>
    </a>
    <nav class="nav" aria-label="Principal">
      {links}
    </nav>
    <a href="#contato" class="head-cta btn btn-sm {'btn-outline-light' if dark else 'btn-ghost'}">Contato</a>
  </div>
</header>"""


def footer():
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-id">
        <p class="idn">Marynna Pereira</p>
        <p>Advogada · {OAB}</p>
      </div>
      <nav class="foot-nav" aria-label="Rodapé">
        <a href="index.html">Início</a>
        <a href="empresas.html">Para empresas</a>
        <a href="patrimonio-e-sucessao.html">Para você e sua família</a>
        <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="{LATTES}" target="_blank" rel="noopener">Lattes</a>
      </nav>
    </div>
    <p class="disclaimer">
      Conteúdo de caráter exclusivamente informativo, publicado nos termos do Provimento nº 205/2021
      do Conselho Federal da Ordem dos Advogados do Brasil. As informações desta página não
      constituem consulta, parecer ou orientação jurídica para caso concreto, não configuram oferta
      de serviços e não veiculam promessa de resultado. Cada situação exige análise individual. As titulações e experiências indicadas são verdadeiras e comprováveis mediante solicitação, nos termos do art. 1º, § 2º, do mesmo Provimento. As
      referências legislativas citadas remetem à norma vigente na data de publicação.
    </p>
    <p class="disclaimer">
      © <span id="yr">{ANO}</span> Marynna Pereira. Todos os direitos reservados.
    </p>
  </div>
</footer>
<a class="wa" href="{WA}" target="_blank" rel="noopener" aria-label="Falar comigo pelo WhatsApp">
  <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm0 18.15h-.01a8.23 8.23 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.23 8.25-8.23 2.2 0 4.27.86 5.83 2.41a8.19 8.19 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.14.16-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.5.11-.11.25-.29.37-.43.13-.15.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43-.14 0-.31-.01-.47-.01-.17 0-.43.06-.66.31-.23.25-.86.85-.86 2.07 0 1.21.89 2.39 1.01 2.55.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.15-1.18-.06-.1-.23-.17-.48-.29Z"/></svg>
  <span class="wa-t">Falar comigo</span>
</a>"""


SHELL = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{preload}<meta name="author" content="Marynna Pereira">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0F1D18">
<meta name="color-scheme" content="light">
{canonical}<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="Marynna Pereira — Advocacia e Consultoria Jurídica">
{social}{icones}<style>
{css}
</style>
{jsonld}</head>
<body>
{header}
<main id="conteudo">
{body}
</main>
{footer}
<script>
(function () {{
  var y = document.getElementById('yr');
  if (y) y.textContent = new Date().getFullYear();
}})();
</script>
</body>
</html>
"""

# Ícones — gerados por icones.py, que também explica o desenho.
#
# O .ico vem primeiro e declara o tamanho: navegador que entende SVG usa o SVG,
# e o sizes serve de desempate para os que não entendem. Ele precisa existir na
# raiz mesmo com as tags aqui, porque navegador e robô pedem /favicon.ico sem
# perguntar ao HTML — e, no GitHub Pages, o que responde a um pedido sem
# resposta é o 404.html, 33 KB de página para quem só queria 4 KB de ícone.
#
# Não há manifesto: o Android usa o apple-touch-icon quando não encontra um, e
# um site institucional de três páginas não se instala como aplicativo.
ICONES = (
    '<link rel="icon" href="/favicon.ico" sizes="32x32">\n'
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
)

OUT_PATH = {
    "index.html": "index.html",
    "empresas.html": "empresas/index.html",
    "patrimonio-e-sucessao.html": "patrimonio-e-sucessao/index.html",
}


def page_url(page):
    """URL pública da página. Vazio enquanto SITE_URL não estiver definido."""
    if not SITE_URL:
        return ""
    return SITE_URL.rstrip("/") + "/" + OUT_PATH[page].replace("index.html", "")


def og_url(page):
    if not SITE_URL:
        return ""
    return SITE_URL.rstrip("/") + "/og/" + PAGES[page]["og"]


def node_id(frag):
    """Identidade estável dos nós reaproveitados entre páginas."""
    base = SITE_URL.rstrip("/") + "/" if SITE_URL else ""
    return f"{base}#{frag}"


# ---------------------------------------------------------------------------
# Perguntas frequentes
#
# O FAQPage é extraído do próprio HTML da página. Dados estruturados só valem
# quando descrevem o que está visível; gerando a partir da fonte, os dois não
# podem divergir por descuido numa edição de texto.
# ---------------------------------------------------------------------------
_DETAILS = re.compile(
    r"<details>\s*<summary>(.*?)</summary>\s*"
    r'<div class="ans">(.*?)</div>\s*</details>',
    re.S)
# Só é tag o que abre uma: com `<[^>]+>`, um "menos de < 5%" no meio da
# resposta engolia tudo até o `>` seguinte.
_TAGS = re.compile(r"<!--.*?-->|</?[a-zA-Z][^>]*>", re.S)
_ESPACO = re.compile(r"\s+")
_ABRE_DETAILS = re.compile(r"<details\b")


def texto(fragmento):
    return _ESPACO.sub(" ", html_mod.unescape(_TAGS.sub("", fragmento))).strip()


def faq(frag, pagina):
    """Perguntas visíveis da página, na ordem em que aparecem.

    _DETAILS casa uma forma exata. `<details open>` ou outra classe no
    invólucro da resposta continuam válidos no navegador e continuariam
    aparecendo para o leitor — mas sairiam daqui em silêncio, e o FAQPage
    publicado passaria a descrever menos do que a página mostra. Por isso a
    contagem é conferida: divergiu, a build para.
    """
    pares = _DETAILS.findall(frag)
    visiveis = len(_ABRE_DETAILS.findall(frag))
    if len(pares) != visiveis:
        raise SystemExit(
            f"{pagina}: a página mostra {visiveis} pergunta(s) e o extrator "
            f"achou {len(pares)}. O FAQPage sairia incompleto. Confira se o "
            f"markup ainda é <details><summary>…</summary>"
            f'<div class="ans">…</div></details>.')
    return [(texto(q), texto(a)) for q, a in pares]


def jsonld(page, frag):
    """Dados estruturados — só o que já está visível na página.

    Um @graph em vez de um nó solto por página: a pessoa, a banca e o site são
    a mesma entidade nas três páginas, e o @id é o que diz isso ao buscador.
    """
    url = page_url(page)
    cfg = PAGES[page]

    pessoa = {
        "@type": "Person",
        "@id": node_id("marynna"),
        "name": NOME,
        "jobTitle": "Advogada",
        "knowsLanguage": IDIOMAS,
        "knowsAbout": ATUA_EM,
        "alumniOf": {
            "@type": "CollegeOrUniversity",
            "name": "Universidade de Fortaleza (UNIFOR)",
        },
        "hasCredential": [
            {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "Inscrição profissional",
                "identifier": OAB,
                "recognizedBy": {
                    "@type": "Organization",
                    "name": "Ordem dos Advogados do Brasil — Seccional Ceará",
                },
            },
            {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "Mestrado",
                "name": "Mestrado em Direito Constitucional",
                "recognizedBy": {
                    "@type": "CollegeOrUniversity",
                    "name": "Universidade de Fortaleza (UNIFOR)",
                },
            },
        ],
        "sameAs": [LINKEDIN, LATTES],
        "worksFor": {"@id": node_id("banca")},
    }

    banca = {
        "@type": "Attorney",
        "@id": node_id("banca"),
        "name": BANCA,
        "description": PAGES["index.html"]["desc"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": END_CIDADE,
            "addressRegion": END_UF,
            "addressCountry": "BR",
        },
        "telephone": TEL,
        "email": MAIL,
        "areaServed": {"@type": "Country", "name": "Brasil"},
        "knowsAbout": ATUA_EM,
        "knowsLanguage": IDIOMAS,
        "sameAs": [LINKEDIN, LATTES],
        "founder": {"@id": node_id("marynna")},
        "employee": {"@id": node_id("marynna")},
    }

    site = {
        "@type": "WebSite",
        "@id": node_id("site"),
        "name": BANCA,
        "inLanguage": "pt-BR",
        "publisher": {"@id": node_id("banca")},
    }

    pagina = {
        "@type": "WebPage",
        "@id": (url + "#pagina") if url else "#pagina",
        "name": cfg["title"],
        "description": cfg["desc"],
        "inLanguage": "pt-BR",
        "isPartOf": {"@id": node_id("site")},
        "about": {"@id": node_id("banca")},
    }

    if SITE_URL:
        raiz = SITE_URL.rstrip("/") + "/"
        pessoa["url"] = raiz
        banca["url"] = raiz
        site["url"] = raiz
        pagina["url"] = url
        cartao = {
            "@type": "ImageObject",
            "url": og_url(page),
            "width": 1200,
            "height": 630,
            "caption": cfg["og_alt"],
        }
        pagina["primaryImageOfPage"] = cartao
        banca["image"] = {
            "@type": "ImageObject",
            "url": og_url("index.html"),
            "width": 1200,
            "height": 630,
        }

    modificado = LASTMOD.get(page, {}).get("data")
    if modificado:
        pagina["dateModified"] = modificado

    grafo = [pessoa, banca, site, pagina]

    trilha = CRUMBS.get(page)
    if trilha and SITE_URL:
        pagina["breadcrumb"] = {"@id": (url + "#trilha")}
        itens = []
        for i, (href, label) in enumerate(trilha, start=1):
            destino = page_url(href) if href else url
            itens.append({
                "@type": "ListItem",
                "position": i,
                "name": label,
                "item": destino,
            })
        grafo.append({
            "@type": "BreadcrumbList",
            "@id": url + "#trilha",
            "itemListElement": itens,
        })

    perguntas = faq(frag, page)
    if perguntas:
        # O FAQPage descreve a mesma URL da WebPage; por isso ele entra como
        # segundo tipo do nó da página, e não como um nó paralelo.
        pagina["@type"] = ["WebPage", "FAQPage"]
        pagina["mainEntity"] = [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in perguntas
        ]

    data = {"@context": "https://schema.org", "@graph": grafo}
    return ('<script type="application/ld+json">\n'
            # `<` é escape JSON válido: o buscador lê a mesma string, e o
            # analisador de HTML nunca vê um `</script>` que feche o bloco
            # antes da hora. O texto vem das perguntas da página, onde um
            # `&lt;/script&gt;` escrito à mão viraria `</script>` literal.
            + json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c")
            + "\n</script>\n")


def atrib(s):
    """Texto indo para dentro de aspas de atributo HTML.

    Título e descrição são prosa: basta uma aspa dupla numa delas para fechar
    o atributo antes da hora e derrubar o resto da tag. Nos dados estruturados
    quem escapa é o json.dumps — lá isto não passa, ou sairia `&quot;` literal.
    """
    return html_mod.escape(s, quote=True)


def social(page):
    """Cartão para redes sociais. Exige URL absoluta — sem SITE_URL, não sai."""
    if not SITE_URL:
        return ""
    cfg = PAGES[page]
    img = og_url(page)
    return (f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:type" content="image/png">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{atrib(cfg["og_alt"])}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{atrib(cfg["title"])}">\n'
            f'<meta name="twitter:description" content="{atrib(cfg["desc"])}">\n'
            f'<meta name="twitter:image" content="{img}">\n'
            f'<meta name="twitter:image:alt" content="{atrib(cfg["og_alt"])}">\n')


def canonical(page):
    url = page_url(page)
    if not url:
        return ""
    return (f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:url" content="{url}">\n')


# ---------------------------------------------------------------------------
# lastmod
#
# O Google ignora lastmod que não corresponde a mudança real de conteúdo. A
# data só avança quando a impressão digital do texto muda: reordenar CSS ou
# reconstruir o site não é alteração de conteúdo.
# ---------------------------------------------------------------------------
LASTMOD_FILE = ROOT / "lastmod.json"


def impressao(page):
    """Tudo que é conteúdo da página, e nada que seja apresentação.

    O corpo não é a única coisa que o leitor vê: a trilha, o menu e o número
    da OAB no rodapé também saem daqui, e mexer neles muda a página. Ficam de
    fora o CSS e o ano do rodapé — o primeiro é forma, o segundo vira sozinho.
    """
    cfg = PAGES[page]
    frag = (SRC / f"{cfg['body']}.body.html").read_bytes()
    compartilhado = [cfg["title"], cfg["desc"], cfg["og_alt"], OAB,
                     repr(CRUMBS.get(page)), repr(NAV_ITEMS), repr(ATUA_EM)]
    miolo = frag + "\x00".join(compartilhado).encode("utf-8")
    return hashlib.sha256(miolo).hexdigest()[:16]


def carrega_lastmod():
    hoje = datetime.date.today().isoformat()
    try:
        antigo = json.loads(LASTMOD_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        antigo = {}
    atual = {}
    for page in PAGES:
        digital = impressao(page)
        anterior = antigo.get(page, {})
        data = anterior.get("data") if anterior.get("digital") == digital else hoje
        atual[page] = {"digital": digital, "data": data or hoje}
    return atual


LASTMOD = carrega_lastmod()


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
    # O 404 é servido no lugar de qualquer endereço inexistente, em qualquer
    # profundidade: os links dele têm de partir da raiz.
    "404.html": {
        "index.html": "/",
        "empresas.html": "/empresas/",
        "patrimonio-e-sucessao.html": "/patrimonio-e-sucessao/",
    },
}

_HREF = re.compile(r'href="(index|empresas|patrimonio-e-sucessao)\.html"')


def rewrite_links(html, page):
    table = LINKS[page]
    return _HREF.sub(lambda m: 'href="%s"' % table[m.group(1) + ".html"], html)


def corpo(nome):
    frag = (SRC / f"{nome}.body.html").read_text(encoding="utf-8")
    return (frag.replace("{{WA}}", WA)
                .replace("{{MAIL}}", MAIL)
                .replace("{{LINKEDIN}}", LINKEDIN)
                .replace("{{LATTES}}", LATTES))


def build():
    for out, cfg in PAGES.items():
        frag = corpo(cfg["body"]).replace("{{CRUMBS}}", crumbs(out))
        html = SHELL.format(
            title=atrib(cfg["title"]), desc=atrib(cfg["desc"]), css=CSS, robots=ROBOTS,
            preload=FONT_PRELOAD, canonical=canonical(out), social=social(out),
            jsonld=jsonld(out, frag), icones=ICONES,
            header=header(out, cfg["dark_head"]), body=frag, footer=footer(),
        )
        html = rewrite_links(html, out)
        dest = DIST / OUT_PATH[out]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        print(f"  ✓ {OUT_PATH[out]}  ({len(html)//1024} KB)")

    LASTMOD_FILE.write_text(
        json.dumps(LASTMOD, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def erro_404():
    """Página de erro do GitHub Pages. Fora do sitemap e fora do índice."""
    html = SHELL.format(
        title="Página não encontrada | Marynna Pereira",
        desc="O endereço solicitado não existe neste site.",
        css=CSS, robots="noindex, follow", preload=FONT_PRELOAD,
        canonical="", social="", jsonld="", icones=ICONES,
        header=header("404.html", True), body=corpo("404"), footer=footer(),
    )
    html = rewrite_links(html, "404.html")
    (DIST / "404.html").write_text(html, encoding="utf-8")
    print("  ✓ 404.html")


def sitemap():
    """Sitemap e robots saem daqui para não repetirem o domínio à mão."""
    if not SITE_URL:
        print("  · SITE_URL vazio — sitemap.xml e robots.txt não foram tocados")
        return
    # changefreq e priority ficaram de fora: o Google não os usa, e sitemap
    # que afirma o que ninguém lê é ruído.
    urls = "\n".join(
        f"  <url>\n"
        f"    <loc>{page_url(p)}</loc>\n"
        f"    <lastmod>{LASTMOD[p]['data']}</lastmod>\n"
        f"  </url>"
        for p in PAGES
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n", encoding="utf-8")
    print("  ✓ sitemap.xml")

    (DIST / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL.rstrip('/')}/sitemap.xml\n", encoding="utf-8")
    print("  ✓ robots.txt")


if __name__ == "__main__":
    print("Gerando páginas:")
    build()
    erro_404()
    sitemap()
