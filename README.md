# Site institucional — Marynna Pereira

Site estático de três páginas, sem dependências externas: as fontes (Fraunces e Inter)
são servidas do próprio domínio, então nada é carregado de terceiros. Também não há
JavaScript essencial — a página funciona inteira com o script desativado.

## Estrutura publicada

    index.html                       →  /
    empresas/index.html              →  /empresas/
    patrimonio-e-sucessao/index.html →  /patrimonio-e-sucessao/
    404.html                         →  erro do GitHub Pages, fora do índice
    fonts/*.woff2                    →  fontes com hash no nome
    og/*.png                         →  cartões de compartilhamento (1200×630)
    favicon.svg, favicon.ico         →  ícone de aba
    apple-touch-icon.png             →  ícone de tela de início do iOS
    sitemap.xml, robots.txt          →  gerados pelo build

## Como editar

Os arquivos publicados são gerados. Não edite o HTML da raiz — edite os fontes em `_fonte/`
e rode o build:

    python3 _fonte/build.py

- `_fonte/src/styles.css` — sistema visual (cores, tipografia, componentes)
- `_fonte/src/index.body.html` — conteúdo da home
- `_fonte/src/empresas.body.html` — conteúdo da página de empresas
- `_fonte/src/pessoal.body.html` — conteúdo da página de patrimônio e sucessão
- `_fonte/build.py` — monta cabeçalho, rodapé, meta tags, dados estruturados, sitemap e
  robots, e reescreve os links
- `_fonte/og.py` e `_fonte/icones.py` — imagens da marca, rodados à parte (ver adiante)

Os fontes usam acentuação normal (UTF-8), não entidades HTML.

Dados que aparecem em todas as páginas (WhatsApp, e-mail, LinkedIn, Lattes, número da OAB)
ficam no topo de `build.py`. O endereço de rua não é publicado: a cidade aparece **só** no
`addressLocality` dos dados estruturados, para sinalizar a praça de atuação.

`SITE_URL` governa `canonical`, `og:url`, `og:image`, a `url` dos dados estruturados e o
sitemap. Se for esvaziado, todos são omitidos — URL relativa não serve para nenhum deles.

`_fonte/lastmod.json` é gerado pelo build e **deve ser versionado**: ele guarda a impressão
digital do conteúdo de cada página e a data em que ela mudou pela última vez. O `lastmod` do
sitemap sai dali, e não da data da build — o Google ignora `lastmod` que avança a cada
republicação. Reordenar CSS ou trocar uma fonte não mexe na data; editar o texto, sim.

## Fontes

As duas fontes são arquivo em `fonts/`, com hash de conteúdo no nome, e vêm precarregadas
(`<link rel=preload … crossorigin>`). Antes elas viajavam em base64 dentro do `<style>` de
cada página. Medido com Lighthouse em 4G lento, throttling real (`--throttling-method=devtools`),
mediana de três execuções:

| | base64 no HTML | arquivo + preload |
|---|---|---|
| HTML por página | 152–166 KB | 42–56 KB |
| FCP | 1233–1248 ms | **788–802 ms** |
| LCP | 2302–2323 ms | **1596–1614 ms** |
| CLS | 0 | 0 |

Duas armadilhas encontradas no caminho, registradas para não se repetirem:

- **O modo simulado do Lighthouse (padrão) inverte o resultado do LCP**, porque cobra o
  download da fonte do caminho crítico independentemente de quando o texto pinta. Ele acusa
  piora onde a medição real acusa 700 ms de ganho. Para decidir sobre fonte, use
  `--throttling-method=devtools`.
- As famílias `… Fallback` em `build.py` vestem a fonte do sistema com as métricas da fonte
  real, para o bloco de texto não mudar de tamanho quando a real chega. As razões vêm de
  medição em navegador; refazê-la exige `document.fonts.load()` explícito, senão
  `document.fonts.ready` resolve sem baixar nada e mede recurso contra recurso.

O casamento é exato no corpo (Inter), que é o elemento de LCP. No `h1` a Fraunces ainda quebra
numa linha a mais que o recurso: nenhuma razão única resolve, porque a diferença está na
distribuição das larguras de glifo, não na largura total.

## Cartões de compartilhamento

    python3 _fonte/og.py

Gera um PNG de 1200×630 por página em `og/`, com o herói da própria página, usando Fraunces
e Inter descomprimidas dos `.woff2` do repositório. Roda separado do build: a imagem só muda
quando o herói muda. Ao alterar um `h1`, regere o cartão correspondente em `CARDS`.

## Ícones

    python3 _fonte/icones.py

Gera `favicon.svg`, `favicon.ico` (16, 32 e 48) e `apple-touch-icon.png` (180×180). Também
roda separado do build: a marca só muda quando alguém decide mudá-la.

É a marca do cabeçalho — o `.mono`, que é um quadrado de fio com **MP** em Fraunces — em dois
estados de tamanho:

| | desenho | por quê |
|---|---|---|
| 16–48 px | **M** sozinho, a sangria no quadrado de tinta | duas letras a 16 px sobram sete pixels de largura cada: os serifas somem e o par vira mancha. Medido em `rsvg-convert` antes de decidir |
| 180 px | **MP** dentro da moldura de fio | onde as duas letras e o fio cabem, a marca volta inteira |

Não são dois desenhos: é o mesmo selo com uma letra a menos. A moldura é o acessório que sai
primeiro — a 16 px um fio de 1 px vira meio pixel cinza e ainda rouba o espaço da letra.

Decisões que não são óbvias no código:

- **As letras saem em contorno**, extraídas do woff2 do próprio repositório, não como
  `<text font-family="…">`. O favicon anterior pedia Georgia, que não é a fonte do site e
  não existe em Android nem na maioria das distribuições Linux — nessas máquinas o navegador
  caía num serif qualquer, com outra métrica, e a letra saía fora do centro. Contorno
  renderiza igual em todo lugar.
- **Peso 600 no ícone pequeno**, embora a Fraunces do site ande de 300 a 500. Peso maior em
  tamanho menor é compensação óptica, não outra tipografia: é o que o eixo `opsz` faria se
  este recorte da fonte o expusesse. A 16 px o peso 400 acinzenta e o 700 fecha as
  contra-formas do M.
- **O `.ico` precisa existir na raiz** mesmo com as tags `<link>` no HTML: navegador e robô
  pedem `/favicon.ico` sem consultar a página. No GitHub Pages, quem responde a um pedido sem
  arquivo é o `404.html` — 33 KB de página para quem só queria 4 KB de ícone.
- **Cada tamanho do `.ico` é rasterizado no seu tamanho.** O Pillow, ao salvar `.ico`,
  reamostra uma imagem só para todos os tamanhos; a diferença aparece justamente a 16 px,
  entre serifa legível e serifa borrada. Daí o contêiner ser montado à mão em `escreve_ico`.
- **O `favicon.svg` tem os dois estados de cor**, num `@media (prefers-color-scheme:dark)`
  dentro do próprio arquivo: sobre barra de abas escura, um quadrado quase preto vira buraco.
  A inversão não é nova — `.mono` já é latão sobre papel no cabeçalho claro e latão claro
  sobre tinta no `.on-dark`. As cores também ficam em atributo de apresentação, que tem
  precedência menor que a regra CSS, para que renderizador que ignore o `<style>` caia no
  estado claro em vez de ficar sem cor.
- **As coordenadas do contorno são arredondadas para inteiro.** Interpolar a fonte variável
  num peso intermediário devolve casas decimais até a décima sexta — eram 3,8 KB de SVG para
  uma letra só, contra 1,2 KB depois. A fonte tem 2000 unidades por em e o desenho ocupa 32:
  o arredondamento acontece duas ordens de grandeza abaixo do pixel.
- **Não há manifesto.** O Android usa o `apple-touch-icon` quando não encontra um, e um site
  institucional de três páginas não se instala como aplicativo.

## Sistema visual

Registro de instrumento jurídico: a afirmação fica na coluna de texto e a autoridade que a
sustenta (lei, artigo, ano) fica na margem, separada por um fio. Esse par margem/texto é o
motivo que se repete no site — nas referências legais, na ficha do herói e nos cartões de
compartilhamento.

- **Tinta** `--ink #0F1D18`, um verde quase preto, nas superfícies escuras
- **Papel** `--paper #F6F4EE`, com `--paper-2` nas seções alternadas
- **Latão** `--brass #5C4A18` como único acento; `--brass-2` só em fios e bordas, nunca em texto
- **Fraunces** de 300 a 500 — o display é leve e grande, os títulos pequenos são densos
- **Inter** no corpo, com `tabular-nums` em percentuais e artigos de lei

A numeração 01–04 aparece só nas etapas do trabalho, que são uma sequência de verdade, e vem
de um `counter()` no CSS. Listas que não são sequência não recebem número.

Animação: uma única entrada escalonada no herói, em CSS, desligada sob
`prefers-reduced-motion: reduce`. Não há animação atrelada a rolagem.

## SEO

- `title` e `description` únicos por página, com o `description` entre 145 e 160 caracteres —
  acima disso o Google corta o trecho
- Dados estruturados num único `@graph` por página: `Person`, `Attorney`, `WebSite`, `WebPage`
  e, nas internas, `BreadcrumbList` e `FAQPage`. O `@id` é o que diz ao buscador que a pessoa
  e a banca das três páginas são a mesma entidade
- O `FAQPage` é extraído dos `<details>` da própria página, não escrito à mão: dado estruturado
  que não corresponde ao conteúdo visível é violação de diretriz
- `max-image-preview:large` no `robots`, para o cartão aparecer em tamanho útil no resultado
- Trilha de navegação visível nas internas, na linha da sobrancelha, casada com o
  `BreadcrumbList` — as duas saem da mesma tabela `CRUMBS` em `build.py`

Não feito, por ser decisão de posicionamento e não questão técnica: **nenhum `title` ou
`description` menciona Fortaleza.** O guia do Google recomenda cidade no título para negócio
com praça definida, e buscas locais ("advogada societária Fortaleza") são de alta intenção.
O site hoje se apresenta como nacional (`areaServed: BR`, atendimento a distância) e a cidade
só aparece nos dados estruturados. Vale decidir de qual lado ficar.

## Pendências antes de divulgar

1. Conferir, no painel de e-mail do domínio, se `oi@marynnapereira.adv.br` tem regra de
   encaminhamento ativa. O domínio já aceita mensagens (MX da Cloudflare), mas o roteamento
   por endereço é configurado à parte.
2. Submeter `sitemap.xml` ao Google Search Console e à Bing Webmaster Tools — a diretiva em
   `robots.txt` só ajuda depois que o robô passa pela primeira vez.
3. Validar os cartões em https://cards-dev.twitter.com/validator e no depurador de
   compartilhamento do Facebook, que também força a releitura do cache.

Referências legais conferidas em 2 de agosto de 2026: `LC nº 227/2026` existe (sancionada em
13/01/2026, publicada em 14/01/2026), o teto de 8% da `Res. Senado nº 9/1992` não foi alterado
pela Reforma Tributária, e a exigibilidade a partir de 1º/01/2027 decorre das anterioridades
anual e nonagesimal. Reconferir se a página for republicada muito depois desta data.

## Conformidade

O conteúdo foi redigido conforme o Provimento nº 205/2021 do Conselho Federal da OAB: caráter
informativo, sem promessa de resultado, sem menção a honorários ou gratuidade e sem depoimentos
ou casos concretos. A análise completa está na nota técnica que acompanha o projeto.

O termo "especialista" foi substituído por "Advogada com ênfase em …", que descreve a área de
atuação sem afirmar titulação. O art. 3º, III do Provimento nº 205/2021 reserva "especialista"
a quem tenha título registrado; se o título existir, dá para voltar atrás editando a linha
`.rl` nos três fragmentos de `_fonte/src/`.

Pela mesma razão, o resumo do herói descreve atividades em vez de vínculos ("Docência e
treinamentos corporativos", não "Professora universitária"): o art. 1º, § 2º exige que a
informação seja verdadeira e comprovável, e cargo no presente afirma vínculo contínuo. A nota
de comprovação mediante solicitação fica no rodapé, em todas as páginas.

## Acessibilidade

- Contraste verificado em navegador: todo texto atinge 7:1 (WCAG AAA), inclusive sobre o papel
  mais escuro das seções `.facts`
- Link "Ir para o conteúdo" antes do cabeçalho
- Foco de teclado visível em todos os elementos interativos (`:focus-visible`)
- Navegação disponível no celular — o cabeçalho quebra em duas linhas em vez de esconder os links
- Sem rolagem horizontal de 320 px para cima, medido em 320, 360, 375, 390, 412 e 430
- Alvos de toque de 44 px nos links de navegação: menu do rodapé, trilha e cabeçalho.
  Ficam de fora os links dentro de frase (`.note a`), que a WCAG 2.5.8 dispensa
- No telefone (≤560 px) o atalho de WhatsApp é disco, só o símbolo. Com o rótulo ele
  media 141 px e cobria um botão do herói em tela estreita ou baixa — e, por flutuar
  por cima, ficava com o toque. Elemento fixo cobre o pé da tela em qualquer rolagem,
  então reservar espaço no fim do documento não resolve; o que resolve é encolher
- Em paisagem baixa (≤520 px de altura) o cabeçalho deixa de ser fixo
- `prefers-reduced-motion: reduce` respeitado
