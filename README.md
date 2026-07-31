# Site institucional — Marynna Pereira

Site estático de três páginas, sem dependências externas: as fontes (Fraunces e Inter)
estão embutidas em base64 no CSS de cada página, então nada é carregado de terceiros.
Também não há JavaScript essencial — a página funciona inteira com o script desativado.

## Estrutura publicada

    index.html                       →  /
    empresas/index.html              →  /empresas/
    patrimonio-e-sucessao/index.html →  /patrimonio-e-sucessao/

## Como editar

Os arquivos publicados são gerados. Não edite o HTML da raiz — edite os fontes em `_fonte/`
e rode o build:

    python3 _fonte/build.py

- `_fonte/src/styles.css` — sistema visual (cores, tipografia, componentes)
- `_fonte/src/index.body.html` — conteúdo da home
- `_fonte/src/empresas.body.html` — conteúdo da página de empresas
- `_fonte/src/pessoal.body.html` — conteúdo da página de patrimônio e sucessão
- `_fonte/build.py` — monta cabeçalho, rodapé, meta tags, dados estruturados e reescreve os links

Os fontes usam acentuação normal (UTF-8), não entidades HTML.

Dados que aparecem em todas as páginas (WhatsApp, e-mail, LinkedIn, Lattes, número da OAB,
endereço) ficam no topo de `build.py`. A cidade aparece **só** no endereço do rodapé e no
`addressLocality` dos dados estruturados.

## Sistema visual

Registro de instrumento jurídico: a afirmação fica na coluna de texto e a autoridade que a
sustenta (lei, artigo, ano) fica na margem, separada por um fio. Esse par margem/texto é o
motivo que se repete no site — nas referências legais, na linha do tempo e na ficha do herói.

- **Tinta** `--ink #0F1D18`, um verde quase preto, nas superfícies escuras
- **Papel** `--paper #F6F4EE`, com `--paper-2` nas seções alternadas
- **Latão** `--brass #5C4A18` como único acento; `--brass-2` só em fios e bordas, nunca em texto
- **Fraunces** de 300 a 500 — o display é leve e grande, os títulos pequenos são densos
- **Inter** no corpo, com `tabular-nums` em anos, percentuais e artigos de lei

A numeração 01–04 aparece só nas etapas do trabalho, que são uma sequência de verdade, e vem
de um `counter()` no CSS. Listas que não são sequência não recebem número.

Animação: uma única entrada escalonada no herói, em CSS, desligada sob
`prefers-reduced-motion: reduce`. Não há animação atrelada a rolagem.

## Pendências antes de divulgar

1. Substituir `OAB/CE nº [inserir]` em `build.py` pelo número real de inscrição — exigido pelo
   art. 44 do Código de Ética e Disciplina da OAB.
2. Inserir a fotografia profissional no lugar do espaço reservado (`.portrait`, na home e na
   página de patrimônio).
3. Definir `SITE_URL` em `build.py` para que sejam emitidos `canonical`, `og:url` e a `url` dos
   dados estruturados. Enquanto estiver vazio, as três tags são omitidas.
4. Conferir as referências legais citadas (em especial `LC nº 227/2026`) contra a norma vigente
   na data da publicação.

## Conformidade

O conteúdo foi redigido conforme o Provimento nº 205/2021 do Conselho Federal da OAB: caráter
informativo, sem promessa de resultado, sem menção a honorários ou gratuidade e sem depoimentos
ou casos concretos. A análise completa está na nota técnica que acompanha o projeto.

O termo "especialista" foi substituído por "Advogada — patrimônio, societário e governança",
que descreve a área de atuação sem afirmar titulação. O art. 3º, III do Provimento nº 205/2021
reserva "especialista" a quem tenha título registrado; se o título existir, dá para voltar
atrás editando a linha `.rl` nos três fragmentos de `_fonte/src/`.

## Acessibilidade

- Contraste verificado em navegador: todo texto atinge 7:1 (WCAG AAA), inclusive sobre o papel
  mais escuro das seções `.facts`
- Link "Ir para o conteúdo" antes do cabeçalho
- Foco de teclado visível em todos os elementos interativos (`:focus-visible`)
- Navegação disponível no celular — o cabeçalho quebra em duas linhas em vez de esconder os links
- Sem rolagem horizontal de 345 px para cima
- `prefers-reduced-motion: reduce` respeitado
