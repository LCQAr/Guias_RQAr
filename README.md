# Relatório Anual de Acompanhamento da Qualidade do Ar (RQAr)

Sistema de geração automatizada do **Relatório Anual de Acompanhamento da Qualidade do Ar**, nos níveis **nacional** e **estadual**, conforme a estrutura estabelecida pelos Guias Técnicos:

- *Guia Técnico para a Elaboração do Relatório Nacional Anual de Acompanhamento da Qualidade do Ar*
- *Guia Técnico para a Elaboração do Relatório Estadual Anual de Acompanhamento da Qualidade do Ar*

A cada ano é necessário reprocessar os dados de qualidade do ar e produzir uma nova versão dos relatórios. Este repositório automatiza esse processo, funcionando como complemento aos Guias Técnicos de Elaboração do RQAr.

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Instalação](#instalação)
  - [Via clique (recomendado para quem não usa terminal)](#instalação-via-clique-recomendado-para-quem-não-usa-terminal)
  - [Via terminal](#instalação-via-terminal)
- [Como usar](#como-usar)
  - [Análise manual](#análise-manual)
  - [Análise semiautomática](#análise-semiautomática)
  - [Análise automática](#análise-automática)
- [O arquivo `book_master.docx`](#o-arquivo-book_masterdocx)
  - [Marcador de bloco (tabelas/mapas)](#marcador-de-bloco-tabelasmapas)
  - [Marcador embutido (indicadores)](#marcador-embutido-indicadores)
- [Painel Interativo (`dashboard.py`)](#painel-interativo-dashboardpy)
- [Painel de Execução (`build_book.py`)](#painel-de-execução-build_bookpy)
- [O que pode ser alterado](#o-que-pode-ser-alterado)
- [O que **não** deve ser alterado](#o-que-não-deve-ser-alterado)
- [Solução de problemas](#solução-de-problemas)

---

## Sobre o projeto

O sistema separa o relatório em duas camadas com tratamento distinto:

1. **Conteúdo textual** — redigido e mantido inteiramente em `book_master.docx`. É de responsabilidade da equipe técnica e não é alterado de forma automática, exceto pela substituição pontual de marcadores específicos.
2. **Conteúdo derivado de dados** — tabelas, mapas e valores numéricos citados no texto, gerados automaticamente a partir do código-fonte do projeto (notebooks por seção e funções de cálculo em `scripts/`). Pode ser preenchido automaticamente onde houver um marcador `{{...}}` no `book_master.docx`, ou inserido manualmente.

> **Nota:** diferentemente do relatório nacional, cuja estrutura de dados é homogênea, cada estado possui seu próprio conjunto de estações, poluentes monitorados e período de dados disponível. Por isso, gerar o relatório completo sem revisão prévia pode não produzir o resultado esperado.

---

## Estrutura de arquivos

| Arquivo/pasta | Descrição | Responsável pela manutenção |
|---|---|---|
| `book_master.docx` | Relatório-fonte — texto, capítulos, formatação e marcadores `{{...}}`. Único arquivo em que se escreve. | Equipe técnica |
| `secao_X/secao_X.Y.ipynb` | Notebooks que buscam os dados e geram cada tabela/mapa de uma seção (ver Guia de Elaboração do RQAr). | Equipe técnica |
| `compute_stats.py` | Calcula automaticamente as estatísticas do texto (ex.: "62 estações"). | Equipe técnica |
| `scripts/` | Funções auxiliares usadas pelos notebooks. | Equipe técnica |
| `build_book.py` | Script principal — roda todas as seções na ordem correta. | Editar só ao adicionar/remover seções |
| `dashboard.py` | Painel Interativo — revisa cada seção separadamente, por estado, antes de gerar o relatório final. | Editar só ao adicionar/remover seções ou filtros |
| `fill_book.py` | Insere automaticamente tabelas/mapas nos marcadores `{{...}}`. | Não editar |
| `fill_inline_stats.py` | Insere automaticamente números nos marcadores `{{...}}` no corpo do texto. | Não editar |
| `html_to_image.py` | Converte cada tabela/mapa HTML das seções em imagem `.png`. | Não editar |
| `content/` | Imagens das tabelas/mapas (gerada automaticamente). | Não editar |
| `book_master_with_stats.docx` | Cópia temporária do master com os números preenchidos. | Não editar |
| `output/book_filled.docx`, `output/book_filled.pdf` | Relatório final, pronto para diagramar. | Gerado a cada execução |
| `painel.py` | Interface gráfica que roda `build_book.py` sem terminal. | Não editar |
| `Instalar.bat` / `Instalar.command` | Instalador de clique único (instala as dependências). | Equipe técnica |
| `Abrir Painel.bat` / `Abrir Painel.command` | Atalho que abre `painel.py` e roda `build_book.py`. | Equipe técnica |
| `Abrir Dashboard.bat` / `Abrir Dashboard.command` | Atalho que abre `dashboard.py` (Painel Interativo) no navegador. | Equipe técnica |

**Diferença entre os dois painéis:**

- **`painel.py`** (*Abrir Painel*) → autopreenchimento direto: um botão único roda o relatório inteiro de uma vez.
- **`dashboard.py`** (*Abrir Dashboard*) → Painel Interativo no navegador: revisão seção por seção antes de decidir o que compõe o relatório.

São ferramentas complementares, usadas em momentos diferentes do processo (ver [Como usar](#como-usar)).

---

## Instalação

Necessária independentemente da forma de uso escolhida. Executar apenas uma vez.

### Instalação via clique (recomendado para quem não usa terminal)

1. **Instalar o Python** — acesse [python.org/downloads](https://www.python.org/downloads), baixe o instalador e siga as telas padrão de instalação.
   - No **Windows**: marque a caixa **"Add Python to PATH"** antes de instalar.
2. **Baixar o projeto** — na página do repositório, clique em **Code → Download ZIP** e extraia a pasta (ex.: em Documentos).
   - O repositório contém as pastas `Nacional/` e `Estadual/`; use apenas os arquivos correspondentes ao nível de relatório em elaboração.
3. **Instalar as bibliotecas** — dê duplo clique em `Instalar.bat` (Windows) ou `Instalar.command` (Mac/Linux).
   - No **Mac**, na primeira vez: clique com o botão direito → **Abrir** (o macOS bloqueia por padrão arquivos baixados da internet). Depois disso, o duplo clique funciona normalmente.
4. Aguarde a janela de progresso da instalação (pode levar alguns minutos na primeira vez).
5. Aguarde a mensagem **"Instalação concluída!"** e feche a janela.

**Problemas comuns ao abrir `Instalar` ou `Abrir Painel`:**

- **Windows** — tela azul "O Windows protegeu o computador": clique em **Mais informações → Executar assim mesmo**. Erro de permissão: botão direito → Propriedades → marque "Desbloquear" → OK. Persistindo, mova a pasta do projeto para Documentos/Área de Trabalho.
- **Mac** — "não pôde ser executado porque você não possui os privilégios de acesso apropriados": botão direito → **Abrir**. Se persistir, peça à equipe técnica para rodar via `bash` no Terminal.

### Instalação via terminal

> Pressupõe familiaridade com terminal/linha de comando. Sem essa familiaridade, use a instalação via clique acima.

1. Instale o Python (mesmo procedimento acima).
2. Baixe o projeto (Code → Download ZIP) e extraia.
3. No terminal, dentro da pasta raiz do projeto (`Guias_RQAr/`):

```bash
   # Criar ambiente virtual isolado
   python -m venv .guia_venv

   # Ativar o ambiente virtual
   # Windows:
   .guia_venv\Scripts\activate
   # Mac/Linux:
   source .guia_venv/bin/activate

   # Instalar dependências
   pip install -r requirements.txt
```

   O terminal deve exibir `(.guia_venv)` no início da linha, confirmando a ativação. Repita a ativação toda vez que abrir um terminal novo — os passos seguintes só funcionam com o ambiente ativado.

4. Confira que estes arquivos estão na raiz do projeto (mesmo nível de `secao_1/`, `secao_3/`, `secao_4/`, `scripts/`):
   `book_master.docx`, `build_book.py`, `fill_book.py`, `fill_inline_stats.py`, `html_to_image.py`, `compute_stats.py`

---

## Como usar

Existem três formas de operar o sistema — não são etapas obrigatórias/sequenciais; cada equipe escolhe conforme a necessidade.

### Análise manual

**Painel Interativo (`Abrir Dashboard` → Dashboard)**

O responsável pelo relatório usa o Painel Interativo para analisar os dados de cada seção e insere manualmente as informações no `book_master.docx` (texto, tabelas, mapas como imagem e indicadores).

Os marcadores `{{...}}` são substituídos manualmente pela equipe técnica — por isso **não é necessário** rodar o Painel de Execução. O `book_master.docx` já preenchido é o próprio documento final; basta exportá-lo como PDF direto do Word.

✅ **Recomendada** — todo o conteúdo passa pela avaliação da equipe técnica, eliminando o risco de seções vazias, incompletas ou inadequadas (especialmente a nível estadual).

### Análise semiautomática

**Painel Interativo + Painel de Execução (`Abrir Painel` → `build_book.py`)**

Segue a etapa manual, mas apenas para as seções problemáticas ou que exigem atenção — nesses casos, remove-se o marcador e insere-se o conteúdo manualmente. Para as demais seções, o marcador `{{...}}` permanece no texto e é preenchido pela automação.

É necessário rodar o Painel de Execução ao final; as seções tratadas manualmente são ignoradas, por não terem mais `{{...}}` a substituir.

### Análise automática

**Painel de Execução (`Abrir Painel` → `build_book.py`)**

Executa o Painel de Execução sem curadoria prévia. O sistema roda a lista fixa de seções e preenche os marcadores automaticamente, sem conferir a existência de dados adequados.

⚠️ **Usar com cautela** — é a forma mais rápida, mas com maior risco de o relatório final sair com seções vazias, incompletas ou não representativas.

### Comparativo das três formas

| | Manual | Semiautomática | Automática |
|---|---|---|---|
| **Usa o Painel Interativo para** | Decidir tudo manualmente | Decidir só as seções problemáticas | Não usa |
| **Marcadores `{{...}}` sobram no texto?** | Nenhum | Só nas seções não tratadas | Todos |
| **Precisa rodar o Painel de Execução?** | Não | Sim, ao final | Sim |
| **Confiabilidade** | Mais alta | Média | Mais baixa |
| **Recomendação** | ✅ Recomendada | Aceitável, conforme o caso | ⚠️ Usar com cautela |

Em todos os casos, o `book_master.docx` é o único arquivo em que se escreve — a diferença está em quanto dele é preenchido à mão versus preenchido automaticamente pelos marcadores.

---

## O arquivo `book_master.docx`

É o arquivo-fonte do relatório — o único documento em que se escreve, em qualquer uma das três formas de uso. Contém, ao mesmo tempo:

- **Elementos textuais** — capítulos, parágrafos, formatação.
- **Marcadores `{{...}}`** — referências a tabelas, mapas ou indicadores a serem inseridos automaticamente.

As pastas `Nacional/` e `Estadual/` já contêm uma versão preenchida de `book_master.docx`, seguindo o padrão adotado nas versões anteriores do Guia Técnico.

### Marcador de bloco (tabelas/mapas)

Aparece em linha/parágrafo próprio, separado do corpo do texto — ex.: `{{SECAO_03_FIGURA20}}`.

- O nome do marcador é sempre **nome do notebook + nome do arquivo HTML**, tudo em maiúsculo:
  - `secao_3.1.ipynb` + `outputs/tabela.6.html` → `{{SECAO_3_1_TABELA6}}`
  - `secao_4.2.ipynb` + `outputs/figura.10.html` → `{{SECAO_4_2_FIGURA10}}`
- Os arquivos estáticos ficam salvos em `content/` após a execução do `Abrir Painel`.

### Marcador embutido (indicadores)

Aparece ao longo do corpo do texto — ex.: `{{N_TOTAL_2024}}`.

- O nome dentro de `{{ }}` precisa ser **exatamente igual** às chaves retornadas em `compute_stats.py`.
- Ao alterar ou incorporar novos dados, atualize ambos os arquivos para que os marcadores coincidam.
- O local e as estatísticas calculadas para o texto podem ser alterados conforme a necessidade.

---

## Painel Interativo (`dashboard.py`)

Abre no navegador e permite:

- Gerar e visualizar mapas e tabelas interativos;
- Conferir as métricas calculadas;
- Decidir, seção por seção, se o conteúdo automático está adequado ou requer tratamento manual;
- *(nível nacional)* alternar entre visualização do país inteiro ou de estados específicos.

**Passo a passo:**

1. Dê duplo clique em `AbrirDashboard.bat` (Windows) ou `AbrirDashboard.command` (Mac/Linux) — abre uma aba no navegador.
2. Na barra lateral, escolha o **Estado (UF)** e a **Seção** a analisar.
3. Clique em **"▷ Gerar / Atualizar"** — o sistema roda o código da seção/UF selecionada e mostra o resultado.
4. Avalie o resultado:
   - Adequado → pode entrar no relatório.
   - Vazio, incompleto ou sem sentido para o estado → não deve entrar (ou precisa de tratamento diferente).
5. Se for usar: copie/capture a tabela ou mapa e cole manualmente no `book_master.docx` (Inserir → Imagem no Word), **sem** usar o sistema de marcadores.
6. Repita os passos 2–5 para cada seção relevante.
7. Na aba **"Métricas"**, confira os indicadores (total de estações, ativas, inativas etc.) e insira manualmente no texto, se necessário.

### Dado insuficiente em alguma seção

Quando uma seção não pode ser gerada adequadamente para um estado (mapa vazio, tabela incompleta, sem dado):

1. Apague o marcador `{{...}}` correspondente no `book_master.docx` (evita substituição indevida no relatório final).
2. Insira manualmente o conteúdo mais adequado disponível — captura do painel, texto explicando a ausência de dado, ou deixe a seção fora do relatório.
3. Salve o `book_master.docx`.

---

## Painel de Execução (`build_book.py`)

Gera o relatório completo de uma vez, preenchendo automaticamente todo marcador `{{...}}` no corpo do texto.

**Passo a passo:**

1. Abra `book_master.docx` no Word e edite o texto normalmente. Salve e feche o arquivo na pasta do projeto.
2. Dê duplo clique em `Abrir Painel.bat` (Windows) ou `Abrir Painel.command` (Mac/Linux) e clique em **"Atualizar Livro Agora"**.
   - A nível estadual, selecione a UF; a nível nacional, o relatório é gerado para todos os estados.
3. Acompanhe o progresso até aparecer **"Concluído com sucesso!"**.
4. Clique em **"Abrir pasta de resultados"** ou **"Abrir livro (Word)"** para ver o resultado.
5. O sistema cria as pastas `content/`, `_static/` e `output/`, com as figuras, arquivos intermediários e o relatório final (`.docx` e `.pdf`), acessíveis a qualquer momento.

**Alternativa via terminal:**

```bash
python build_book.py
```

Aguarde a mensagem `Done!`/`Concluído!` e abra a pasta `output/` — `book_filled.docx` e `book_filled.pdf` são o resultado final.

### O que é executado

Ao clicar em **"Atualizar Livro Agora"** (ou rodar `python build_book.py`), nesta ordem:

1. Roda cada notebook da lista `NOTEBOOKS` (em `build_book.py`), um a um, gerando tabela/mapa em `secao_X/outputs/*.html`.
2. Converte cada `outputs/*.html` em imagem `.png`, salva em `content/`.
3. Calcula os indicadores via `compute_stats()` (`compute_stats.py`) e substitui os marcadores `{{TOKEN}}` no texto, salvando em `book_master_with_stats.docx` (o original não é alterado).
4. Monta o relatório final, substituindo cada marcador `{{MARCADOR}}` (sozinho em um parágrafo) pela imagem/tabela correspondente em `content/`.
5. Exporta `output/book_filled.docx` e `output/book_filled.pdf`.

---

## O que pode ser alterado

**Na estrutura do relatório:**

- Todo o texto do `book_master.docx`, em qualquer parágrafo que não seja apenas um `{{marcador}}` sozinho.
- Formatação/layout (fontes, cores, cabeçalhos, tamanho de página, estilos de título) — tudo é lido do `book_master.docx` e mantido no resultado final.
- Imagens inseridas manualmente no Word, fora do sistema de marcadores.
- A posição dos marcadores no texto (desde que continuem sozinhos no parágrafo).
- Seções novas sem marcadores, com apenas texto ou imagens.

**No código:**

- **Notebook novo:** escreva normalmente salvando saídas em `secao_X/outputs/*.html` e adicione o caminho na lista `NOTEBOOKS` em `build_book.py`.
- **Número novo no texto:** crie/edite uma função `stats_xxx()` em `compute_stats.py`, garanta que é chamada dentro de `compute_stats()`, e use `{{NOME_DA_CHAVE}}` no texto.
- Lógica de cálculo de qualquer número ou tabela (fonte de dados, filtros, fórmulas).
- Ao adicionar uma nova seção de código ao projeto, inclua-a na lista lida por `build_book.py`.

---

## O que **não** deve ser alterado

- A configuração das pastas de arquivos (o sistema depende da estrutura fornecida).
- `output/book_filled.docx` diretamente — é substituído a cada execução; edições feitas nele são perdidas.
- `book_master_with_stats.docx` — arquivo intermediário, também substituído a cada execução.
- Não renomear/mover `build_book.py`, `fill_book.py`, `fill_inline_stats.py` ou `html_to_image.py` para fora da raiz do projeto.
- Não renomear notebooks ou arquivos em `outputs/` sem atualizar o marcador correspondente (o nome do arquivo define o nome do marcador).
- Não escrever um marcador de bloco misturado com outro texto no mesmo parágrafo.
- Não usar um nome de marcador que não exista nem em `outputs/*.html` nem em `compute_stats()` — o marcador ficará gravado no texto final, sem ser substituído.

---

## Solução de problemas

| Erro | Causa provável / solução |
|---|---|
| `ModuleNotFoundError` | Pacote não instalado — rode `pip install -r requirements.txt` novamente ou instale a biblioteca individualmente. |
| `notebook not found` / `Skipping ... (not found)` | O caminho do notebook em `NOTEBOOKS` não bate com o arquivo real — confira nome e pasta. |
| Marcador aparece no PDF sem substituição (ex.: `{{SECAO_3_2_TABELA1}}`) | Não havia arquivo/dado correspondente — confira se o notebook rodou sem erro e gerou o `outputs/*.html` esperado, ou se a chave existe em `compute_stats()`. |
| Texto sumiu ou mudou sozinho | Confira se a edição foi feita em `book_master.docx` (correto) e não em `output/book_filled.docx` ou `book_master_with_stats.docx` (substituídos a cada execução). |

---

*Documentação elaborada pela equipe técnica (2026).*
