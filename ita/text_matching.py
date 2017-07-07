from string import ascii_lowercase
import csv, re
from gensim import corpora, models, similarities
from operator import itemgetter

def readCSV(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        return [r for r in reader]

def row2str(r):
    m = re.search('\((.*?)\)(.*)', r[2])
    if m is not None:
        return '{} {} {}'.format(r[1], m.group(1), m.group(2))
        #return 'asset-{} control-{} {}'.format(r[1].replace(' ', '-'), m.group(1), m.group(2))
    else:
        return '{} {}'.format(r[1], r[2])

def str2words(s):
    # is, are, by, in?
    stoplist = set('a an of the and or to for on'.split())
    chars = []
    for c in s.lower():
        if c in ascii_lowercase:
            chars.append(c)
        else:
            chars.append(' ')
    s = ''.join(chars)
    return [word for word in s.split() if word not in stoplist]

def nGrams(s, n):
    if len(s) < n:
        return []
    else:
        return [' '.join(s[i:i+n]) for i in range(len(s) - n + 1)]


class Controls(object):
    def __add__(self, controls):
        res = Controls()
        res.rows = self.rows + controls.rows
        res.docs = self.docs + controls.docs
        res.wordlist = self.wordlist + controls.wordlist
        res.tokenslist = self.tokenslist + controls.tokenslist
        res.dictionary = corpora.Dictionary(res.tokenslist)
        res.corpus = [res.dictionary.doc2bow(tokens) for tokens in res.tokenslist]
        return res
    def readCSV(self, filename):
        self.rows = readCSV(filename)
        self.docs = [row2str(r) for r in self.rows if row2str(r) is not None]
        self.wordlist = [str2words(s) for s in self.docs]
        self.tokenslist = [nGrams(w, 2) + w for w in self.wordlist]
        self.dictionary = corpora.Dictionary(self.tokenslist)
        self.corpus = [self.dictionary.doc2bow(tokens) for tokens in self.tokenslist]
    def initLsi(self):
        self.model = models.LsiModel(self.corpus, id2word = self.dictionary, num_topics=100)
        self.index = similarities.Similarity('/tmp/gensim.lsi.index', self.model[self.corpus], num_features = 100)
    def initTfidf(self):
        self.model = models.TfidfModel(self.corpus, id2word=self.dictionary)
        self.index = similarities.Similarity('/tmp/gensim.tfidf.index', self.model[self.corpus], num_features = 2000)
    def getVec(self, tokens):
        return self.model[self.dictionary.doc2bow(tokens)]
    def getMatches(self, tokens):
        v = self.dictionary.doc2bow(tokens)
        sims = self.index[self.model[v]]
        return sorted(list(enumerate(sims)), key = itemgetter(1))
    def getAllMatches(self, tokenslist):
        return [self.getMatches(tokens)[-1] for tokens in tokenslist]

