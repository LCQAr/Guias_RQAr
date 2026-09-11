#!/bin/bash
cd "$(dirname "$0")"
if [ ! -f ".guia_venv/bin/python3" ]; then
    echo "ERRO: Ambiente nao encontrado."
    echo "Rode 'Instalar.command' primeiro."
    read -p "Pressione Enter para fechar..."
    exit 1
fi
./.guia_venv/bin/python3 painel.py
