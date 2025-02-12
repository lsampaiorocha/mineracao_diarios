import csv
import unicodedata
import random

def load_subjects(filename):
    """Carrega os assuntos de um arquivo .txt e retorna uma lista."""
    with open(filename, 'r', encoding='utf-8') as file:
        subjects = [line.strip() for line in file if line.strip()]
    return subjects

def preprocess(text):
    text = unicodedata.normalize('NFKD', text.lower())
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text.strip()

# Função para verificar similaridade
def is_similar(half_term, seplag_term):
    half_clean = preprocess(half_term)
    seplag_clean = preprocess(seplag_term)
    return (half_clean == seplag_clean or
            half_clean in seplag_clean.split() or
            seplag_clean.startswith(half_clean))

# Carregar os dados
subjects1 = load_subjects('Dicionário HALF - A até M.txt')
subjects2 = load_subjects('Dicionário SEPLAG - A até M.txt')

# Limitar pares positivos para garantir balanceamento
positive_pairs = []
for half_term in subjects1:
    for seplag_term in subjects2:
        if is_similar(half_term, seplag_term):
            positive_pairs.append((half_term, seplag_term, 1))
            break  # Limita a 1 par positivo por termo HALF

# Garantir que os pares positivos não excedam 50% do total
positive_pairs = positive_pairs[:300]  # Máximo de 300 pares positivos

# Gerar pares negativos
negative_pairs = []
positive_set = set((h, s) for h, s, _ in positive_pairs)
half_terms = [t.strip() for t in subjects1]
seplag_terms = [t.strip() for t in subjects2]

max_attempts = 10000  # Aumento de tentativas
attempts = 0

while len(negative_pairs) < (600 - len(positive_pairs)) and attempts < max_attempts:
    h = random.choice(half_terms)
    s = random.choice(seplag_terms)
    if (h, s) not in positive_set and not is_similar(h, s):
        negative_pairs.append((h, s, 0))
    attempts += 1

# Combinar e embaralhar
all_pairs = positive_pairs + negative_pairs
random.shuffle(all_pairs)

# Garantir exatamente 600 pares
final_pairs = all_pairs[:600]

# Salvar em CSV
with open('pares_assuntos_0_1.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['HALF', 'SEPLAG', 'Rótulo'])
    writer.writerows(final_pairs)

print(f"Arquivo gerado! Pares positivos: {len(positive_pairs)}, Negativos: {len(negative_pairs)}")