import os
import pandas
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Certifique-se de ter atualizado o pacote
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import tiktoken
from Funções import assunto, normalizecomespaco

# Carregar variáveis do .env
load_dotenv()

# Definir a chave da API
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para contar tokens usando tiktoken
def contar_tokens(texto, modelo="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(modelo)
    return len(enc.encode(texto))

def AnalisepublicacaoJSON(contexto, model="gpt-4o-mini"):
    # Configurando o modelo ChatOpenAI
    chat = ChatOpenAI(
        model_name=model,
        temperature=0,
    )

    # Criando o template de prompt para o chat
    template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "Você é um analista de publicações de diários oficiais do governo em busca de categorizar as publicações por assunto."
            "Utilize o conteúdo da publicação para responder às perguntas."
            "Seja conciso nas respostas, entregando apenas as informações solicitadas."
            "Publicação: {contexto}"
        ),
        HumanMessagePromptTemplate.from_template(
            "{input}"
        )
    ])

    # Usando `|` para conectar o template ao chat
    question_answer_chain = template | chat

    q1 = """
    1-Sua tarefa consiste em responder apenas com o assunto que melhor descreve a publicação,

    2-Se houver uma combinação válida de assuntos que descreve melhor o texto junte um, dois ou três assuntos separando-os com / como ficar melhor de acordo com os exemplos
    
    Exemplos = [portaria/autorização/viagem, portaria/exoneração, portaria/concessão/diárias, autorização/viagem/diárias]
    
    3-Se o texto tiver portaria, decreto, corrigenda ou lei, deverá vir primeiro na lista de resultados,
    
    4-Caso nenhum deles descreva corretamente, retorne apenas "Nenhum Assunto Corresponde:" e uma sugestão com 1 a 5 palavras.
    
    Assuntos = ['portaria','decreto','lei','corrigenda','revisão','demissão','arrecadação','denominação',
    'acréscimo','reconhecimento','declaração','concessão','alteração','fixação',
    'Atualização','Criação','divulgação','cessão','aviso','concorrência','instrução normativa','instrução','citação por edital',
    'edital de intimação','edital de convocação','edital de notificação','edital','convocação',
    'ato declaratorio','licenciamento','decreto','portaria administrativa','indenização','pensão',
    'reconhecimento de dívida','reconhecimento de despesa','nomeação','valestransportes','arquivamento',
    'reconhecimento','despesa','divida','exoneração','doação','registro de preços,'registro','reestruturacao',
    'autorização','designação','constituição','composição','relatório','quitação','conclusão',
    'aditivos aos contratos','aditivo ao contrato','aditivo de convênio','contratação',
    'aditivo','fomento','contrato','cooperação técnica','cooperação','relação de pareceres',
    'inexigibilidade','permissão de uso','permissão','liberação','acionamento','instauração','elogio',
    'extrato','execução','mecenato','licença','disposição','passagens','promoção','substituição',
    'ordem de serviço','ordem','rescisão','ratificação','requisição','pagamento',
    'convocação','resolução','homologação','afastamento','aposentadoria','cessão','tornar sem efeito','tornar',
    'diária','multa','sanção','estágio','bolsa','concessão','abono','desistência','homologação','composição','progressão',
    'valetransporte','reversão','suprimento','mudança','determinação','instituição','delegação',
    'dispensa','desligamento','promoção','extinção','premiação','apuração','aferimento','oficialização','Reintegração','Integração','Parceria','Indicação',
    'negação','exclusão','gratificação','falecimento','estabelece','apostilamento','definição','Aditamento','Inventário','
    'prorrogação','deslocamento','matrícula','transferência','reforma','auxilio','parecer','errata','capacitação','medida disciplinar',
    'revogação','termo de autorização de uso','termo','licitação','aprovação','credenciamento','anulação','notificação',
    'viagem','circulação','absolvição','punição','acatamento','resultado final','resultado','final','regulamentação','recurso','administrativo']
    """

    # Concatenando o contexto e a pergunta para contar os tokens
    input_text = f"Publicação: {contexto}\n\n{q1}"
    prompt_tokens = contar_tokens(input_text, model)

    # Executando a análise do documento
    response = question_answer_chain.invoke({"contexto": contexto, "input": q1})
    
    # Acessar diretamente o conteúdo da mensagem
    resposta = response.content
    completion_tokens = contar_tokens(resposta, model)

    return resposta, prompt_tokens, completion_tokens



for z in os.listdir('json a avaliar'):

    # Carregar o arçãovo JSON
    with open("json a avaliar/"+z, "r", encoding="utf-8") as f:
        dados = json.load(f)

        # Inicializando listas para armazenar tokens para o CSV
        prompt_tokens_list = []
        completion_tokens_list = []

        # Iterar sobre os elementos do JSON
        for i, item in enumerate(dados):
            # Acessar o documento a ser analisado, assumindo que está no campo 'documento'
            documento = item.get('TEXTO', "")

            # Verificar se o documento não está vazio
            if documento:
                print(f"\nAnalisando o documento {i + 1}:")
                total_tokens = contar_tokens(documento)
                print(f"Número total de tokens no documento: {total_tokens}")

                # Se o documento tiver mais que 5000 tokens, fragmentar o texto em duas partes e analisar cada uma
                if total_tokens >= 5000:
                    
                    fragmentoum = documento[0:10000]
                    fragmentodois = documento[-10000:-1]
                    for termo in assunto:
                        if(normalizecomespaco(termo) in normalizecomespaco(fragmentoum)):
                            resposta, prompt_tokens, completion_tokens = AnalisepublicacaoJSON(contexto=fragmentoum)
                            break
                        elif(termo==assunto[-1]):
                            resposta, prompt_tokens, completion_tokens = AnalisepublicacaoJSON(contexto=fragmentodois)
                    
                else:
                    resposta, prompt_tokens, completion_tokens = AnalisepublicacaoJSON(contexto=documento)
        
                # Adicionar os resultados ao item
                item['assunto'] = resposta
                item['prompt_tokens'] = prompt_tokens
                item['completion_tokens'] = completion_tokens
        
                # Adicionar os tokens às listas para o CSV
                prompt_tokens_list.append(prompt_tokens)
                completion_tokens_list.append(completion_tokens)
        
                # Imprimir a resposta
                print(resposta)
        
            else:
                # Se o documento estiver vazio, adicionar uma resposta padrão
                print(f"Documento {i + 1} está vazio. Nenhuma análise realizada.")
                item['analise'] = "Documento vazio."
                item['prompt_tokens'] = 0
                item['completion_tokens'] = 0
                prompt_tokens_list.append(0)
                completion_tokens_list.append(0)

        # Salvar o arquivo JSON atualizado
        with open("json a avaliar(analisados)/"+z, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
            
'''
        # Criar DataFrame para salvar os tokens em CSV
        df_tokens = pd.DataFrame({
            'prompt_tokens': prompt_tokens_list,
            'completion_tokens': completion_tokens_list
        })

'''