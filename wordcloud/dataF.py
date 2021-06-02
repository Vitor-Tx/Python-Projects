from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup

# getNewsList() recebe uma lista com links de notícias(linksList)
# e uma lista vazia(titleList). Ela retorna uma lista com textos 
# das notícias e preenche titleList com os títulos das notícias.
def getNewsList(linksList, titleList = []):
    lineList = [] # lista com as linhas do texto da notícia
    news = [] # lista com as strings contendo cada texto de notícia que será retornada
    for i, notiLink in enumerate(linksList): # para cada link de notícia em linksList
        link = Request(notiLink, headers={'User-Agent': 'Mozilla/5.0'})
        pagina = urlopen(link).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(pagina, "lxml")
        scrapList = (soup.findAll("p")) # todas as tags p e seu conteúdo
        titleList.append(soup.title.text) # adiciona o título da notícia da iteração atual à lista titleList
        getNewsLineList(scrapList, lineList) # chama getNewsLineList, que preenche a segunda lista com o conteúdo útil da primeira
        news.append("\n".join(lineList)) # adiciona o texto da notícia à lista news
    return news

# getNewsLineList() recebe uma lista com blocos de código html(scrapList)
# e outra lista vazia(lineList), que será preenchida com o conteúdo 
# útil(da notícia) de cada linha da primeira lista.
def getNewsLineList(scrapList, lineList):
    for line in scrapList:
        lineList.append(line.text)

link = Request('http://g1.globo.com', headers={'User-Agent': 'Mozilla/5.0'})
pagina = urlopen(link).read().decode('utf-8', 'ignore')
soup = BeautifulSoup(pagina, "lxml")
texto = soup.findAll("a") # todas as tags a e seu conteúdo
links = [] # lista de links de notícias
manchetes = [] # lista de manchetes de notícias
titleList = [] # lista de títulos de notícias
newsList = [] # lista de textos de notícias

for line in texto: 
    scrapped_link = str(line.get("href")) #converte o link(em href) para string
    if scrapped_link.find("/noticia/2019") != -1 and len(line.text) != 0: # verifica se o link é o link de uma notícia e se está junto de uma manchete
        manchetes.append(line.text) # adiciona a manchete na lista de manchetes
        links.append(scrapped_link.strip(" ")) # adiciona o link na lista de links

newsList = getNewsList(links, titleList) # preenche a lista de textos de notícias e a lista de títulos de notícias

df = pd.DataFrame() 
df["Link"] = links
df["Manchete"] = manchetes
df["Noticia"] = newsList
df["Título"] = titleList

lines, columns = df.shape

for i in range(0,lines):
    print( f" link: {i} " + df["Link"][i] + 
    "\nManchete: " + df["Manchete"][i] + "\nTitulo: " + df["Título"][i] + "\nNoticia: " + df["Noticia"][i])