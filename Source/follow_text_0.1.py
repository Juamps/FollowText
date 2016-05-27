__author__ = 'jp'
import wikipedia # access Wikipedia
import sys  # read user input
from nltk.corpus import wordnet as wn  # get list of nouns
from time import sleep, time  # performance metrics
import codecs # handle utf8 characters


MAX_CRAWL = 5
WORDS = []
SUMMARIES = []
NOUNS = []
WORD_FILENAME = "words"
SUMMARY_FILENAME = "summaries"


def list_nouns():
    global NOUNS
    print "[+] Creating list of nouns... (This only has to be done once)"
    ## Make list of nouns in wordnet
    NOUNS = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
    print "    Done!"


def next_word(pos=1):
    global WORDS, NOUNS, SUMMARIES, MAX_CRAWL
    ans = None
    cont = 1
    nouns_found = 0
    summary = SUMMARIES[-1]
    words = summary.split(' ')
    while not ans and cont < len(words):
        ## select last word in summary
        noun = words[-cont]
        ## remove periods, commas and plural forms ending in s from string
        noun = noun.rstrip('.')
        noun = noun.rstrip(',')
        noun = noun.rstrip('\'')
        noun = noun.lstrip('\'')
        noun = noun.rstrip('s')

        ## check if word is noun
        if noun in NOUNS:
            if len(noun) > 1:
                if noun not in WORDS:
                    nouns_found += 1
                    ## return word only if it is a non monosyllabic word and you have found 'pos - 1' new nouns before
                    if nouns_found == pos:
                        ans = noun
                else:
                    print "[!] Word '", noun, "' already in list"
                    print "    Skipping..."
        cont += 1
    #crop summary if necessary
    if len(SUMMARIES) < MAX_CRAWL and cont > 2:
        summary = ' '.join(words[0:2-cont])
        SUMMARIES[-1] = summary
    return ans


def validate_seed(seed):
    valid = False
    try:
        wikipedia.summary(seed)
        valid = True
    except wikipedia.exceptions.PageError as e:
        print "[!] Error:", e
    except wikipedia.exceptions.DisambiguationError as e:
        valid = True
        # print e.options
    except wikipedia.exceptions.ConnectionError as e:
        print "[!] Error:", e
        print "    Check your Internet conneciton and try again."
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
        ## chose a suggestion that explicitly has the word in it. If none, choose first suggestion
        try:
            suggestion = next(sug for sug in e.options if word.lower() in sug.lower())
        except StopIteration:
            suggestion = e.options[0]

        print "[!] Ambiguous term, using:", suggestion
        # print e.options
        summary = wikipedia.summary(suggestion)
    ## Append term and summary

    WORDS.append(word)
    SUMMARIES.append(summary)
    print "    Summary fetched."
    print SUMMARIES[-1]
    print "\n"


def write_to_file():
    global WORDS, SUMMARIES, WORD_FILENAME, SUMMARY_FILENAME
    wf = "../Output/"+WORD_FILENAME
    sf = "../Output/"+SUMMARY_FILENAME
    with codecs.open(wf, 'wb', "utf-8") as f:
        for word in WORDS:
            f.write(word)

    with codecs.open(sf, 'wb', "utf-8") as f:
        for summary in SUMMARIES:
            f.write(summary)

if __name__ == '__main__':
    t = time()
    # Validate function call
    if len(sys.argv) != 3:
        print "[!] Function must be called with exactly two (2) parameters." \
              "\n    Usage: follow_text_0.1.py seed word_count "
        print "    Exiting..."
        exit(0)
    elif not isinstance(sys.argv[2], int):
        try:
            int(sys.argv[2])
        except ValueError:
            print "[!] Second argument must be an integer!"
            print "    Exiting..."
            exit(0)

    try:
        word = sys.argv[1]
        MAX_CRAWL = int(sys.argv[2])
        if validate_seed(word):
            list_nouns()
            cont = 0
            print "[+] Initialising crawl."
            while cont < MAX_CRAWL:
                # pos = 1
                add_word(word)
                ## Choose next word
                word = next_word()
                # word = next_word(pos)
                if not word:
                    break
                cont += 1
            # print "cook" in nouns
    except:
        print "[!] Unexpected error", sys.exc_info()[0]
    finally:
        # print "Words fetched:", WORDS
        # for s in SUMMARIES:
        #     print s
        #     print "\n"

        #write info to file
        write_to_file()
        t = time() - t
        print "Time elapsed:", t