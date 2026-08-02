# Site institucional — Marynna Pereira

Site estático de três páginas, sem dependências externas: as fontes (Fraunces e Inter)
estão embutidas em base64 no CSS de cada página, então nada é carregado de terceiros.
Também não há JavaScript essencial — a página funciona inteira com o script desativado.

## Estrutura publicada

    index.html                       →  /
    empresas/index.html              →  /empresas/
    patrimonio-e-sucessao/index.html →  /patrimonio-e-sucessao/
    og/*.png                         →  cartões de compartilhamento (1200×630)
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

Os fontes usam acentuação normal (UTF-8), não entidades HTML.

Dados que aparecem em todas as páginas (WhatsApp, e-mail, LinkedIn, Lattes, número da OAB)
ficam no topo de `build.py`. O endereço de rua não é publicado: a cidade aparece **só** no
`addressLocality` dos dados estruturados, para sinalizar a praça de atuação.

`SITE_URL` governa `canonical`, `og:url`, `og:image`, a `url` dos dados estruturados e o
sitemap. Se for esvaziado, todos são omitidos — URL relativa não serve para nenhum deles.

## Cartões de compartilhamento

    python3 _fonte/og.py

Gera um PNG de 1200×630 por página em `og/`, com o herói da própria página, usando Fraunces
e Inter descomprimidas dos `.woff2` do repositório. Roda separado do build: a imagem só muda
quando o herói muda. Ao alterar um `h1`, regere o cartão correspondente em `CARDS`.

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
- Sem rolagem horizontal de 345 px para cima
- `prefers-reduced-motion: reduce` respeitado
