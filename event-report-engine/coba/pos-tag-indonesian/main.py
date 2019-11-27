from nltk.tokenize import word_tokenize
import pickle

file = open('indonesian_ngram_pos_tag.pickle', 'rb')
ngram_tagger = pickle.load(file)
file.close()
 
kalimat = '[PHYSICSDAY] Ayo Masyarakat Fisika berdiri dan bersuaralah untuk mendukung futsal fisika. Senin, 18 Maret 2019 19.30 Gor Pertamina ITS Blackwolf/Hitam (Kerudung Hitam) : 5k'


print("N-gram tagger")
print(ngram_tagger.tag(word_tokenize(kalimat)))

file = open('indonesian_tnt_pos_tag.pickle', 'rb')
tnt_tagger = pickle.load(file)
file.close()

print('\nTnT tagger')
print(tnt_tagger.tag(word_tokenize(kalimat)))

file = open('indonesian_classifier_pos_tag.pickle', 'rb')
classifier_tagger = pickle.load(file)
file.close()

print('\nClassifier tagger')
print(classifier_tagger.tag(word_tokenize(kalimat)))
