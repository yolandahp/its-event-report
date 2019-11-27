import string
import re
import html
import urllib.request
import json
import os
import pickle

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def clean_text_classification(text):
    text = text.lower()
    
    text = re.sub(r'@[A-Za-z0-9]+', ' ', text)
    text = re.sub(r'#[A-Za-z0-9]+', ' ', text)
    text = re.sub(r'\w+:\/\/\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    
    text = re.sub(r' +', ' ', text)
    
    return ' '.join(text.split())

def clean_text_pos(text):
    text = html.unescape(text)
    text = re.sub(r'#[A-Za-z0-9]+', ' ', text)
    text = re.sub(r'\w+:\/\/\S+', ' ', text)
    
    text = re.sub(r' +', ' ', text)
    text = os.linesep.join([s for s in text.splitlines() if s])
    text = ', '.join(text.split('\n'))
    
    return text

def replace_slang(text):
    with open("extra/akronim.json", "r") as f:    
        acronym = json.load(f)
    
    res = []
    
    for w in text.split(' '):
        if w in acronym:
            res.append(acronym[w])
        else:
            res.append(w)
    
    return ' '.join(res)

def stemming(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    
    stem_text = stemmer.stem(text)
    
    return stem_text

def clean_proc_pos(text):
    text = clean_text_pos(text)
    text = replace_slang(text)

    return text

def clean_proc_clf(text):
    text = clean_text_classification(text)
    text = replace_slang(text)

    text = stemming(text)

    return text

if __name__ == "__main__":
    text = 'Bakor Pemandu ITS mengundang Pemandu Aktif ITS untuk duduk bareng ngobrolin LKMM TD pada:\n\n📆 Selasa - Rabu, 20-21 Feruari\n2018\n🕛 18.00 - 21.30 WIB\n📍 SCC Lt. 3\n👔 Standar Kuliah\n\n"Raise your standards to create change!" - An Iota of Truth\n\n#OborBakor\n#BAKORITS\n#ITSSurabaya https://t.co/v6oFZcWLFv'

    clean_text = clean_proc_pos(text)
    print(clean_text)

    clean_text = clean_proc_clf(text)
    print(clean_text)