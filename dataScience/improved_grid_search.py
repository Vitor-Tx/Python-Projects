import pandas as pd
import sys
import io
import time
import numpy as np
from datetime import datetime
import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.model_selection import cross_val_predict
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.base import clone
import glob
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier, PassiveAggressiveClassifier, Perceptron
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import pathlib

def get_pipe_list(algs):
    """
        Função que tem o propósito de gerar uma lista de pipelines com vários algoritmos e parâmetros diferentes.
    """
    pipelist = []
    
    for j in range(0, len(algs)):
        pipelist.append(Pipeline([('vect', HashingVectorizer(analyzer="word", stop_words = set(stopwords.words('portuguese') + list(punctuation)))),
        ('tfidf', TfidfTransformer()), 
        ('clf', clone(algs[j])),]))
    return pipelist

def get_true_false(lista):
    zipped = [[sum(item) for item in zip(items)] for items in zip(*lista)]
    TList = []
    FList = []
    for i in range(0, len(lista)):
        ipred = sum(zipped[i])
        Tpred = lista[i][i]
        TList.append(Tpred) 
        FList.append(ipred - Tpred)
    return TList + FList


#Obtendo o path do diretório atual
path = str(pathlib.Path().absolute()) 

#Planilhas para treinos e testes
train_np = pd.read_csv(path+'\\Planilhas\\train_test\\train_np.csv')
test_np = pd.read_csv(path+'\\Planilhas\\train_test\\test_np.csv')
train_neutral = pd.read_csv(path+'\\Planilhas\\train_test\\train_neutral.csv')
test_neutral = pd.read_csv(path+'\\Planilhas\\train_test\\test_neutral.csv')

df_list =[[train_np, test_np], [train_neutral, test_neutral]]
testes = ["sem notícias neutras balanceado", "com notícias neutras balanceado"]
paramList = ['n-gram(1,1)', 'n-gram(1,2)']
algoList = ['Decision Tree']

#criando lista de pipelines
#params = {'n-grams': [(1,1), (1,2)]}
#pipelist = get_pipe_list([MultinomialNB(), SGDClassifier(), Perceptron(), DecisionTreeClassifier(), PassiveAggressiveClassifier(), RandomForestClassifier()])
pipelist = [Pipeline([('vect', CountVectorizer(analyzer="word", stop_words = set(stopwords.words('portuguese') + list(punctuation)))),
        ('tfidf', TfidfTransformer()), 
        ('clf', DecisionTreeClassifier())])]
#dicionário com parâmetros dos componentes do pipeline antes do algoritmo em si
param_dict = {'vect__ngram_range': [(1, 1), (1, 2)],
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),}

#Lista com dicionários com parâmetros para os algoritmos
parameter_list = [{'clf__max_depth': (15, 35),
                   'clf__min_samples_split': (75, 125),
                   'clf__min_samples_leaf': (25, 35),
                   'clf__max_features': (0.5, 'sqrt'),
                   'clf__criterion': ('gini', 'entropy'),
}]

cmp = pd.DataFrame(columns = ["Algoritmo", "Parâmetros", "Parâmetros testados", "Melhores parâmetos", "Tipo", "Acurácia", "Duração Treino", "Duração Teste", "FN", "FP", "FNT", "TN", "TP", "TNT", "Precisão", "F1", "Recall", "N_treino", "N_teste"])
dic_list = []

for i in range(0, 1):

    #Preparando as listas com notícias e classificações para treino e teste
    
    train_news = df_list[i][0]
    train_classif = train_news["Modelo"]
    train_news = train_news["Notícia"]
    test_news = df_list[i][1]
    test_classif = test_news["Modelo"]
    test_news = test_news["Notícia"]
    if("Neutro" in train_classif):
        lista = ['Negativo', 'Neutro', 'Positivo']
    else:
        lista = ['Negativo', 'Positivo']
    n_treino = len(train_news)
    
    for j in range(0, len(pipelist)):
        params = dict(**param_dict, **parameter_list[0])
        randomS = RandomizedSearchCV(pipelist[j], params, cv=3, n_jobs=10, pre_dispatch=8, n_iter=10) #objeto para Randomized search
        time_train = time.time() #verificando o tempo decorrido durante os treinos
        randomS.fit(train_news, train_classif) #treinando o algoritmo
        time_train = time.time() - time_train
        print(time_train)
        time_test = time.time() #verificando o tempo decorrido durante os testes
        predicted = randomS.predict(test_news) #testando o algoritmo
        time_test = time.time() - time_test
        print(time_test)
        
        cm = metrics.confusion_matrix(np.asarray(test_classif), predicted, labels = lista)
        
        if('Neutro' not in lista):
            tn, fp, fn, tp  = cm.ravel()
            tnt, fnt = ['N/A', 'N/A']
        else: tn, tnt, tp, fn, fnt, fp  = get_true_false(cm)
        #relatório de classificação(com precisão, acurácia, f1, recall e etc do teste do algoritmo)
        cr = metrics.classification_report(np.asarray(test_classif), predicted, target_names=lista, zero_division=1, output_dict=True)
        #transferindo os dados do teste para um dicionário
        dic = {"Algoritmo" : algoList[j],
                  "Parâmetros testados" : "\n".join([j for j in sorted(params.keys())]),
                  "Melhores parâmetros" : "\n".join(["%s: %r" % (param_name, randomS.best_params_[param_name]) for param_name in sorted(params.keys())]),
                  "Tipo" : testes[i],
                  "Acurácia" : randomS.score(test_news, test_classif),
                  "Duração Treino" : time_train,
                  "Duração Teste" : time_test,
                  "FN" : fn,
                  "FNT" : fnt, 
                  "FP" : fp, 
                  "TN" : tn, 
                  "TNT" : tnt, 
                  "TP" : tp, 
                  "Precisão" : cr["macro avg"]["precision"], 
                  "F1" : cr["macro avg"]["f1-score"], 
                  "Recall" : cr["macro avg"]["recall"], 
                  "N_treino" : n_treino, 
                  "N_teste" : cr["macro avg"]["support"]}

        print(f"A acurácia do teste {testes[i]} utilizando o algoritmo {algoList[j]} é de: ")
        print(dic["Acurácia"])
        print(f"\nO treinamento e teste demoraram {time_train + time_test} segundos.\n")
        print("-------------------------------- Testes padronizados ---------------------")
        print("Best parameters set found on development set:")
        print()
        print(randomS.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = randomS.cv_results_['mean_test_score']
        stds = randomS.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, randomS.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                % (mean, std * 2, params))
        print()

        print("Detailed classification report:")
        print()
        print("The model is trained on the full development set.")
        print("The scores are computed on the full evaluation set.")
        print()
        print(classification_report(test_classif, predicted))
        print()

        dic_list.append(dic)

#Um dataframe é feito utilizando-se a lista de dicionários
cmp = pd.DataFrame(dic_list, columns = ["Algoritmo", "Parâmetros testados", "Melhores parâmetros", "Tipo", "Acurácia", "Duração Treino","Duração Teste",  "FN", "FNT", "FP", "TN", "TNT", "TP", "Precisão", "F1", "Recall", "N_treino", "N_teste"])



