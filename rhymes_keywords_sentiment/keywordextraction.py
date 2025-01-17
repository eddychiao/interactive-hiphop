from collections import OrderedDict
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.tokenizer import Tokenizer
from abc import ABC, abstractmethod
import time

t = time.time()
# If this errors, run "python -m spacy download en_core_web_md"
nlp = spacy.load("en_core_web_md")
print(time.time() - t)

class KeywordExtractor:
    """Wrapper class for extracting keywords from text"""
    def __init__(self, model="textrank"):
        self.model = None
        if model == "textrank":
            self.model = TextRank()

    def set_stopwords(self, stopwords):
        self.model.set_stopwords(stopwords)
    
    def analyze(self, text):
        self.model.analyze(text)

    def get_keywords(self, num=5):
        return self.model.get_keywords(num)


class KeywordModel(ABC):
    @abstractmethod
    def set_stopwords(self, stopwords):
        """Set the appropriate stop words for the model"""
        pass

    @abstractmethod
    def analyze(self):
        """Run algorithm on text"""
        pass

    @abstractmethod
    def get_keywords(self, num_keywords):
        """Return the top `num_keywords` keywords"""
        pass

class TextRank(KeywordModel):
    """
    Source: https://towardsdatascience.com/textrank-for-keyword-extraction-by-python-c0bae21bcec0
    """
    def __init__(self):
        self.d = 0.85 # damping coefficient, usually is .85
        self.min_diff = 1e-5 # convergence threshold
        self.steps = 10 # iteration steps
        self.node_weight = None # save keywords and its weight
        self.text_raw = None

    def set_stopwords(self, stopwords):  
        """Set stop words"""
        for word in STOP_WORDS.union(set(stopwords)):
            lexeme = nlp.vocab[word]
            lexeme.is_stop = True
    
    def sentence_segment(self, doc, candidate_pos, lower):
        """Store those words only in cadidate_pos"""
        sentences = []
        for sent in doc.sents:
            selected_words = []
            for token in sent:
                # Store words only with cadidate POS tag
                if token.pos_ in candidate_pos and token.is_stop is False:
                    if lower is True:
                        selected_words.append(token.text.lower())
                    else:
                        selected_words.append(token.text)
            sentences.append(selected_words)
        return sentences
        
    def get_vocab(self, sentences):
        """Get all tokens"""
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab
    
    def get_token_pairs(self, window_size, sentences):
        """Build token_pairs from windows in sentences"""
        token_pairs = list()
        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(i+1, i+window_size):
                    if j >= len(sentence):
                        break
                    pair = (word, sentence[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs
        
    def symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())
    
    def get_matrix(self, vocab, token_pairs):
        """Get normalized matrix"""
        # Build matrix
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')
        for word1, word2 in token_pairs:
            i, j = vocab[word1], vocab[word2]
            g[i][j] = 1
            
        # Get Symmeric matrix
        g = self.symmetrize(g)
        
        # Normalize matrix by column
        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm!=0) # this is ignore the 0 element in norm
        
        return g_norm

    
    def get_keywords(self, number=10):
        """Get top number keywords"""
        node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
        res = []
        for i, (key, value) in enumerate(node_weight.items()):
            # print(key + ' - ' + str(value))
            res.append(key)
            if i > number:
                break
        return res
        
        
    def analyze(self, text, 
                candidate_pos=['NOUN', 'PROPN', 'VERB', 'ADJ', "ADV"], 
                window_size=4, lower=False, stopwords=list()):
        """Main function to analyze text"""
        
        # Set stop words
        self.set_stopwords(stopwords)
        
        # Pare text by spaCy
        if not self.text_raw:
            self.text_raw = text
        else:
            self.text_raw += " " + text
        doc = nlp(self.text_raw)
        
        # Filter sentences
        sentences = self.sentence_segment(doc, candidate_pos, lower) # list of list of words
        
        # Build vocabulary
        vocab = self.get_vocab(sentences)
        
        # Get token_pairs from windows
        token_pairs = self.get_token_pairs(window_size, sentences)
        
        # Get normalized matrix
        g = self.get_matrix(vocab, token_pairs)
        
        # Initionlization for weight(pagerank value)
        pr = np.array([1] * len(vocab))
        
        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1-self.d) + self.d * np.dot(g, pr)
            if abs(previous_pr - sum(pr))  < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weight = dict()
        for word, index in vocab.items():
            node_weight[word] = pr[index]
        
        self.node_weight = node_weight
    
if __name__ == "__main__":
    song_lyrics = None
    with open("noneshallpass.txt") as f:
        song_lyrics = f.read().lower()
    km = KeywordExtractor(model="textrank")

    extra_stop_words = ["n't", "'s", "'m", "``", "'", '"', '.', ",", "ai", "'re", "'ll"]
    km.set_stopwords(extra_stop_words)

    km.analyze(song_lyrics)
    print("Keywords for verse:")
    print(km.get_keywords(10))

    km2 = KeywordExtractor(model="textrank")
    km2.set_stopwords(extra_stop_words)

    s1 = "This is a test of the model."
    km2.analyze(s1)
    print("Keywords for '{0}':".format(s1))
    print(km2.get_keywords(5))

    s2 = "This is also a test of the keyword model, but with new words."
    km2.analyze(s2)
    print("Keywords for '{0}':".format(s2))
    print(km2.get_keywords(5))

    s3 = open("./microphone_fiend.txt", 'r').read().lower()
    km3 = KeywordExtractor(model="textrank")
    km3.set_stopwords(extra_stop_words)
    km3.analyze(s3)
    print("Keywords for Microphone Fiend by Rakim:")
    print(km3.get_keywords(10))

    s4 = open("./redefinition_mosdef.txt", 'r').read().lower()
    km4 = KeywordExtractor(model="textrank")
    km4.set_stopwords(extra_stop_words)
    km4.analyze(s4)
    print("Keywords for Mos Def's verse on Re:Definition:")
    print(km4.get_keywords(10))
