__author__ = 'jp'
import wikipedia # access Wikipedia
import sys  # read user input
from nltk.corpus import wordnet as wn  # get list of nouns
from time import sleep, time  # performance metrics

MAX_CRAWL = 5
WORDS = []
SUMMARIES = []
NOUNS = []


def list_nouns():
    global NOUNS
    print "[+] Creating list of nouns... (This only has to be done once)"
    ## Make list of nouns in wordnet
    NOUNS = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
    print "    Done!"


def next_word(summary, pos):
    ans = None
    cont = 1
    nouns_found = 0
    words = summary.split(' ')
    while not ans and cont < len(words):
        if words[-cont] in NOUNS and len(words[-cont]) > 1:
            nouns_found += 1
            ## return word only if it is a non monosyllabic word and you have found 'pos - 1' nouns before
            if nouns_found == pos:
                ans = words[-cont]
        cont += 1
    return ans


def validate_seed(seed):
    valid = False
    suggestion = None
    try:
        wikipedia.summary(seed)
        valid = True
    except wikipedia.exceptions.PageError as e:
        print "[!] Error:", e
    except wikipedia.exceptions.DisambiguationError as e:
        valid = True
        # print e.options
    if valid:
        print "[+] Valid seed."
    return valid


def add_word(word):
    print "[+] Current search:", word, "  [", cont + 1, "/", MAX_CRAWL, "]"
    try:
        ## Fetch summary
        summary = wikipedia.summary(word)
    except wikipedia.exceptions.PageError as e:
        e.message
        if len(WORDS) == 0:
            print "[!]"

    except wikipedia.exceptions.DisambiguationError as e:
        suggestion = e.options[0]
        print "[!] Ambiguous term, using:", suggestion
        # print e.options
        summary = wikipedia.summary(suggestion)
    ## Append term and summary
    WORDS.append(word)
    SUMMARIES.append(summary)
    print "    Summary fetched."

if __name__ == '__main__':
    t = time()
    # Validate function call
    if len(sys.argv) != 2:
        print "[!] Function must be called with exactly one (1) parameter."
        print "    Exiting..."
        sleep(1)
    else:
        try:
            word = sys.argv[1]
            if validate_seed(word):
                list_nouns()
                cont = 0
                print "[+] Initialising crawl."
                while cont < MAX_CRAWL:
                    pos = 1
                    add_word(word)
                    ## Choose next word
                    word = next_word(SUMMARIES[-1], pos)
                    if not word:
                        break
                    cont += 1
                # print "cook" in nouns
                t = time() - t
                print "Time elapsed:", t
        except:
            print "[!] Unexpected error", sys.exc_info()[0]
        finally:
            print "Words fetched:", WORDS
            print "Summaries:", SUMMARIES