#Fazendo o primeiro trabalho de Estrutura de Dados 1(que foi feito em C) em python.
#O trabalho consistia em fazer um programa que recebesse o nome/path de um arquivo .txt
#Nesse arquivo, espera-se encontrar nomes de outros arquivos .txt(existentes ou não)
#Os arquivos que existirem, serão lidos e terão seus dados armazenados na memória, e tais dados
#Serão concatenados e armazenados em um arquivo final 'fout.txt'.

#Função para printar uma "barrinha" de caracteres
def headln(): 
    print('-=' * 30 + '-')


headln()
print(f"{'Trabalho de ED1 em python':^60}")
headln()
arq = input('Insira o nome/caminho do arquivo de entrada: ')
fin = open(arq, 'r')
fout = open('fout.txt', 'w')
fout.close()
lista = fin.read().replace('\n', ' ').split() # lista com nomes dos arquivos a serem lidos
for strin in lista:
    try:
        with open(strin, 'r') as faux:
            fout = open('fout.txt', 'a')
            fout.write(faux.read())
            fout.close()
            faux.close()
    except FileNotFoundError:
        print(f"arquivo '{strin}' não existe")

fin.close()
