# -*- coding: utf-8 -*-
"""
@author: Dario Peralta
"""
#%%
import numpy as np
import pandas as pd
#%%
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
#
from sklearn.cluster import KMeans
#%%
from prep import helpers
#%%
def get_tfidf(corpus, ngram_range=(1,2)):
	# tf-idf params
	max_df = 1.0
	min_df = 1
	norm = 'l2'
	vectorizer = TfidfVectorizer(max_df=1.0,
									 min_df=1, stop_words=None,
									 tokenizer=helpers.tokenize_and_stem,
									 ngram_range=ngram_range,
									 use_idf=True,
									 norm=norm)
	return (vectorizer.fit_transform(corpus), vectorizer)
#%%
def get_clusters(X, 
				k_choices=[k for k in range(20, 55, 5)],
				dim_choices=[d for d in range(20, 55, 5)]):
	scores = np.ones((len(dim_choices), len(k_choices))) * -1
	variances = np.zeros(len(dim_choices))
	best_score = -1
	best_model = None
	np.random.seed(42)
	for d, dims in enumerate(dim_choices):
		# reduce dimensionality (LSA)
		svd = TruncatedSVD(dims)
		normalizer = Normalizer(copy=False)
		lsa = make_pipeline(svd, normalizer)
		#
		X_t = lsa.fit_transform(X)
		#
		explained_variance = svd.explained_variance_ratio_.sum()
		print("Varianza explicada con {} dimensiones: {}%".format(
			dims, int(explained_variance * 100)))
		variances[d] = explained_variance
		for c, k in enumerate(k_choices):
			# helpers
			km = KMeans(n_clusters=k,
						init='k-means++',
						max_iter=500,
						n_init=5, 
						n_jobs=-1)
			km.fit(X_t)
			#
			scores[d, c] = metrics.silhouette_score(X, km.labels_, sample_size=1000)
			print("Metrica de calidad del clustering con {} dimensiones y {} clusters: {:.4f}".format(
					dims, k,
					scores[d, c]))
			if scores[d, c] > best_score:
				best_score = scores[d, c]
				best_model = (lsa, km, dims, k)
	#
	return best_model
#%%
def cluster_descriptions(model, base, terms, n_words=5):
	centroids = base.inverse_transform(model.cluster_centers_)
	ordered = centroids.argsort()[:,::-1]
	descriptions = []
	for i in range(centroids.shape[0]):
		descriptions.append(', '.join(terms[t] for t in ordered[i, :n_words]))
	return descriptions
#%%
def add_cluster_descriptions(df, best_model, vectorizer):
	#
	df['cluster_id'] = best_model[1].labels_
	#
	#%%
	cluster_descs = cluster_descriptions(best_model[1],
										 best_model[0].steps[0][1],
										 vectorizer.get_feature_names())
	cluster_descs = pd.DataFrame(data=cluster_descs)
	cluster_descs.rename(columns={0:'cluster_description'}, 
						 inplace=True)
	cluster_descs.index.names = ['cluster_id']
	#%%
	df = pd.merge(left=df, 
					  right=cluster_descs,
					  how='left',
					  left_on=['cluster_id'],
					  right_index=True)
	return df