/*
	Este programa recebe 4 argumentos em tempo de lançamento, das 2 formas possíveis:
	-l file1 -o file2 ou -o file1 -l file2 (-l file = input, -o file = output)
	Se as informações forem recebidas corretamente o programa recebe o nome de arquivos presentes na input
	e realiza a junção destes arquivos no arquivo output.
                
	by Isaque dos Reis, Vinicius Calixto e Vitor Manoel Gonçalves Teixeira, 2018
*/

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<ctype.h>

//Constantes literais de erros:
#define ERR_FRNULL  	10
#define ERR_FWNULL  	20
#define ERR_ARGC    	31
#define ERR_ARGV1       41
#define ERR_ARGV2       42
#define ERR_ARGV3       43
#define ERR_MALC    	50
#define ERR_SIZEVET 	60
#define ERR_FSEEK   	70
#define ERR_NODIGIT 	80
#define FILE_BUFF       4096
#define FILE_NAME_BUFF  500

#define MAXTXT      30 //Tamanho máximo do nome de um arquivo

typedef struct
{
    char name[MAXTXT+1]; //tamanho máximo do nome de um arquivo
} FILE_NAMES;

typedef struct
{
    char *fileContent; //guarda, em um vetor de caracteres, o conteudo de um arquivo
}BUFFER;

int err_args(int argc, char *argv[]);

int err_fun(const int n,const char str[MAXTXT+1]);

BUFFER *getBuffer(int nFiles, FILE_NAMES f[]);

FILE_NAMES *getFileNames(const char finName[MAXTXT+1], int *nFiles);

void joinFiles(char foutName[MAXTXT+1], int lenBuff, BUFFER b[]);

int 
main(int argc,char *argv[])
{
	FILE *fi = NULL;				     //Ponteiro para o arquivo de entrada 
    FILE *fo = NULL;				     //Ponteiro para o arquivo de saída
	FILE_NAMES *files = NULL; 			 //Ponteiro que para estrutura com o nome dos arquivos
	BUFFER *buff = NULL; 				 //buffer que armazena temporariamente os dados dos arquivos
	char input[MAXTXT+1] = {'\0'};       //Arranjo auxiliar de fi
	char output[MAXTXT+1] = {'\0'};      //Arranjo auxiliar de fo
	char str[MAXTXT+1] = {'\0'}; 	     //Arranjo que pode ser modificado em funções para ser usado na err_fun
	int aux = 0;						 //Variável que recebe o retorno das funções
	int nFiles = 0;						 //Variável que guarda o numero de arquivos

    if((aux = err_args(argc,argv))!=0)
        return err_fun(aux, input);

    if((strcmp(argv[1], "-l")==0)&&(strcmp(argv[3], "-o")==0)){
        strcpy(input, argv[2]);
	    strcpy(output, argv[4]);
    }
    else{
        strcpy(input, argv[4]);
	    strcpy(output, argv[2]);
    }			   

	fi = fopen(input,"r");
	fo = fopen(output,"w");

	if(fi == NULL)
        return err_fun(ERR_FRNULL,input);
	if(fo == NULL)
		return err_fun(ERR_FWNULL,output);
	
    files = getFileNames(input, &nFiles);  //recebe o nome dos arquivos contidos em fin
    buff = getBuffer(nFiles, files);       //armazena o conteudo dos arquivos no BUFFER
    joinFiles(output, nFiles, buff);       //escreve no arquivo fout

	fclose(fi);
	fclose(fo);
	free(files);
	free(buff);
	return 0;
}

/*
    Essa função recebe o argc e o argv da main, e verifica se a quantidade, ordem e
    tipo de argumentos inseridos foi adequada. Por exemplo, se a quantidade estiver correta,
    mas nenhuma das tags("-o" e "-l") for inserida, a função retornará o código desse erro,
    encontrado na lista de defines de constantes literais.

*/
int 
err_args (int argc, char *argv[])
{
    if (argc>5)
        return ERR_ARGC;
    else if (argc<5)
        return ERR_ARGC;
    else if ((strcmp(argv[1],"-o")==0)&&(strcmp(argv[3],"-l")!=0))
        return ERR_ARGV1;
    else if ((strcmp(argv[1],"-l")==0)&&(strcmp(argv[3],"-o")!=0))
        return ERR_ARGV1;
    else if ((strcmp(argv[1],"-l")!=0)&&(strcmp(argv[1],"-o")!=0)&&(strcmp(argv[3],"-l")!=0)&&(strcmp(argv[3],"-o")!=0)){
        if ((strcmp(argv[2],"-l")!=0)&&(strcmp(argv[2],"-o")!=0)&&(strcmp(argv[4],"-l")!=0)&&(strcmp(argv[4],"-o")!=0))
            return ERR_ARGV2;
        else return ERR_ARGV3;
    }
    else return 0;
}

/*
	função que imprime em stderr erros possíveis do programa
 
	argumento const int n -> constante literal que representa algum erro 
	saída = inteiro -> main -> script

*/
int 
err_fun (const int n,const char str[MAXTXT+1])
{
	if(n == ERR_FRNULL)
	{
	   fprintf(stderr,"Erro de leitura no arquivo %s!\n",str);
       fprintf(stderr,"Arquivo inexistente ou inacessível!\n");
	   return 1;
	}
	else if(n == ERR_FWNULL)
	{
	   fprintf(stderr,"Erro de escrita no arquivo %s!\n",str);
		return 2;
	}
	else if(n == ERR_ARGC)
	{
		fprintf(stderr,"Erro! 4 argumentos devem ser inseridos!\n");
		return 3;
	}
    else if(n == ERR_ARGV1)
	{
		fprintf(stderr,"Erro! A ordem dos argumentos está incorreta!\n");
		return 3;
	}
    else if(n == ERR_ARGV2)
	{
		fprintf(stderr,"Erro! Nenhuma tag conhecida inserida!\n");
		return 3;
	}
    else if(n == ERR_ARGV3)
	{
		fprintf(stderr,"Erro! Uma ou mais tags inseridas incorretamente!\n");
		return 3;
	}
	else if(n == ERR_MALC)
	{
		fprintf(stderr,"Erro ao fazer alocação dinâmica de memória!\n");
		return 4;
	}
	else if(n == ERR_SIZEVET)
	{
		fprintf(stderr,"Quantidade de elementos devem ser maior que 0!\n");
		return 5;
	}
	else if(n == ERR_FSEEK)
	{
		fprintf(stderr,"Erro,a posição do elemento deve ser maior que 0!\n");
		return 6;
	}
	else if(n == ERR_NODIGIT)
	{
		fprintf(stderr,"Erro! o %sº argumento passado em tempo de lançamento deve ser um digito\n",str);
		return 7;
	}
	else
	{
		fprintf(stderr,"Erro desconhecido!\n");
		return 10;
	}
}

                                 


/**
* Esta função carrega um ponteiro para a estrutura BUFFER, alocado
* dinamicamente para suportar nFiles, que representa o numero de 
* arquivos presente no arquivo de entrada, indicados pelo array
* da estrutura FILE_NAMES. 
* Um um ponteiro-de-ponteiro FILE é criado para armazenar os nFiles
* presentes no array da estrutura FILE_NAMES. Este é alocado dinâmi-
* camente, para suportar os nFiles que serão carregados no buffer.
* Por fim, para cada elemento buff, ela realiza a alocação dinâmica 
* do ponteiro fileContent presente na estrutura BUFFER, para que este 
* armazene o conteúdo do arquivo que está sendo realizada a leitura.
*	
*   int nFiles -> numeroDeArquivos presentes em FILE_NAMES
*   FILE_NAMES f[] -> Array da estrutura FILE_NAME, que armazena o 
*   nome de cada arquivo presente no fin.txt
*
*	return BUFFER buff -> estrutura que armazena temporariamente o 
*   conteudo dos nFiles indicados por FILE_NAMES.
*------------------------------------------------------------------------------------------------
* 
*                                  ESCRITA NO ARQUIVO FOUT
*
*         LEITURA DOS NOMES         |           ARMAZENAMENTO TEMPORÁRIO DOS DADOS DOS ARQUIVOS                                
*         DOS ARQUIVOS              |           E ESCRITA DEFINITIVA.
*                                   | 
*                                   |
*                                   |
*               struct FILE_NAMES   |                            struct BUFFER
*                  +------------+   | "r"                        +------------+     "a"                 
*               |->|FILE_NAME[0]| --|fopen---char *fileContent-->|BUFF[0]     | ---------|
*               |->|FILE_NAME[1]| --|fopen---char *fileContent-->|BUFF[1]     | ---------|
*               |->|FILE_NAME[2]| --|fopen---char *fileContent-->|BUFF[2]     | ---------|
*               |  | ...        | --|fopen---char *fileContent-->| ...        | ---------|
*               |  +------------+   |                            +------------+          v
*  +---------+  |                   |                                               +---------+
*  |a.txt    |--|                   |                                               |file1    |
*  |b.txt    |--|                   |                                               |\n       |
*  |c.txt    |--|                   |                                               |file2    |        
*  | ...     |--|                   |                                               |\n       |
*  |z.txt    |--|                   |                                               |...      |
*  +---------+                      |                                               +---------+
*  fin.txt                          |                                                fout.txt
*                                   |
*                                   | 
*/ 
BUFFER 
*getBuffer(int nFiles, FILE_NAMES f[])
{
    char ch = 0;                //armazena um caractere temporariamente
    int i = 0;                  //iterador que percorre os arquivos e o buffer
    int j = 0;                  //iterador que percorre a string fileContent

    FILE **files = NULL;        //ponteiro para o array de arquivos
    BUFFER *buff = NULL;        //ponteiro para o buffer dos arquivos

    int buffsize = FILE_BUFF;   //taxa de crescimento do conteudo do arquivo

    files = (FILE**) calloc(nFiles, sizeof(FILE*)); 
    if(files == NULL)
        exit(err_fun(ERR_MALC, NULL));

    /*inicializa os arquivos*/
    for(int i = 0; i < nFiles; i++)
    {
        files[i] = fopen(f[i].name, "r");
        if(files[i] == NULL)
            exit(err_fun(ERR_FRNULL, f[i].name));
    }// for

    buff = (BUFFER*) calloc(nFiles, sizeof(BUFFER));
    if(buff == NULL)
        exit(err_fun(ERR_MALC, NULL));

    while(i < nFiles)
    {
        buff[i].fileContent = (char*) calloc(buffsize, sizeof(char));
        if(buff[i].fileContent == NULL)
       		exit(err_fun(ERR_MALC, NULL));

        int j = 0;
        while(fscanf(files[i], "%c", &ch) != EOF)
        {  
            if(j >= buffsize)
            {
                buffsize += FILE_BUFF;
                buff[i].fileContent = realloc(buff[i].fileContent, buffsize * sizeof(char));
                if(buff[i].fileContent == NULL)
					exit(err_fun(ERR_MALC, NULL));
            }   
            buff[i].fileContent[j] = ch;
            j++;
        }// while
        buff[i].fileContent[j] = '\0';
            // printf("%s\n", buff[i].fileContent);
        fclose(files[i]);
        i++;
    }

    return buff;   
}

/**
* Esta função realiza a leitura de um arquivo, que contem strings
* representando o nome de arquivos que serão usados posteriormente.
* Ela le sequencialmente as strings de cada linha do arquivo, e as
* armazena no array da estrutura FILE_NAMES;
* Por fim, ela passa para o ponteiro nFiles, o numero efetivo de 
* nome de arquivos lidos e fecha o arquivo.
*
*   char finName[] -> nome do arquivo de entrada, com o nome dos 
*   arquivos a serem manipulados pela funcao joinFiles.
*   int *nFiles -> ponteiro que armazena o numero de arquivos lidos
*   efetivamente do arquvo finName.
*
*	return FILE_NAMES files -> estrutura que armaazena o nome dos 
*   arquivos contidos em finName.
*
* 
*/
FILE_NAMES 
*getFileNames(const char finName[MAXTXT+1], int *nFiles)
{
    int i = 0;                      //contador de iterações
    FILE_NAMES *files = NULL;       //estrutura que armazena o nome dos arquivos
    FILE *f = NULL;                 //ponteiro para o arquivo finName
    int buffsize = FILE_NAME_BUFF;  //taxa de crescimento do vetor files

    f = fopen(finName, "r");
    if(f == NULL)
        exit(err_fun(ERR_FRNULL, finName));

    files = (FILE_NAMES*) calloc(buffsize, sizeof(FILE_NAMES));
    if(files == NULL)
   		exit(err_fun(ERR_MALC, NULL));

    while(fscanf(f, "%s", &files[i].name) != EOF)
    {
        if(i >= buffsize)
        {
            buffsize += FILE_NAME_BUFF;
            files = realloc(files, buffsize * sizeof(FILE_NAMES));
            if(files == NULL)
               exit(err_fun(ERR_MALC, NULL));
        }// if
        i++;
    }// while
    *nFiles = i;
    fclose(f);
    return files;
}

/**
*	Escreve no arquivo fout o conteudo de todos os arquivos, que
*   estão armazenados no BUFFER.
*
*   char foutnName[] -> nome do arquivo de saida, que será escrito
*   no modo "a"(append).
*   int lenBuff -> numero de arquivos armazenado no BUFFER
*   BUFFER b[] -> array da estrutura BUFFER, contendo os dados de
*   todos os arquivos que serão escritos
*
*	return void
*
* 
*/
void 
joinFiles(char foutName[MAXTXT+1], int lenBuff, BUFFER b[])
{
    FILE *f = fopen(foutName, "a");
    if(f == NULL)
       exit(err_fun(ERR_FRNULL, foutName));

    for(int i = 0; i < lenBuff; i++)
        fprintf(f, "%s\n", b[i].fileContent);

    fclose(f);
    return;
}
