import abc
import requests
import urllib3
import re
import pandas as pd
from bs4 import BeautifulSoup
import sys
import pathlib
import io
from datetime import date, time, datetime
urllib3.disable_warnings()
path =  str(pathlib.Path().absolute())
DFpath = path + '\\Planilhas\\'
Textpath = path + '\\Text\\'

def string_list_to_txt(assunto:str, end:str, list = None):
    if(list == None):
        return
    #try:
    file = io.open(Textpath+assunto+"_"+end+".txt", "w", encoding="utf-8")
    #except(FileNotFoundError, IOError):
        #file.close()
        #file = io.open(Textpath+assunto+"_"+end+".txt", "w", encoding="utf-8")
    for line in list:
        file.write(line+"\n")
    file.close()

class News_Scraper(abc.ABC):
    news_vehicle = ''
    news_site = ''
    assunto = ''
    max_pages = 0
    pages = max_pages
    soup_tags = []
    tag_attrs = []
    attr_values = []
    keys = []
    key_dict = {'':''}
    link_list = []
    temp_link_list = []
    date_tuple = ()
    date_list = []
    title_list = []
    news_list = []
    
    def __init__(self, assunto : str, pages : int):
        self.assunto = assunto 
        if(self.max_pages < pages):
            self.pages = self.max_pages
        else: self.pages = pages

    def set_assunto(self, assunto : str):
        self.assunto = assunto
    
    def set_key_values(self, values : list) -> int:
        self.key_dict = dict(zip(self.keys, values))

    def prepare_pages(self, i: int):
        self.key_dict['page'] = str(i)
        return requests.get(self.news_site, params=self.key_dict, verify=False) # request para cada busca
    
    def get_news_blocks(self, i:int, tag):
        if(tag == None):
            return None
        return tag.findAll(self.soup_tags[0], attrs={self.tag_attrs[0]:self.attr_values[0]}) # tags html onde estão as chamadas das notícias

    @abc.abstractmethod
    def get_direct_link(self, tag, i : int) -> str:
        pass

    @abc.abstractmethod
    def get_date(self, soup) -> date:
        pass

    
    def scrape_links(self) -> int:
        if(self.assunto == ''): 
            print("Nenhum assunto foi configurado para a pesquisa\n")
            return -1
        captured = 0 # número de links capturados
        for i in range(1, self.pages + 1):
            print(f"\nTentando acessar a página {i} da pesquisa...\n")
            site_html = self.prepare_pages(i)
            if site_html == None:
                continue
            if(site_html.status_code != 200): # se status_code não for 200, houve algum erro
                print(f"\nErro, não consegui acessar essa página da pesquisa: {i}\n")
                continue
            site_main_soup = BeautifulSoup(site_html.text, "html5lib") 
            news_blocks = self.get_news_blocks(i, site_main_soup)
            if(news_blocks == None or len(news_blocks) == 0): # se nenhuma tag com essa estrutura existir, quer dizer que não há mais notícias(ou nenhum resultado foi encontrado)
                print(f"\nErro, não encontrei nenhuma notícia nessa página: {i}\n")
                break
            for tag in news_blocks: # pra cada bloco de notícia encontrado na página atual
                direct_link = self.get_direct_link(tag, i)
                if(direct_link == ''):
                    continue
                if(direct_link in self.link_list):
                    continue
                self.link_list.append(direct_link)
                print(f"\nConsegui pegar o link dessa notícia: {direct_link}\n")
                captured += 1
        print(f"\n Consegui capturar {captured} links.\n")
        self.key_dict['page'] = '1'
        return 0

    @abc.abstractmethod
    def scrape_paragraphs(self, tag):
        pass
    
    def scrape_news(self):
        if(len(self.link_list) == 0):
            print("não há nenhum link de notícia para acessar!\n")
        captured = 0 # número de notícias capturadas
        tries = 0 # número de tentativas de captura de notícia
        total = len(self.link_list) # total de links
        left = total # número de links restantes a serem acessados
        for link in self.link_list: # pra cada link na lista de links
            print(f"\nTentando pegar a notícia desse link({tries} tentativas, {captured} sucessos, {left} restantes): {link}\n")
            tries += 1
            left -= 1
            try:
                paragrafos_noticia = [] # lista com os parágrafos da notícia
                link_html = requests.get(link, verify=False) # request para o link atual
                if(link_html.status_code != 200): # se status_code não for 200, houve algum erro
                    print(f"\nErro, não consegui acessar esse link: {link}\n")
                    continue 
                link_html.encoding= "utf-8"
                link_soup = BeautifulSoup(link_html.text, "html5lib") 
                p_tags = self.scrape_paragraphs(link_soup)
                if(p_tags == None or len(p_tags) == 0): # se nenhuma tag for encontrada, ocorreu um erro
                    print(f"\nErro, acessei o link, mas não consegui pegar a notícia: {link}\n")
                    continue 
            except Exception:
                print(f"\nErro ao acessar o link dessa notícia: {link}")
                continue
            for tag in p_tags: # pra cada tag(com parágrafo)
                paragrafos_noticia.append(tag.text) # adiciona na lista de parágrafos
            titulo = link_soup.find(self.soup_tags[4], attrs={self.tag_attrs[4]:self.attr_values[4]})
            if(titulo == None): # se o título não for encontrado
                titulo = "N/A"
            else: 
                titulo = re.sub(r'\s{0,}\n{1,}\s{0,}', '', titulo.text)
                #titulo = titulo.text.encode("raw_unicode_escape").decode("utf-8", "ignore") #pro caso de o titulo sair com símbolos estranhos substituindo acentos e etc
            date = self.get_date(link_soup)
            if(date == None):
                date = "N/A"
            self.title_list.append(titulo)
            self.date_list.append(date)
            # re.sub(r'\s{0,}\n{1,}\s{0,}', ' ', "".join(paragrafos_noticia).replace(u'\xa0', u' ')) 
            # "".join(paragrafos_noticia).replace(u'\xa0', u' ')
            noticia = re.sub(r'\s{0,}\n{1,}\s{0,}', ' ', "".join(paragrafos_noticia).replace(u'\xa0', u' ')).strip()  # junta os parágrafos num texto completo e limpa espaços e \n desnecessários
            self.news_list.append(noticia) # adiciona o texto na lista de notícias
            self.temp_link_list.append(link)
            print(f"\nNotícia Capturada com sucesso: {titulo}\n")
            captured += 1
        print(f"\n Consegui capturar {captured} notícias. {len(self.link_list)-captured} notícias deixaram de ser capturadas.\n")
        return self.temp_link_list
    
    def scrape(self):
        self.scrape_links()
        string_list_to_txt(assunto, 'links', self.link_list)
        self.scrape_news()

    def createDF(self):
        df = pd.DataFrame(index = None)
        try:
            df["Título"] = self.title_list
            df["Notícia"] = self.news_list
            if(len(self.date_list) != len(self.news_list)):
                print(f"\nhmmmmm temos um probleminha. datas = {len(self.date_list)} e noticias = {len(self.news_list)} \n")
            df["Data"] = self.date_list
            if(len(self.link_list) != len(self.news_list) and len(self.temp_link_list) == len(self.news_list)):
                df["Link"] = self.temp_link_list
            else: 
                df["Link"] = self.link_list
            try:
                file = io.open(DFpath+self.assunto+'_'+self.news_vehicle+".csv", "r", encoding="utf-8")
                filename = input(f"\nParece que já existe um arquivo com o nome '{self.assunto+'_'+self.news_vehicle+'.csv'}'. Insira um novo nome para o arquivo. Caso queira que o arquivo seja substituído, digite 'sub'.\n")
                if(filename != 'sub'):
                    df.to_csv(DFpath+filename, index=False) 
                else:
                    df.to_csv(DFpath+self.assunto+'_'+self.news_vehicle+".csv", index=False)
                file.close()        
            except(FileNotFoundError, IOError):
                df.to_csv(DFpath+self.assunto+'_'+self.news_vehicle+".csv", index=False)
            #s_n = input(f"\nOk, com as notícias capturadas, você gostaria de gerar um arquivo .txt com as notícias com o nome {self.assunto+'_'+self.news_vehicle}_news.txt? (digite 's' caso queira) ")
            #if(s_n == "s"):
            string_list_to_txt(self.assunto+'_'+self.news_vehicle, "news", self.news_list)
        except Exception as e:
            print("\n"+ e + "\n")
            sys.exit()



class G1_Scraper(News_Scraper):

    def __init__(self, assunto:str, pages:int):
        self.news_vehicle = "G1"
        self.max_pages = 40
        super().__init__(assunto, pages)
        self.news_site = 'https://g1.globo.com/busca/'
        self.soup_tags = ['li', 'div', 'meta', 'p', 'h1']
        self.tag_attrs = ['class', 'class', 'http-equiv', 'class', 'class']
        self.attr_values = ['widget widget--card widget--info', 'widget--info__text-container', 'refresh', 'content-text__container', 'content-head__title']
        self.keys = ['q', 'page', 'order', 'species']
        self.key_dict = dict([('q', assunto), ('page', '1'), ('order', 'relevant'), ('species', 'notícias')])

    def set_periodo(self, simpleperiod = '', reset = False, fromperiod = '', toperiod = ''):
        if(fromperiod == '' or toperiod == ''):
            if 'from' in self.key_dict:
                del self.key_dict['from']
            if 'to' in self.key_dict:
                del self.key_dict['to']
            return
        if(reset == True):
            return 
            
        if(simpleperiod in ["now-1h", "now-1d", "now-1w", "now-1M", "now-1y"]): 
            self.key_dict["from"] = simpleperiod
            return
        if(fromperiod != '' and toperiod != ''):
            self.key_dict["from"] = fromperiod + 'T00:00:00-0300'
            self.key_dict["to"] = toperiod + 'T23:59:59-0300'

    def set_order(self, order : str):
        if order in ['relevant', 'recent']:
            self.key_dict['order'] = order
    def prepare_pages(self, i: int):
        self.key_dict['page'] = str(i)
        req = requests.get(self.news_site, params=self.key_dict, verify=False) # request para cada busca
        print(f'\n{req.url}\n')
        return req

    def get_direct_link(self, tag, i : int) -> str:
        referral_link = "https:" + tag.find(self.soup_tags[1], attrs={self.tag_attrs[1]:self.attr_values[1]}).find("a").get("href") # link de redirecionamento
        referral_html = requests.get(referral_link, verify=False) # request com o link de redirecionamento contido na div
        if(referral_html.status_code != 200): # se status_code não for 200, houve algum erro
            print(f"\nErro, não consegui acessar o link direto de uma das notícias da página: {i}\n")
            return ''
        referral_soup = BeautifulSoup(referral_html.text, "html5lib") # acessa o html do link de redirecionamento para obter o link direto
        direct_link = referral_soup.find(self.soup_tags[2], attrs={self.tag_attrs[2]:self.attr_values[2]}).get("content").strip("0;URL='") # link direto para a notícia
        return direct_link

    def get_date(self, soup) -> date:
        try:
            date = datetime.fromisoformat(soup.find('time', attrs={'itemprop':'datePublished'}).get("datetime").strip('Z')).date()
            return date  
        except Exception:
            return None


    def scrape_paragraphs(self, tag):
        return tag.find_all(self.soup_tags[3], attrs={self.tag_attrs[3]:self.attr_values[3]}) # obtenção das tags html com os parágrafos
        

class Gazeta_Scraper(News_Scraper):
    def __init__(self, assunto:str, pages:int):
        self.news_vehicle = "Gazeta do Povo"
        self.max_pages = 30
        super().__init__(assunto, pages)
        self.news_site = 'https://www.gazetadopovo.com.br/republica/'
        self.soup_tags = ['article', 'a', 'div', 'p', 'h1']
        self.tag_attrs = ['class', 'class', 'class', '', 'class']
        self.attr_values = ['c-item', 'trigger-gtm', 'c-body', '', 'c-title']
        self.keys = ['']
        self.key_dict = {'':''}

    def get_direct_link(self, tag, i : int) -> str:
        direct_link = tag.find(self.soup_tags[1], attrs={self.tag_attrs[1]:self.attr_values[1]})
        if(direct_link == None): 
            print(f"\nErro, não consegui acessar o link direto de uma das notícias da página: {i}\n")
            return ''
        direct_link = direct_link.get('href')
        return 'https://www.gazetadopovo.com.br' + direct_link
    
    def prepare_pages(self, i: int):
        if(i==1):
            return requests.get(self.news_site)
        return requests.get(self.news_site + str(i))

    def get_date(self, soup) -> date:
        try:
            date = datetime.strptime(soup.find("div", attrs={'class':'c-date-time'}).find('span').text, '%d/%m/%Y %H:%Mh').date()
            return date  
        except Exception:
            return None
    
    def scrape_paragraphs(self, tag):
        if(tag == None): 
            return None
        paragraphs = tag.find(self.soup_tags[2], attrs={self.tag_attrs[2]:self.attr_values[2]})
        if(paragraphs == None):
            return None 
        return paragraphs.findAll(self.soup_tags[3]) # obtenção das tags html com os parágrafos
    
    

class Epoca_Scraper(News_Scraper):
    def __init__(self, assunto:str, pages:int):
        self.news_vehicle = "Época"
        self.max_pages = 40
        super().__init__(assunto, pages)
        self.news_site = 'https://epoca.globo.com/busca/'
        self.soup_tags = ['a', 'a', 'meta', 'p', 'h1', 'div']
        self.tag_attrs = ['', '', 'http-equiv', '', 'class', 'class']
        self.attr_values = ['', '', 'refresh', '', 'article__title', 'article__content-container protected-content']
        self.keys = ['q', 'page', 'species']
        self.key_dict = dict([('q', assunto), ('page', '1'), ('species', 'notícias')])

    def get_direct_link(self, tag, i : int) -> str:
        referral_link = "https:" + tag.get("href") # link de redirecionamento
        referral_html = requests.get(referral_link, verify=False) # request com o link de redirecionamento contido na div
        if(referral_html.status_code != 200): # se status_code não for 200, houve algum erro
            print(f"\nErro, não consegui acessar o link direto de uma das notícias da página: {i}\n")
            return ''
        referral_soup = BeautifulSoup(referral_html.text, "html5lib") # acessa o html do link de redirecionamento para obter o link direto
        direct_link = referral_soup.find(self.soup_tags[2], attrs={self.tag_attrs[2]:self.attr_values[2]}).get("content").strip("0;URL='") # link direto para a notícia
        return direct_link    


    def get_news_blocks(self, i:int, tag):
        try:
            a = tag.find('ul', attrs={'class':'resultado_da_busca unstyled'}).findAll(self.soup_tags[0])
            return a
        except Exception:
            return None

    def get_date(self, soup) -> date:
        try:
            date = datetime.strptime(soup.find('div', attrs={'class':'article__date'}).text.strip('\n').split('\n')[0], "%d/%m/%Y - %H:%M").date()
            return date  
        except Exception:
            return None
    
    def scrape_paragraphs(self, tag):
        if(tag == None): 
            return None
        paragraphs = tag.find(self.soup_tags[5], attrs={self.tag_attrs[5]:self.attr_values[5]})
        if(paragraphs == None):
            return None 
        return paragraphs.findAll(self.soup_tags[3])
        


class Folha_Scraper(News_Scraper):
    def __init__(self, assunto:str, pages:int):
        self.editoriais_full = ['online/opiniao', 'online/pensata', 'online/paineldoleitor', 'online/dinheiro', 'online/cotidiano',
        'online/mundo', 'online/esporte', 'online/ilustrada', 'online/ilustrissima', 'online/ambiente', 'online/ciencia', 'online/comida',
        'online/educacao', 'online/equilibrio', 'online/saopaulo', 'online/informatica', 'online/turismo']
        self.editoriais_used = ['online/opiniao', 'online/paineldoleitor', 'online/dinheiro', 'online/cotidiano',
        'online/mundo', 'online/esporte', 'online/ilustrada', 'online/ilustrissima', 'online/ambiente', 'online/ciencia', 'online/comida',
        'online/educacao', 'online/equilibrio', 'online/saopaulo', 'online/informatica', 'online/turismo']
        self.news_vehicle = "Folha de São Paulo"
        self.max_pages = 10000000
        super().__init__(assunto, pages)
        self.news_site = 'https://search.folha.uol.com.br/search'
        self.soup_tags = ['div', 'a', 'div', 'p', 'h1']
        self.tag_attrs = ['class', '', 'class', '', 'class']
        self.attr_values = ['c-headline__content', '', 'c-news__body', '', 'c-content-head__title']
        self.keys = ['q', 'periodo', 'site', 'sort', 'site[]', 'sr']
        self.key_dict = dict([('q', assunto),('periodo', 'todos'),('site', 'sitefolha'), ('sort', 'desc'), ('site[]', self.editoriais_used), ('sr', '1')])

    def set_editoriais(self, reset = False):
        return

    def prepare_pages(self, i: int):
        self.key_dict['sr'] = str( ( (i - 1) * 25) + 1)
        try:
            req = requests.get(self.news_site, params=self.key_dict, verify=False)
            print(f'\n{req.url}\n')
            return req # request para cada busca
        except Exception as e:
            print(f"exception: = {e}")
            return None
            
            

    def set_periodo(self, simpleperiod = '', reset = False, fromperiod = '', toperiod = ''):
        if reset == True:
            self.key_dict['periodo'] = 'todos'
            return
        if(simpleperiod in ["todos", "24", "semana", "mes", "ano"]):
            self.key_dict["periodo"] = simpleperiod
        if 'sd' in self.key_dict:
            del self.key_dict['sd']
        if 'ed' in self.key_dict:
            del self.key_dict['ed']
        elif fromperiod != '' and toperiod != '':
            self.key_dict['periodo'] = 'personalizado'
            self.key_dict['sd'] = fromperiod 
            self.key_dict['ed'] = toperiod
        
        

    def get_direct_link(self, tag, i : int) -> str:
        direct_link = tag.find(self.soup_tags[1])
        if(direct_link == None): 
            print(f"\nErro, não consegui acessar o link direto de uma das notícias da página: {i}\n")
            return ''
        direct_link = direct_link.get('href')
        return direct_link
    
    def get_date(self, soup) -> date:
        try:
            date = datetime.fromisoformat(soup.find('time', attrs={'class':'c-more-options__published-date'}).get("datetime")).date()
            return date  
        except Exception:
            return None

    def scrape_paragraphs(self, tag):
        if(tag == None): 
            return None
        paragraphs = tag.find(self.soup_tags[2], attrs={self.tag_attrs[2]:self.attr_values[2]})
        if(paragraphs == None):
            return None 
        return paragraphs.findAll(self.soup_tags[3]) # obtenção das tags html com os parágrafos



def headln(): 
    print('-=' * 30 + '-')


headln()
print(f"{'Web scraper para notícias':^60}")
headln()

assunto = input("\nInsira o assunto a ser pesquisado no veículo de notícias: ")
print("\nAgora, escolha uma das opções de veículos de notícia abaixo: ")
option = int(input("1 - G1;\n2 - Gazeta do Povo;\n3 - Época;\n4 - Folha de São Paulo;\n5 - G1 e Folha;"))
while(option < 1 or option > 5):
    option = int(input("Opção inválida! Insira um número de 1 a 4: "))
print("\nAguarde, irei começar a procurar os links das notícias.\n")

lista = []
scraper = None
if(option == 1):
    scraper = G1_Scraper(assunto, 1)
    scraper.set_order('recent')
    #scraper.set_periodo(simpleperiod='now-1M')
    #scraper.set_periodo(fromperiod = "2020-03-19", toperiod = "2020-04-19")
elif(option == 2):
    scraper = Gazeta_Scraper(assunto, 30)
elif(option == 3):
    scraper = Epoca_Scraper(assunto, 40)
elif(option == 4):
    scraper = Folha_Scraper(assunto, 250)    
    #scraper.set_periodo(simpleperiod='todos')
    scraper.set_periodo(fromperiod='01/01/2018', toperiod='04/06/2020')
else:
    lista = [G1_Scraper(assunto, 40), Folha_Scraper(assunto, 250)]
    lista[0].set_order('recent')
    lista[1].set_periodo(simpleperiod='todos')
    
if len(lista) == 0:
    scraper.scrape_links()
#option = input("\nTodos os links foram capturados. Recomenda-se que você salve-os em disco antes do processo de coleta de notícias.\nVocê deseja salvar os links em disco? Se sim, escreva 's'. ")
#if(option == 's'):
    string_list_to_txt(scraper.assunto+'_'+scraper.news_vehicle, "links", scraper.link_list)
    scraper.scrape_news()

    scraper.createDF()
else:
    for i in lista:
        i.scrape()
        i.createDF()


#scraper = G1_Scraper(assunto, 40)

#scraper2 = Gazeta_Scraper(assunto, 30)

#scraper3 = Epoca_Scraper(assunto, 40)

#scraper4 = Folha_Scraper(assunto, 100)    

#scraper.scrape_links()
#string_list_to_txt(scraper.assunto+'_'+scraper.news_vehicle, "links", scraper.link_list)
#scraper.scrape_news()
#scraper.createDF()

#scraper2.scrape_links()
#string_list_to_txt(scraper2.assunto+'_'+scraper2.news_vehicle, "links", scraper2.link_list)
#scraper2.scrape_news()
#scraper2.createDF()

#scraper3.scrape_links()
#string_list_to_txt(scraper3.assunto+'_'+scraper3.news_vehicle, "links", scraper3.link_list)
#scraper3.scrape_news()
#scraper3.createDF()

#scraper4.scrape_links()
#string_list_to_txt(scraper4.assunto+'_'+scraper4.news_vehicle, "links", scraper4.link_list)
#scraper4.scrape_news()
#scraper4.createDF()

