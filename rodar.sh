#!/bin/bash

# Diretório de saída
OUTPUT_DIR="out_correcao"

# Cria o diretório de saída, se não existir
mkdir -p "$OUTPUT_DIR"

# Loop para arquivos de 01 a 22
for i in $(seq -w 1 22); do
    INPUT_FILE="exemplos/$i"
    OUTPUT_FILE="$OUTPUT_DIR/output_$i.txt"

    echo "Processando $INPUT_FILE..."
    python3 tp.py "$INPUT_FILE" --decimals 2 --digits 2 --policy largest > "$OUTPUT_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "Saída salva em $OUTPUT_FILE"
    else
        echo "Erro ao processar $INPUT_FILE. Veja $OUTPUT_FILE para detalhes."
    fi
done

echo "Processamento concluído."
