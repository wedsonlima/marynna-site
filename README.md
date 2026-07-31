# Site institucional — Marynna Pereira

Site estático de três páginas, sem dependências externas: as fontes (Fraunces e Inter)
estão embutidas em base64 no CSS de cada página, então nada é carregado de terceiros.

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
- `_fonte/build.py` — monta cabeçalho, rodapé, meta tags e reescreve os links

Dados que aparecem em todas as páginas (WhatsApp, e-mail, LinkedIn, Lattes, número da OAB)
ficam no topo de `build.py`.

## Pendências antes de divulgar

1. Substituir `OAB/CE nº [inserir]` pelo número real de inscrição — exigido pelo art. 44 do
   Código de Ética e Disciplina da OAB.
2. Confirmar o uso do termo "especialista" (art. 3º, III do Provimento nº 205/2021).
3. Inserir a fotografia profissional no lugar do espaço reservado.

## Conformidade

O conteúdo foi redigido conforme o Provimento nº 205/2021 do Conselho Federal da OAB:
caráter informativo, sem promessa de resultado, sem menção a honorários ou gratuidade e sem
depoimentos ou casos concretos. A análise completa está na nota técnica que acompanha o projeto.

## Acessibilidade

Todos os textos foram verificados em navegador e atendem à razão de contraste 7:1 (WCAG AAA).
