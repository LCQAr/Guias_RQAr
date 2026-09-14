# Relatório Nacional Anual de Acompanhamento da Qualidade do Ar

Arquivos complementares ao Guia de Elaboração do Relatório Nacional Anual
de Acompanhamento da Qualidade do Ar.

## Estrutura

```
Nacional/
├── book_master.docx              # Documento-fonte — único arquivo em que se escreve
├── book_master_with_stats.docx   # Gerado automaticamente — não editar
├── build_book.py                 # Motor do sistema (roda todas as seções)
├── dashboard.py                  # Painel Interativo (Streamlit)
├── painel.py                     # Autopreenchimento (janela com botão)
├── fill_book.py                  # Insere tabelas/mapas nos marcadores — não editar
├── fill_inline_stats.py          # Insere números no texto — não editar
├── html_to_image.py              # Converte HTML em imagem — não editar
├── requirements.txt              # Bibliotecas necessárias
├── Instalar.bat / .command       # Instalador de clique único
├── AbrirDashboard.bat / .command # Abre o Painel Interativo
├── Abrir Painel.bat / .command   # Abre o Autopreenchimento
├── scripts/                      # compute_stats.py e funções auxiliares
├── secao_1/                      # Notebooks — Seção 1 do relatório
├── secao_3/                      # Notebooks — Seção 3 do relatório
├── secao_4/                      # Notebooks — Seção 4 do relatório
├── content/                      # Gerado automaticamente — imagens das seções
└── output/                       # Gerado automaticamente — relatório final (.docx/.pdf)
```
