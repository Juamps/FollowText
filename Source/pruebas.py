__author__ = 'jp'

import wikipedia  # access Wikipedia
from nltk.corpus import wordnet as wn  # get list of nouns
from time import time  # performance metrics
import subprocess  # excecute system functions

t = time()
try:
    s = wikipedia.summary('book')
    print s
    subprocess.call(['espeak', s])
except wikipedia.exceptions.DisambiguationError as e:
    print e.options
except wikipedia.exceptions.PageError as e:
    print e
# t = time() - t
# print s
# print "Time elapsed:", t
#
# print "[+] Creating list of nouns"
# t = time()
# ## Make a list of nouns in wordnet
# nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
# print "[+] Done!"
# # print "cook" in nouns
# t = time() - t
# print "Time elapsed:", t