__author__ = 'jp'

import wikipedia  # access Wikipedia
from nltk.corpus import wordnet as wn  # get list of nouns
from time import time  # performance metrics
import subprocess  # excecute system functions

# t = time()
# try:
#     s = wikipedia.summary('book')
#     print s
#     subprocess.call(['espeak', s])
# except wikipedia.exceptions.DisambiguationError as e:
#     print e.options
# except wikipedia.exceptions.PageError as e:
#     print e
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

from googleapiclient import discovery

api_key = "AIzaSyBjcxQoEC4KhtdHxFUcdFo0uCLEUm_1EoI"
cx = "002450837493438996748:mg1lpmyfubw"

service = discovery.build("customsearch", "v1",
               developerKey=api_key)

res = service.cse().list(
    q='butterfly',
    cx=cx,
    searchType='image',
    num=3,
    imgType='clipart',
    fileType='png',
    safe='off'
).execute()

if not 'items' in res:
    print 'No result !!\nres is: {}'.format(res)
else:
    for item in res['items']:
        print('{}:\n\t{}'.format(item['title'], item['link']))