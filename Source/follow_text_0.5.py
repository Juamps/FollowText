__author__ = 'jp'
import wikipedia # access Wikipedia
import sys  # read user input
import nltk  # word database
from nltk.corpus import wordnet as wn  # get list of nouns
from time import sleep, time  # performance metrics
import codecs  # handle utf8 characters
import datetime  # for timestamp
import random  # select random stuff
from Flickr_connector import Flickr_connector  # manage Flickr info
from urllib import urlretrieve  # download Flickr image
from urllib2 import urlopen, HTTPError  # check image permissions
from PIL import Image  # resize image
from AppKit import NSSpeechSynthesizer
from Cocoa import NSURL  # create NSURL format to save audio file
import requests  # query google api
import json  # interpret google api answer

### GLOBAL VARIABLES
MAX_CRAWL = 5
WORDS = []
SENTENCES = []
NOUNS = []
WORD_FILENAME = "words"
SENTENCE_FILENAME = "sentences"
CONT = 0
WIKI_LANGUAGE = 'es'  # # 'es' for Spanish, 'en' for English, 'de' for German
KEYS = {} # keys for flickr and google APIs
IMG_SIZE = "xxlarge"  # # options are 'icon', 'small', 'medium', 'large', 'xlarge', 'xxlarge', 'huge'

# TTS variables
RATE = 200    # Value in words per minute; human speed 180-220
VOLUME = 0.5  # Floating point value in the range of 0.0 to 1.0 inclusive.
VOICE = "com.apple.speech.synthesis.voice.juan.premium"  # String identifier of the active voice.
              ### RUN showcase_voices.py TO SEE ALL AVAILABLE VOICES IN YOUR SYSTEM ###


def list_nouns():

    global NOUNS
    print "[+] Creating list of nouns... (This only has to be done once)"

    if WIKI_LANGUAGE == 'en':
        ## Make list of nouns from wordnet
        NOUNS = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
        ## TODO CREATE A SEPARATE LIST FOR NOUNS ENDING IN S
    elif WIKI_LANGUAGE == 'es':
        ## Make list of nouns from cess_esp
        list = nltk.corpus.cess_esp.tagged_words()
        sust = []
        for elem in list:
            if elem[1][0] == 'n':
                sust.append(elem[0])
        NOUNS = set(sust)
    # TODO german language support
    # elif WIKI_LANGUAGE == 'de':
    else:
        print "[!] Language not recognised, using English."
        ## Make list of nouns from wordnet
        NOUNS = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}


    print "    Done!"


def next_word(pos=1):
    '''
    :param pos:
    :return: returns the [pos] noun before the first period/stop [.]
    '''
    global WORDS, NOUNS, SENTENCES, MAX_CRAWL
    ans = None
    cont = 1
    nouns_found = 0
    sentence = SENTENCES[-1]
    words = sentence.split(' ')
    while not ans and cont + 1 < len(words):
        ## select last word in sentence
        noun = words[-cont]
        ## remove periods, commas and plural forms ending in s from word
        right_punctuation = ['.', ',', ')', ']', '}', '\'', 's', '\'', '\"']
        left_punctuation = ['(', '[', '{', '\'', '\"']

        for element in right_punctuation:
            noun = noun.rstrip(element)
        for element in left_punctuation:
            noun = noun.lstrip(element)
        # noun = noun.rstrip('.')
        # noun = noun.rstrip(',')
        # noun = noun.rstrip(')')
        # noun = noun.rstrip('\'')
        # noun = noun.lstrip('\'')
        ## TODO CHECK FOR NOUNS ENDING IN S
        noun = noun.lower()
        noun = noun.rstrip('s')

        ## check if word is noun
        if noun in NOUNS:
            if len(noun) > 1:
                if noun not in WORDS:
                    nouns_found += 1
                    ## return word only if 'pos - 1' new nouns have been found before
                    if nouns_found == pos:
                        ans = noun
                else:
                    print "[!] Word '", noun, "' already in list"
                    print "    Skipping..."
        cont += 1
    return ans


def validate_seed(seed):
    valid = False
    try:
        print seed
        wikipedia.summary(seed)
        valid = True
    except wikipedia.exceptions.PageError as e:
        print "[!] Error:", e
    except wikipedia.exceptions.DisambiguationError as e:
        valid = True
        # print e.options
    except wikipedia.exceptions.ConnectionError as e:
        print "[!] Error:", e
        print "    Check your Internet connection and try again."
    if valid:
        print "[+] Valid seed."
    return valid


def disambiguate(word, e):
    try:
        ## Print all suggestions
        # for option in e.options:
        #     print option

        # Choose a suggestion that explicitly has the word in it.
        # suggestion = next(sug for sug in e.options if word.lower() in sug.lower())

        ## Choose suggestion at random
        suggestion = random.choice(e.options)
    except StopIteration:
        ## If none, choose first suggestion
        suggestion = e.options[0]

    try:
        # print "Trying to use " + suggestion
        ## Fetch new summary
        summary = wikipedia.summary(suggestion)
        print "[!] Ambiguous term, using:", suggestion
        # print e.options
        return summary
    except wikipedia.exceptions.DisambiguationError as err:
        # print err.options
        return disambiguate(suggestion, err)
    except wikipedia.exceptions.PageError as err:
        print err.message
        return disambiguate(suggestion, e)


def add_word(word):
    print "[+] Current search:", word, "  [", CONT + 1, "/", MAX_CRAWL, "]"
    try:
        ## Fetch sentence
        summary = wikipedia.summary(word)
    except wikipedia.exceptions.PageError as e:
        print e.message
        if len(WORDS) == 0:
            print "[!]"
    except wikipedia.exceptions.DisambiguationError as e:
        summary = disambiguate(word, e)

    summary_split = summary.split('.')
    ## Clean summary
    for elem in range(0, len(summary_split)):
        summary_split[elem] = summary_split[elem].strip()
    ## Keep first sentence and remove from summary
    sentence = summary_split[0]
    # if len(summary_split) > 1 and summary_split[1] != '':
    #     summary_split = summary_split[1:]
    #     ## Check if the first period does not end the sentence
    #     ## Look at next sentence and if it doesn't start with a capital letter, append.
    #     next_sentence = summary_split[0].lstrip()[0].strip()
    #     while len(next_sentence) == 0 or (next_sentence.islower() and len(summary_split)) > 1:
    #         sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()
    #         summary_split = summary_split[1:]
    #         next_sentence = summary_split[0].lstrip()[0].strip()
    #     if summary_split[0].lstrip()[0].islower():
    #         sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()

    if len(summary_split) > 1 and summary_split[1] != '':
        summary_split = summary_split[1:]
        ## Check if the first period does not end the sentence
        ## Look at next sentence and if it doesn't start with a capital letter, append.
        next_sentence = summary_split[0].strip()
        # print summary_split
        ## Check if length of next split is 1 => likely it is an acronym
        if len(next_sentence) == 1:
            while len(next_sentence) == 1 and len(summary_split) > 1:
                sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()
                summary_split = summary_split[1:]
                next_sentence = summary_split[0].strip()
            print next_sentence
            ## Add the next sentence after the acronym
            if len(next_sentence) > 1:
                sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()
        ## If not, check if it's some sort of abbreviation
        else:
            ## Sentences after periods would only be lower case if previous was abbreviation
            next_sentence = summary_split[0].lstrip()[0].strip()
            while next_sentence.islower() and len(summary_split) > 1 and summary_split[1] != '':
                sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()
                summary_split = summary_split[1:]
                next_sentence = summary_split[0].lstrip()[0].strip()
            if summary_split[0].lstrip()[0].islower():
                sentence = sentence.rstrip() + '. ' + summary_split[0].lstrip()

    ## Add final point to sentence
    sentence = sentence.rstrip() + '.'
    ## Append term and sentence
    WORDS.append(word)
    SENTENCES.append(sentence)
    print "    Sentence fetched:"
    print "    " + SENTENCES[-1]
    print "\n"

    ## Download image for word
    fetch_image(word)

    ## Speak word
    tts_NS(word)


def write_to_file():
    global WORDS, SENTENCES, WORD_FILENAME, SENTENCE_FILENAME

    ## Add timestaps to file names
    timestamp = datetime.datetime.now().isoformat().split('.')[0]
    wf = "../Output/" + sys.argv[1] + "_" + str(CONT) + "_words_" + timestamp + ".txt"
    sf = "../Output/" + sys.argv[1] + "_" + str(CONT) + "_summary_" + timestamp + ".txt"
    tf = "../Output/" + sys.argv[1] + "_" + str(CONT) + "_speech_" + timestamp + ".mp3"
    with codecs.open(wf, 'wb', "utf-8") as f:
        for word in WORDS:
            f.write(word + '\n')

    with codecs.open(sf, 'wb', "utf-8") as f:
        for sentence in SENTENCES:
            f.write(sentence + " ")


def with_flickr(word):
    fc = Flickr_connector('../keys.txt')
    photo_url = fc.fetch_photo(word)
    return photo_url


def with_google(word):
    key = KEYS["google_key"]
    cx = KEYS["google_engine_id"]
    startIndex = '1'
    searchTerm = word
    searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
        searchTerm + "&start=" + startIndex + "&key=" + key + "&cx=" + cx + \
        "&searchType=image" + "&imgType=photo" + "&imgSize=" + IMG_SIZE

    r = requests.get(searchUrl)

    response = r.content.decode('utf-8')
    result = json.loads(response)
    # print(searchUrl)
    # print(r)

    ## get all results
    all_results = result['items']

    ## get results urls
    urls = []
    for res in all_results:
        url = str(res['link'])
        ## only add jpegs
        if url.split('.')[-1] == 'jpg':
            urls.append(str(res['link']))

    # for url in urls:
    #     print url

    downloadable = None
    to_remove = []
    while downloadable is None:
        for i in range(len(urls)):
            try:
                urlopen(urls[i])
                downloadable = True
            except HTTPError:
                to_remove.append(i)
    # remove if not accessible
    for element in to_remove:
        del urls[element]

    return random.choice(urls)

def resize_image(filepath):
    im = Image.open(filepath)
    width, height = im.size

    #if landscape, width 1920px; if portrait height 1080px
    if width > height:
        ## scale width to 1920px
        ## suppose width=w, scale=x;  w*x = 1920 => x = 1920/w
        scale = 1920 / float(width)
    else:
        ## scale height to 1080px
        scale = 1080 / float(height)
    ## resize
    w = int(width*scale)
    h = int(height*scale)
    resized_im = im.resize((w, h), Image.ANTIALIAS)
    ## save resized
    resized_im.save(filepath)

def fetch_image(word):
    print "[+] Fetching image... "

    ## Using Flickr
    photo_url_Flickr = with_flickr(word)
    filetype = photo_url_Flickr.split('.')[-1]
    filepath_Flickr = "../Images/Flickr/" + str(len(WORDS)) + "_" + word + "." + filetype

    ## Using Google Search
    photo_url_Google = with_google(word)
    filetype = photo_url_Google.split('.')[-1]
    filepath_Google = "../Images/Google/" + str(len(WORDS)) + "_" + word + "." + filetype

    ## download images
    urlretrieve(photo_url_Flickr, filepath_Flickr)
    urlretrieve(photo_url_Google, filepath_Google)

    ## resize images
    resize_image(filepath_Flickr)
    resize_image(filepath_Google)


    print "    Done!"


def tts_NS(word):
    ## Initialise voice synthesizer
    # synth = [[NSSpeechSynthesizer alloc] initWithVoice:nil];
    synth = NSSpeechSynthesizer.alloc().initWithVoice_(None)

    ## Set voice values
    synth.setVoice_(VOICE)
    synth.setVolume_(VOLUME)
    synth.setRate_(RATE)

    ## Create NSURL path
    filepath = "../Audio/" + str(len(WORDS)) + "_" + word + "_NS.aiff"
    url = NSURL.fileURLWithPath_(filepath)

    ## Save sythesized word
    synth.startSpeakingString_toURL_(word, url)


def read_keys(filepath):
    with open(filepath, "rb") as f:
        lines = f.readlines()
    for line in lines:
        l = line.split(',')
        KEYS[l[0].strip()] = l[1].strip()


def main():
    global MAX_CRAWL, CONT
    ## Set search language
    wikipedia.set_lang(WIKI_LANGUAGE)
    t = time()
    # Validate function call
    if len(sys.argv) != 3:
        print "[!] Function must be called with exactly two (2) parameters." \
              "\n    Usage: follow_text_0.2.py seed word_count "
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
        read_keys('../keys.txt')
        if validate_seed(word):
            list_nouns()
            CONT = 0
            print "[+] Initialising crawl."
            while CONT < MAX_CRAWL:
                # pos = 1
                add_word(word)
                ## Choose next word
                word = next_word()
                # word = next_word(pos)
                if not word:
                    print "[*] There are no more nouns to follow. Exiting..."
                    break
                CONT += 1
    except Exception as e:
        print "[!] Unexpected error", sys.exc_info()[0]
        print "   ", e
    finally:
        # print "Words fetched:", WORDS
        # for s in SENTENCES:
        #     print s
        #     print "\n"

        #write info to file
        write_to_file()
        t = time() - t
        print "Time elapsed:", t


if __name__ == '__main__':
    main()