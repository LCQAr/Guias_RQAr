# Guias RQAr — Relatório de Acompanhamento da Qualidade do Ar

Este repositório reúne os arquivos e ferramentas utilizados na elaboração
dos Relatórios Anuais de Acompanhamento da Qualidade do Ar (RQAr), nas
esferas **Nacional** e **Estadual**, incluindo os processos de tratamento
dos dados brutos que alimentam ambos os relatórios.

## Estrutura do repositório

```
Guias_RQAr/
├── Nacional/          # Geração do Relatório Nacional (RQAr)
├── Estadual/           # Geração dos Relatórios Estaduais (REQAr)
└── Tratamento_dados/    # Processamento dos dados brutos de origem
    ├── funcoes_monitoramento/
    └── funcoes_rede/
```

### `Nacional/`

Contém os notebooks, scripts e o sistema de autopreenchimento responsáveis
pela geração do **Relatório Nacional de Acompanhamento da Qualidade do
Ar**, organizados em `secao_1/`, `secao_3/`, `secao_4/` e `scripts/`.
Inclui o documento-fonte do relatório (`book_master.docx`) e o sistema de
geração automática (`build_book.py`, `dashboard.py`). Instruções completas
de instalação e uso no `README.md` da própria pasta.

### `Estadual/`

Contém a estrutura equivalente para geração dos **Relatórios Estaduais
(REQAr)**, com a mesma arquitetura do Nacional — notebooks organizados
por seção, sistema de autopreenchimento e Painel Interativo —, mas com
suporte à filtragem dos dados por Unidade Federativa (UF), já que cada
estado possui seu próprio conjunto de estações, poluentes monitorados e
período de dados disponível. Instruções completas no `README.md` da
própria pasta.

### `Tratamento_dados/`

Contém os scripts responsáveis pelo processamento dos dados brutos de
qualidade do ar antes de serem consumidos pelos relatórios Nacional e
Estadual, organizados em:
- `funcoes_monitoramento/` — funções relacionadas aos dados de
  monitoramento (estações, poluentes, séries temporais).
- `funcoes_rede/` — funções relacionadas à estrutura da rede de
  monitoramento.

## Como usar

O fluxo geral é:

1. **Tratamento dos dados** (`Tratamento_dados/`) — processa os dados
   brutos e os disponibiliza no formato utilizado pelos relatórios.
2. **Geração dos relatórios** (`Nacional/` e/ou `Estadual/`) — cada pasta
   contém um sistema de autopreenchimento independente e autocontido, com:
   - **Instalação** de clique único (`Instalar.bat` / `Instalar.command`);
   - **Painel Interativo** no navegador (`AbrirDashboard.bat` /
     `AbrirDashboard.command`), para análise e curadoria dos dados seção
     por seção antes de compor o relatório;
   - **Painel de Execução** (`Abrir Painel.bat` / `Abrir Painel.command`),
     para geração automática do relatório final em Word e PDF.

Consulte o `README.md` dentro de cada pasta (`Nacional/README.md` e
`Estadual/README.md`) para o passo a passo completo de instalação e uso.

## Requisitos gerais

- Python 3.10 ou superior
- Ambiente virtual isolado por pasta (`.guia_venv`), criado automaticamente
  pelo instalador de cada sistema
- Consulte o `requirements.txt` de cada pasta (`Nacional/` e `Estadual/`)
  para a lista completa de bibliotecas

## Sobre o projeto

Este sistema foi desenvolvido para apoiar a elaboração padronizada dos
Relatórios Anuais de Acompanhamento da Qualidade do Ar, como complemento
aos respectivos Guias Técnicos de Elaboração. O presente repositório faz parte
da série de ferramentas previstas pelo projeto em conjunto ao Ministério do Meio
Ambiente e Mudança do Clima produzido por meio do TED Nº 001987/0002/2024 SQA, 
Projeto Instrumentos para a Gestão da Qualidade do Ar no Brasil. 
