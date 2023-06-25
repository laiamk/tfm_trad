import numpy as np
import pandas as pd
import os
import re
import copy
import itertools

def prepare_list(df: pd.DataFrame, column: str) -> pd.DataFrame:
    # Elimino los valores nulos y los duplicados
    df_aux = df[column].dropna().drop_duplicates().to_frame()
    # Miro la longitud de cada elemento
    df_aux['chars'] = df_aux[column].apply(lambda x: len(x))
    # Ordeno según la longitud de palabra en sentido descendente
    df_aux.sort_values('chars', ascending=False, inplace=True)
    return df_aux[column].to_list()


def read(path) -> [list, list]:
    """
    Read and clean the text specified in path
    :param path: Path to the text
    :returns: The cleaned text and the raw text, both in list format where each element is a phrase
    """
    with open(path, 'r', encoding='utf-8') as line:
    # Reads a specific line of text in the file. 
        raw_t = line.readlines()
    clean_t = clean_text(raw_t)
    return raw_t, clean_t


def clean_text(text: list) -> list:
    """Limpieza de un archivo leido como utf-8, elimina las lineas que marcan salto de parrafo y en cada linea
    elimina los caracteres especificados en la remove_list
    
    :param text: lista con el texto ya segmentado
    :returns: Cleaned text
    """
    # Elimina las lineas de salto de parrafo
    real_lines=[line for line in text if line!='<p>\n']
    # Elimina signos de puntuación
    real_text = [re.sub(r'[^\w\s]','',line)[:-1] for line in real_lines]
    # Asegura que cada palabra está separada por un único espacio
    real_text = [' '.join(re.findall('\S+',line)) for line in real_text]
    return real_text


def word_count(text: list, separator: str=' ') -> list:
    """
    Count the number of words in every element of the list

    :param text: list of strings
    :param separator: How to differenciate bewteen words
    :returns: The number of words in each element
    """
    return [len(line.split(separator)) for line in text]

def find_punctuation_in_list(raw_text: list, ls_characters: list, negative_matches: bool = False, verbose: bool=False):
    n_matches = []
    ls_text=[line for line in raw_text if line!='<p>\n']
    ls_text = [' '.join(re.findall('\S+',line)) for line in ls_text]
    for N in range(len(ls_text)):
        ls = [pattern for pattern in ls_characters if pattern in ls_text[N]]
        dic = {}
        aux = copy.deepcopy(ls_text[N])
        for pattern in ls:
            if len(pattern.split(' '))==1:
                dic[pattern] = aux.count(pattern)
            else:
                dic[pattern] = aux.count(pattern)
            aux=aux.replace(pattern,'')
        ls_final = [key for key,item in dic.items() if item>0]
        if negative_matches:
            n_words = len(ls_text[N].split(' '))
            print(dic)
            n_matches.append(n_words - np.sum([len(key.split(' '))*value for key,value in dic.items()]))
        else:
            n_matches.append(np.sum(list(dic.values())))
        if verbose:
            print(f'{N}: {ls} -> {ls_final} ({np.sum(list(dic.values()))})')
    # if count_matches:
    #     if inverted:
    #         number_ocurrences = [np.sum([char in phrase for char in ls_characters]) for phrase in ls_text]
    #     else:
    #         number_ocurrences = [np.sum([word in ls_characters for word in phrase.split(' ')]) for phrase in ls_text]
    # else:
    #     number_ocurrences = [np.sum([not word in ls_characters for word in phrase.split(' ')]) for phrase in ls_text]
    return n_matches

def find_char_in_list(ls_text: list, ls_characters: list, verbose: bool = False) -> list:
    """
    Generic function to find how many times a certain set of characters appears in each element (string) of a list.
    """
    n_matches = []
    for N in range(len(ls_text)):
        ls = [pattern for pattern in ls_characters if pattern in ls_text[N]]
        dic = {}
        aux = copy.deepcopy(ls_text[N])
        for pattern in ls:
            if len(pattern.split(' ')) == 1:
                # dic[pattern] = aux.count(pattern)
                dic[pattern] = np.sum([1 for i in ls_text[N].split(' ') if pattern == i],dtype=int)
            else:
                dic[pattern] = aux.count(pattern)
            aux = aux.replace(pattern,'')
        ls_final = [key for key,item in dic.items() if item>0]
        n_matches.append(np.sum(list(dic.values())))
        if verbose:
            print(f'{N}: {ls} -> {ls_final} ({np.sum(list(dic.values()))})')

    return n_matches


def simplificacion_1_1(ls_text: list, ls_non_content_words: list=None):
    """
    Simplificación 1.1 Calculations
    :param ls_text: the clean text
    :param ls_non_content_words: A list of non content words (and phrases)
    :returns: All the statistics for this part
    """
    #Join all str in the list
    total_text = ' '.join(ls_text)
    #Create a list of words
    total_text_list = total_text.split(' ')
    # dict.fromkeys eliminates duplicates. So we get the number of unique words
    unique_words = len(list(dict.fromkeys(total_text_list)))
    #Total number of words
    total_words = len(total_text_list)
    #Ratio of unique words
    unique_ratio = unique_words/total_words

    #List of ocurrences of content words
    number_non_content_words = find_char_in_list(ls_text, ls_non_content_words)

    #List of total word per phrase
    number_word_in_phrase = [len(phrase.split(' ')) for phrase in ls_text]
    #Ratio
    non_content_word_ratio_per_phrase = np.array(number_non_content_words)/np.array(number_word_in_phrase)
    non_content_word_ratio_per_phrase_average = np.mean(non_content_word_ratio_per_phrase)
    
    #Characters per word
    average_characters_per_word =[np.mean([len(word) for word in phrase.split(' ')]) for phrase in ls_text]
    total_average_characters_per_word = np.mean(average_characters_per_word)

    return (unique_words, total_words, unique_ratio, number_non_content_words, number_word_in_phrase, 
        non_content_word_ratio_per_phrase, non_content_word_ratio_per_phrase_average, average_characters_per_word, 
        total_average_characters_per_word)

def simplificacion_1_2(ls_text: list):
    number_word_in_phrase = [len(phrase.split(' ')) for phrase in ls_text]
    mean_number_phrases = np.mean(number_word_in_phrase)
    number_phrases = len(ls_text)
    return number_word_in_phrase, mean_number_phrases, number_phrases

def explicitacion_2_1(ls_text: list, ls_marcadores: list=None):
    number_marcadores_discursivos = find_char_in_list(ls_text,ls_marcadores)
    return number_marcadores_discursivos

def explicitacion_2_2(ls_text: list, ls_conjunciones: list=None):
    number_conjunciones = find_char_in_list(ls_text,ls_conjunciones)
    return number_conjunciones

def explicitacion_2_3(ls_text: list):
    rejoin = lambda x: ''.join(x)
    number_characters_per_phrase = [len(rejoin(phrase.split(' '))) for phrase in ls_text]
    total_text = ' '.join(ls_text)
    len_text = len(total_text)
    return number_characters_per_phrase, len_text

def explicitacion_2_4(ls_text: list, ls_pronombres: list=None):
    number_pronombres = find_char_in_list(ls_text,ls_pronombres)
    return number_pronombres

def final_statistics(dic: dict) -> dict:
    """
    Calculations of some extra statistics
    """
    dic['mean_pronombres'] = np.mean(dic['number_pronombres'])
    dic['pctg_pronombres'] = np.sum(dic['number_pronombres'])/np.sum(dic['number_word_in_phrase'])
    dic['mean_non_content_word'] = np.mean(dic['number_non_content_words'])

    dic['mean_conjunciones'] = np.mean(dic['number_conjunciones'])
    dic['pctg_conjunciones'] = np.sum(dic['number_conjunciones'])/np.sum(dic['number_word_in_phrase'])

    dic['mean_marcadores_discursivos'] = np.mean(dic['number_marcadores_discursivos'])
    dic['pctg_marcadores_discursivos'] = np.sum(dic['number_marcadores_discursivos'])/np.sum(dic['number_word_in_phrase'])
    
    dic['mean_punctuations'] = np.mean(dic['punctuations'])
    dic['pctg_punctuations'] = np.sum(dic['punctuations'])/np.sum(dic['number_word_in_phrase'])

    return dic

