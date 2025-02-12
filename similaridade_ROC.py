import pandas as pd
import unicodedata
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import stopwords
import nltk

# Configurações iniciais
nltk.download("stopwords")
stopwords_pt = set(stopwords.words("portuguese"))
stopwords_pt.update(["de", "a", "o", "e", "que", "para", "em", "com", "por", "na", "no", "se", "mas", "as", "os", "uma", "um", "do", "dos", "das"])

# Funções de pré-processamento
def remover_acentuacao(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def remover_stopwords(texto):
    return " ".join([p for p in texto.split() if p.lower() not in stopwords_pt])

def preprocessar_texto(texto):
    return remover_stopwords(remover_acentuacao(texto))

# Função para análise hierárquica
def analisar_hierarquia(texto1, texto2):
    texto1_clean = preprocessar_texto(texto1)
    texto2_clean = preprocessar_texto(texto2)
    
    # Verifica se texto2 contém texto1
    if texto1_clean in texto2_clean:
        return len(texto1_clean)/len(texto2_clean)
    return 0

# Função principal de similaridade
def calcular_similaridade_com_hierarquia(texto1, texto2):
    # Pré-processamento
    t1 = preprocessar_texto(texto1)
    t2 = preprocessar_texto(texto2)
    
    # Cálculo de hierarquia
    hierarquia = analisar_hierarquia(texto1, texto2)
    
    # Embeddings e similaridade básica
    modelo = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    emb1 = modelo.encode(t1, convert_to_tensor=True)
    emb2 = modelo.encode(t2, convert_to_tensor=True)
    similaridade = util.cos_sim(emb1, emb2).item()
    
    # Normalizar similaridades próximas de 1 para o intervalo entre 0.8 e 0.9
    # if similaridade > 0.9:
    #    similaridade = 0.8 + (similaridade - 0.9) * np.random.rand()
        
    # similaridades.append(similaridade)

    """ similaridades = [0.78517596, 0.19967378, 0.51423444, 0.59241457, 0.04645041, 0.60754485,
        0.17052412, 0.06505159, 0.94888554, 0.96563203, 0.80839735, 0.30461377,
        0.09767211, 0.68423303, 0.44015249, 0.12203823, 0.49517691, 0.03438852,
        0.9093204,  0.25877998, 0.66252228, 0.31171108, 0.52006802, 0.54671028,
        0.18485446, 0.96958463, 0.77513282, 0.93949894, 0.89482735, 0.59789998,
        0.92187424, 0.0884925,  0.19598286, 0.04522729, 0.32533033, 0.38867729,
        0.27134903, 0.82873751, 0.35675333, 0.28093451, 0.54269608, 0.14092422,
        0.80219698, 0.07455064, 0.98688694, 0.77224477, 0.19871568, 0.00552212,
        0.81546143, 0.70685734] """

    # Combinação com peso para hierarquia
    return min(similaridade * (1 + hierarquia * 0.5), 1.0)  # Aumento de 50% baseado na hierarquia

# Carregamento de dados
def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel com tratamento robusto."""
    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(arquivo, engine='openpyxl')

        # Verificar estrutura do arquivo
        if len(df.columns) < 4:
            raise ValueError("O arquivo deve ter pelo menos 4 colunas.")
            
        # Extrair pares e rótulos
        numeracao = df.iloc[:, 0] # Coluna A
        pares = list(zip(df.iloc[:, 1], df.iloc[:, 2]))  # Colunas B e C
        rotulos = df.iloc[:, 3].astype(int).tolist()    # Coluna D    

        return df, numeracao, pares, rotulos
        
    except Exception as e:
        print(f"Erro ao carregar arquivo: {str(e)}")
        raise

# Função para calcular o índice de Youden para determinar o limiar ideal
def calcular_limiar_ideal(similaridades, rotulos):
    # Curva ROC
    fpr, tpr, thresholds = roc_curve(rotulos, similaridades)
    youden_index = tpr - fpr
    melhor_limiar_idx = np.argmax(youden_index)
    melhor_limiar = thresholds[melhor_limiar_idx]
    return melhor_limiar, fpr, tpr, thresholds, melhor_limiar_idx

# Cálculo de métricas
def calcular_metricas(similaridades, rotulos):
    fpr, tpr, thresholds = roc_curve(rotulos, similaridades)

    # print(rotulos, similaridades)
    # print(fpr, tpr)
    # print(len(thresholds))

    roc_auc = auc(fpr, tpr)
    youden = tpr - fpr
    melhor_idx = np.argmax(youden)
    return thresholds[melhor_idx], fpr, tpr, thresholds, roc_auc

# Geração de gráfico
def plotar_curva_roc(fpr, tpr, thresholds, melhor_limiar_idx, melhor_limiar, roc_auc):
    # Coordenadas do ponto correspondente ao limiar ideal
    fpr_limiar = fpr[melhor_limiar_idx]
    tpr_limiar = tpr[melhor_limiar_idx]

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'Curva ROC (AUC = {roc_auc:.4f})', color='blue')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Classificador Aleatório')
   
    # Destacar o ponto correspondente ao limiar ideal
    plt.scatter(fpr_limiar, tpr_limiar, color='red', label=f'Limiar Ideal = {melhor_limiar:.4f}', zorder=5)
    plt.xlabel('Taxa de Falsos Positivos')
    plt.ylabel('Taxa de Verdadeiros Positivos')
    plt.title('Curva ROC com Análise de Hierarquia')
    plt.legend()
    plt.savefig('curva_roc1000.png', dpi=300)
    plt.close()

    # Avaliar classificações para diferentes limiares
    for threshold in [1.0, 0.5, 0.3]:
        predicoes = [1 if sim >= threshold else 0 for sim in similaridades]
        print(f"\nLimiar: {threshold}, Previsões: {predicoes}")

# Execução principal
if __name__ == "__main__":
    # Carregar dados
    df, numeracao, pares, rotulos = carregar_dados("Validação de Assuntos - 1000 pares.xlsx")
    
    # Calcular similaridades
    similaridades = [calcular_similaridade_com_hierarquia(t1, t2) for t1, t2 in pares]
    
    # Adicionar similaridades à coluna E
    df['Predição/Similaridade'] = similaridades  # Adiciona uma nova coluna 'Predição/Similaridade'
    
    # Salvar o arquivo com as similaridades
    df.to_excel("Validação de Assuntos - 1000 pares com similaridades.xlsx", index=False)

    # Calcular métricas
    melhor_limiar, fpr, tpr, thresholds, roc_auc = calcular_metricas(similaridades, rotulos)
    
    # Gerar gráfico
    plotar_curva_roc(fpr, tpr, thresholds, np.argmax(tpr - fpr), melhor_limiar, roc_auc)
    
    # Calcular AUC
    roc_auc = auc(fpr, tpr)

    print("Pares:", pares)
    print("Similaridades:", similaridades)
    print("Rótulos:", rotulos)
    
    # Exibir resultados
    print(f"AUC: {roc_auc:.4f}")
    print(f"Limiar Ideal: {melhor_limiar:.4f}")
    print("\nExemplo de Pares:")
    for i in np.random.choice(len(pares), 5, replace=False):
        print(f"Par {numeracao[i]}: {pares[i]} | Similaridade: {similaridades[i]:.4f} | Rótulo: {rotulos[i]}")