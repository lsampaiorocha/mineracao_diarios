import pdfplumber
import os
import json
from unidecode import unidecode
import re
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA



class Orgaos:
  def __init__(self, nome, doc, page, y0, y1):
    self.nome = nome
    self.doc = doc
    self.page = page
    self.y0 = y0
    self.y1 = y1

class Conteudo:
  def __init__(self, nome, doc, publicacao, y1, page1, y0, page2):
    self.nome = nome
    self.doc = doc
    self.publicacao = publicacao
    self.y1 = y1
    self.page1 = page1
    self.y0 = y0
    self.page2 = page2

class Publicacao:
  def __init__(self, texto, tabela, negrito, page1, page2, y1, y0):
    self.texto = texto
    self.tabela = tabela
    self.negrito = negrito
    self.page1 = page1
    self.page2 = page2
    self.y1 = y1
    self.y0 = y0

#Extrai os órgãos presentes de um DOE
def extrair_orgaos_PDF(pdf_files):
  lista = []
  listaadic = []
  with pdfplumber.open(pdf_files) as pdf:
    for P in range(0,len(pdf.pages)):
      pagina = pdf.pages[P]
      i=0
      while(i<len(pagina.rects)):
        temp=''
        for w in range(0,len(pagina.chars)):
          if(pagina.chars[w]['y0'] > pagina.rects[i]['y1'] or pagina.chars[w]['y1'] < pagina.rects[i]['y0'] or pagina.chars[w]['y0'] > 800):
            continue
          if('Bold' in pagina.chars[w]['fontname'] and pagina.chars[w]['x0']>=pagina.rects[i]['x0'] and pagina.chars[w]['x1']<=pagina.rects[i]['x1'] and pagina.chars[w]['y1']>=pagina.rects[i]['y0'] and pagina.chars[w]['y1']<=pagina.rects[i]['y1']):
            temp=temp+pagina.chars[w]['text']
            page = pagina.chars[w]['page_number']
            y0 = pagina.chars[w]['y0']
            y1 = pagina.chars[w]['y1']
          elif('Bold' not in pagina.chars[w]['fontname'] and pagina.chars[w]['x0']>=pagina.rects[i]['x0'] and pagina.chars[w]['x1']<=pagina.rects[i]['x1'] and pagina.chars[w]['y1']>=pagina.rects[i]['y0'] and pagina.chars[w]['y1']<=pagina.rects[i]['y1']):
            temp=''
            break
        if(temp!=''):
          if(temp not in listaadic):
            if('(' not in temp or ')' not in temp):
              for z in range(0,len(temp)):
                if(temp[z].isnumeric() or temp[z].islower()):
                  temp=''
                  break
            if(temp!=''):
              lista.append(temp)
              listaadic.append(temp)
              lista[-1] = Orgaos(temp,pdf_files,page,y0,y1)
            temp=''
        i+=1
  return lista

  #Extrai texto presente entre os órgãos de um documento
#Extrai o texto entre os Órgãos excluindo a seção 'OUTROS'
def extrair_texto_entre_orgaos(lista):
  conteudo = []
  publicacoes = []
  with pdfplumber.open(lista[0].doc) as pdf:
    temp = ''
    tempnegrito = ''
    listanegrito = []
    l=0
    while(l<len(lista)):
      if(l+1==len(lista)):
        limite = len(pdf.pages)
      else:
        limite = lista[l+1].page
      if(lista[l].nome =='OUTROS'):
        break
      publicpage=0
      tabela = False
      y1=0
      py1=0
      page1=0
      y0=0
      py0=0
      page2=0
      for p in range(lista[l].page-1,limite):
        pagina = pdf.pages[p]
        rects = pagina.rects

        for c in range(0,len(pagina.chars)):
          if(pagina.chars[c]['y0']>=800):
            continue
          if(l+1==len(lista)):
            if(pagina.chars[c]['page_number']==lista[l].page):
              if(pagina.chars[c]['y0']<lista[l].y0):
              
                temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
              
                if('*** *** ***' in temp):
                  temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)

            elif(pagina.chars[c]['page_number']>lista[l].page):
              
              temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
              
              if('*** *** ***' in temp):
                temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf,temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)

          elif(pagina.chars[c]['page_number']>=lista[l].page and pagina.chars[c]['page_number']<=lista[l+1].page):
            if(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y0']<lista[l].y0 and pagina.chars[c]['y1']>lista[l+1].y1):
              
                temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
              
                if('*** *** ***' in temp):
                  temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)

            elif(pagina.chars[c]['page_number']==lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              if(pagina.chars[c]['y0']<lista[l].y0):
              
                temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
              
                if('*** *** ***' in temp):
                  temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)
                  
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']<lista[l+1].page):
              
              temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
              
              if('*** *** ***' in temp):
                temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)
                  
            elif(pagina.chars[c]['page_number']>lista[l].page and pagina.chars[c]['page_number']==lista[l+1].page):
              if(pagina.chars[c]['y1']>lista[l+1].y1):
                temp, tempnegrito, listanegrito, publicpage, page2, y1, py1,y0, py0 = ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c)
                if('*** *** ***' in temp):
                  temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)
                  
          elif(temp!=''):
            temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)
            conteudo.append('')
            conteudo[-1] = Conteudo(lista[l].nome,lista[l].doc,publicacoes,y1,page1,y0,page2)
            publicacoes = []   
      if(temp!=''):
        temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0 = SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0)
        conteudo.append('')
        conteudo[-1] = Conteudo(lista[l].nome,lista[l].doc,publicacoes,y1,page1,y0,page2)
        publicacoes = []
      l+=1
    return conteudo
#Extrai o caracter(adicionado para reduzir o tamanho de texto do código)
def ExtrairCaracter(pagina, rects, y1, py1, publicpage, temp, tempnegrito, listanegrito, c):
  for R in range(0,len(rects)):
    if(pagina.chars[c]['x0']>rects[R]['x0'] and pagina.chars[c]['x1']<rects[R]['x1'] and pagina.chars[c]['y1']>rects[R]['y0'] and pagina.chars[c]['y1']<rects[R]['y1']):
      pagina.chars[c]['text'] = ''
      break
  if(y1==0):
    y1=pagina.chars[c]['y1']
    page1=pagina.chars[c]['page_number']
  if(py1==0):
    py1=pagina.chars[c]['y1']
  if(publicpage==0):
    publicpage = pagina.chars[c]['page_number']
  if('Bold' in pagina.chars[c]['fontname']):
    tempnegrito = tempnegrito + pagina.chars[c]['text']
  elif(tempnegrito != ''):
    listanegrito.append(tempnegrito)
    tempnegrito = ''
  temp=temp+pagina.chars[c]['text']
  py0=pagina.chars[c]['y0']
  y0=pagina.chars[c]['y0']
  page2=pagina.chars[c]['page_number']
  
  return temp, tempnegrito, listanegrito, publicpage, page2, y1, py1, y0, py0   
#Separa publicações(adicionado para reduzir o tamanho de texto do código)
def SepararPublicacao(pdf, temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0):
  if(tempnegrito != ''):
    listanegrito.append(tempnegrito)
    tempnegrito=''
  tabela = EncontrarTabela(pdf, publicpage, page2, py1, py0)
  if('*** *** ***' in temp):
    temp = temp.split('*** *** ***')
    publicacoes.append(temp[0])
    temp=''
  else:
    publicacoes.append(temp)
    temp=''
  publicacoes[-1] = Publicacao(publicacoes[-1], tabela, listanegrito, publicpage, page2, py1, py0)
  tabela = False
  publicpage = 0
  py1=0
  py0=0
  listanegrito = []
  return temp, tempnegrito, listanegrito, tabela, publicacoes, publicpage, page2, py1, py0
#Verifica a publicação para detectar tabelas no texto
def EncontrarTabela(pdf, page1, page2, py1, py0):
  tabela = False
  for page in range(page1-1,page2):
    pagina = pdf.pages[page]
    marcadortabela1 = False
    marcadortabela2 = False
    for linhas in pagina.lines:
      #Mesma página
      if(linhas['page_number'] == page1 and linhas['y0']<py1 and marcadortabela1 == False):
        marcadortabela1 = True
      elif(linhas['page_number'] == page1 and linhas['y0']<py1 and linhas['y0']>py0 and marcadortabela1 == True):
        marcadortabela2 = True
      
      #página após o começo da publicação
      elif(linhas['page_number'] > page1 and linhas['page_number'] < page2 and marcadortabela1 == False):
        marcadortabela1 = True
      elif(linhas['page_number'] > page1 and linhas['page_number'] < page2 and marcadortabela1 == True):
        marcadortabela2 = True

      #página no final da publicação
      elif(linhas['page_number'] == page2 and linhas['y0']>py0 and marcadortabela1 == False):
        marcadortabela1 = True
      elif(linhas['page_number'] == page2 and linhas['y0']>py0 and marcadortabela1 == True):
        marcadortabela2 = True

      if(marcadortabela1 and marcadortabela2):
        tabela = True
        break
  return tabela


def BuscaPalavra(text):
  pastajson = os.listdir('json extraidos')
  pastajson.sort()
  resultados = []
  for arquivo in pastajson:
    if(arquivo.endswith('.json')):
      print(arquivo)
      file = open('json extraidos/'+arquivo,'r')
      file = json.load(file)
      for i in range(0,len(file)):
        if(normalizesemespaco(text) in normalizesemespaco(file[i]['TEXTO'])):
          resultados.append(file[i]['TEXTO'])
  return resultados


assunto = [
'rever','demitir','arrecadar','denomina','estabelece','acrescenta','reconhece','declara','concede','altera','fixa',
'Atualizar','Criar','divulga','cessão','aviso','concorrencia','instrucao normativa','instrucao','citacao por edital',
'edital de intimacao','edital de convocacao','edital de notificacao','edital','convocacao',
'ato declaratorio','licenciamento','corrigenda','decreto','portaria administrativa','indenização','pensão',
'reconhecimento de dívida','reconhecimento de despesa','nomeia','valestransportes','arquivar',
'reconhecimento','despesa','divida','exonera','doacao'
'nomear','autorizar','designa','constituir','compor',
'aditivos aos contratos','aditivo ao contrato','aditivo de convênio',
'aditivo','fomento','contrato','declaração','cooperação técnica','cooperação',
'inexigibilidade','permissão de uso','permissão','liberação','acionar','instaurar','elogiar',
'extrato','execucao','mecenato','licenca','dispoe','autoriza','passagens','promoção','substituição',
'ordem de serviço','ordem','rescisão','ratificação','requisição',
'convocação','resolução','homologação','afastamento','aposentar','cessar','tornar sem efeito','tornar',
'diaria','multa','sanção','estagio','bolsa','concessão','abono','desistencia','homologar','compor','progressao',
'valetransporte','reverte','suprimento','mudanca','determina','institui','delegar',
'dispensa','desligar','promover','extinguir','extinta','premiação','apura','afere','oficia',
'negar','homologar','declarar','excluir','gratificação','falecimento','estabelecer','apostilamento',
'prorrogar','deslocamento','matricular','transferir','reform','aposentadoria','aposent','auxilio','parecer',
'revogação','termo de autorização de uso','termo','licitação','dispensa','aprovar','credenciar','anular','notificar',
'viajar','viagem','circulação','absolver','punir','acatar','resultado final','resultado','final'
]


# Função para normalizar o texto: remover acentos e converter para minúsculas
def normalizesemespaco(text):
    text = unidecode(text).lower()
    text = re.sub(r'[-/?!@#%^&*()_+=\[{\]};:|\\<>,.\d\s]', '', text)
    return text


# Função para normalizar o texto: remover acentos e converter para minúsculas
def normalizecomespaco(text):
    text = unidecode(text).lower()
    text = re.sub(r'[-/?!@#%^&*()_+=\[{\]};:|\\<>,.\d]', '', text)
    return text

palavras_importantes_normalizadas = [normalizesemespaco(palavra) for palavra in assunto]
padrao_regex = re.compile('|'.join(palavras_importantes_normalizadas), re.IGNORECASE)

# Função para filtrar termos relevantes que contêm palavras importantes
def filtrar_termos(termos):
    for termo in termos:
        termo_normalizado = normalizesemespaco(termo)
        if padrao_regex.search(termo_normalizado):
          #print(padrao_regex.search(termo_normalizado))
          return termo_normalizado
    return None


def testeDBSCAN(X ,label, epsilon, amostras, metric):
  db = DBSCAN(eps=epsilon,min_samples=amostras,metric='cosine').fit(X)
  labels = db.labels_
  
  label.append(labels)

  n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
  n_noise_ = list(labels).count(-1)
  print('\nResultado DBSCAN')
  print('Número de Clusters: ',n_clusters_)
  print('Número de ruído: ',n_noise_)
  #print('\nHomogeneity: ',metrics.homogeneity_score(labels_true,labels))
  #print('\nCompleteness: ',metrics.completeness_score(labels_true,labels))
  #print('\nV-measure: ',metrics.v_measure_score(labels_true,labels))
  #print('\nAdjusted Rand Index: ',metrics.adjusted_rand_score(labels_true,labels))
  #print('\nAdjusted Mutual Information: ',metrics.adjusted_mutual_info_score(X,labels))
  #print('leafsize: ',leafsize)

  #for i, label in enumerate(labels):
  #    print(f'Amostra {i} -> Cluster: {label}')

  #print('\nepsilon = ',epsilon)
  #print('min_samples = ',amostras)
  #print('\nNúmero estimado de cluster: ',n_clusters_)
  #print('Número estimado de ruído: ',n_noise_)

  #print("Silhouette Coefficient: ", metrics.silhouette_score(X, labels))

  pca = PCA(2)
  Xreduzido = pca.fit_transform(X)

  unique_labels = set(labels)
  core_samples_mask = np.zeros_like(labels, dtype=bool)
  core_samples_mask[db.core_sample_indices_] = True

  colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

  for k, col in zip(unique_labels, colors):
      if k == -1:
          # Black used for noise.
          col = [0, 0, 0, 1]

      class_member_mask = labels == k

      xy = Xreduzido[class_member_mask & core_samples_mask]
      plt.plot(
          xy[:, 0],
          xy[:, 1],
          "o",
          markerfacecolor=tuple(col),
          markeredgecolor="k",
          markersize=14,
      )

      xy = Xreduzido[class_member_mask & ~core_samples_mask]
      plt.plot(
          xy[:, 0],
          xy[:, 1],
          "o",
          markerfacecolor=tuple(col),
          markeredgecolor="k",
          markersize=6,
      )

  plt.title(f'Com medidas: eps={epsilon} e min_samples={amostras}\n Clusters={n_clusters_} | Ruído={n_noise_} | Silhouette={metrics.silhouette_score(X,labels)}')
  #plt.show()
  return n_clusters_

def testeKMeans(X, label, intervalo):
  inercia = []
  coeficientes = []
  valores = intervalo
  templabel = 0

  for p in valores:
    kk = KMeans(p,random_state=0).fit(X)
    inercia.append(kk.inertia_)
    coeficientes.append(metrics.silhouette_score(X,kk.labels_))
    #txt = open(os.path.join('Resultados KMeans amostras','clusters='+format(p)+'[26-06-2024]'+'.txt'),'w')
    #txt.write(f'Coeficiente de silhueta: {coeficientes[-1]}\n')
    #for i,label in enumerate(kk.labels_):
    #    txt.write(f'amostra:{i+1} -> cluster:{label+1}\n')
    #txt.close()
    if(len(valores)<2):
      templabel= kk.labels_
      label.append(templabel)

  maiorsilhueta = 0
  indice = 0
  if(len(coeficientes)>1):
    for i in range(0,len(coeficientes)):
        if(coeficientes[i]>maiorsilhueta):
            maiorsilhueta=coeficientes[i]
            clusters = i+2
  else:
    maiorsilhueta = coeficientes[0]
    clusters = intervalo[0]
  print("\nResultado KMeans")
  print(f'Maior silhueta = {maiorsilhueta}')
  print(f'número de clusters = {clusters}')


  plt.figure(figsize=(8,6))
  plt.plot(valores,inercia,'bo-')
  plt.xlabel('Número de Clusters (k)')
  plt.ylabel('Inércia')
  plt.title('Método do Cotovelo para Encontrar o Número Ideal de Clusters')
  plt.show()

def plotargraficoKMeans(X, clusters):
  kmeans = KMeans(clusters,random_state=0)
  kk = kmeans.fit_predict(X)
  pca = PCA(2)
  Xreduzido = pca.fit_transform(X)
  # Plotando as amostras com cores de acordo com os clusters
  plt.figure(figsize=(8, 6))
  plt.scatter(Xreduzido[:, 0], Xreduzido[:, 1], c=kk, s=50, cmap='viridis')

  # Plotando os centróides dos clusters
  centroids = kmeans.cluster_centers_
  plt.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', marker='x')
  plt.title(f'Com clusters={clusters} | Silhouette={silhouette_score(X,kk)}')
  plt.xlabel('Feature 1')
  plt.ylabel('Feature 2')
  #plt.show()

def plotargraficoAGG(X, label, clusters):
  agg = AgglomerativeClustering(n_clusters=clusters).fit_predict(X)
  
  label.append(agg)
  print("\nResultado AGG")
  print('Silhouette Coefficient: ',silhouette_score(X,agg))
  print('Número de clusters = ',clusters)
  pca = PCA(2)
  Xreduzido = pca.fit_transform(X)
  plt.figure(figsize=(8,6))
  plt.scatter(Xreduzido[:,0], Xreduzido[:,1], c=agg, s=50, cmap='viridis')
  plt.title(f"Com clusters={clusters} | Silhouette = {silhouette_score(X,agg)}")
  #plt.show()
