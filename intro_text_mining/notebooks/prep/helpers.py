# -*- coding: utf-8 -*-
"""
@author: Dario Peralta
"""

import pandas as pd
import nltk
from nltk.collocations import BigramCollocationFinder
import re
import unicodedata

def cleanup_str(raw):
	rs = re.sub("\\(.*?\\)|[^a-zA-ZñÑ\\s]"," ",raw)
	rs = re.sub("\\s+"," ",rs).strip().lower()
	return rs

def normalize_description(raw):
	rs = cleanup_str(raw)
	return re.sub(r'\ba c\b','air conditioning',rs)

def remove_stopwords(text, language='English', stopwords=None):
	stopwords = stopwords or nltk.corpus.stopwords.words(language)
	tokens = nltk.word_tokenize(text)
	return ' '.join(w for w in tokens if not w in stopwords and len(w)>1)
	
def stem(desc, stemmer=None):
	stemmer = stemmer or nltk.PorterStemmer()
	return ' '.join(stemmer.stem(w) for w in nltk.word_tokenize(desc))

def tokenize_and_stem(text, stopwords=None,
					  stemmer=None,
					  language='English'):
	rs = normalize_description(text)
	rs = remove_stopwords(rs, language=language, stopwords=stopwords)
	rs = stem(rs, stemmer=stemmer)
	return rs.split()

def prepare_document(desc, language='English', stopwords=None, stemmer=None):
	rs = normalize_description(desc)
	rs = remove_stopwords(rs, language=language, stopwords=stopwords)
	rs = stem(rs, stemmer=stemmer)
	rs = set(nltk.word_tokenize(rs))
	rs = sorted(rs)
	return ' '.join(rs)

def get_tokens(corpus, language='English', stopwords=None):
	stopwords = stopwords or nltk.corpus.stopwords.words(language)
	return [w for d in corpus
			for w in d.split() if len(w) > 1 and w not in stopwords]

def get_bigrams(tokens, freq_filter = None):
	finder = BigramCollocationFinder.from_words(tokens)
	if freq_filter:
		finder.apply_freq_filter(freq_filter)
	return list(' '.join(b[0]) for b in finder.ngram_fd.items())

def get_vocab(corpus, language='English', stopwords=None):
	tokens = get_tokens(corpus, language=language, stopwords=stopwords)
	bigrams = get_bigrams(tokens, 2)
	return set(tokens + bigrams)

def get_mcc_data(mcc_fn = "../data/mcc_codes.csv"):
	stemmer = nltk.PorterStemmer()
	stopwords = nltk.corpus.stopwords.words('English')
	
	mcc_df = pd.read_csv(mcc_fn)
	mcc_df['clean_desc'] =  mcc_df.apply(
			lambda x: normalize_description(x.edited_description) 
			if type(x.irs_description) is float 
			else normalize_description(x.irs_description),
			axis=1)
	mcc_df['stem_desc'] = mcc_df.clean_desc.apply(stem, stemmer=stemmer)
	mcc_df['desc'] = mcc_df.apply(
			lambda x: prepare_document(x.edited_description, 
										stopwords = stopwords, 
										stemmer = stemmer) 
			if type(x.irs_description) is float 
			else prepare_document(x.irs_description, stopwords = stopwords, stemmer = stemmer),
			axis=1)
	return mcc_df