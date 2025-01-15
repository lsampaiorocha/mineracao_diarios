import unicodedata
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Carregar tokenizador e modelo
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Função para remover acentuações de um texto
def remover_acentuacao(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

# Função para calcular embeddings com pooling CLS token
def get_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**tokens)
    return outputs.last_hidden_state[:, 0, :].squeeze()  # Usar CLS token

# Função para comparar cada linha do arquivo1 com todas as linhas do arquivo2
def comparar_arquivos(arquivo1, arquivo2, arquivo_saida):
    # Ler os arquivos
    with open(arquivo1, 'r', encoding='utf-8') as f1, open(arquivo2, 'r', encoding='utf-8') as f2:
        # Remover acentuações das linhas
        linhas1 = [remover_acentuacao(linha.strip()) for linha in f1.readlines()]
        linhas2 = [remover_acentuacao(linha.strip()) for linha in f2.readlines()]
    
    # Calcular similaridade para cada linha de arquivo1 com todas as linhas de arquivo2
    resultados = []
    for linha1 in linhas1:
        emb1 = get_embedding(linha1)
        for linha2 in linhas2:
            emb2 = get_embedding(linha2)
            similaridade = F.cosine_similarity(emb1, emb2, dim=0).item()  # Obter valor escalar
            resultados.append((linha1, linha2, similaridade))
    
    # Salvar resultados em um novo arquivo
    with open(arquivo_saida, 'w', encoding='utf-8') as saida:
        for linha1, linha2, similaridade in resultados:
            saida.write(f"Texto 1: {linha1}\nTexto 2: {linha2}\nSimilaridade: {similaridade:.4f}\n\n")
    
    print(f"Resultados salvos em: {arquivo_saida}")

# Caminhos dos arquivos
arquivo1 = "Dicionário HALF - A a H.txt"  # Substitua pelo caminho do primeiro arquivo
arquivo2 = "Dicionário SEPLAG - A a H.txt"  # Substitua pelo caminho do segundo arquivo
arquivo_saida = "resultados_similaridade_final.txt"  # Caminho do arquivo de saída

# Chamar a função para comparar os arquivos
comparar_arquivos(arquivo1, arquivo2, arquivo_saida)