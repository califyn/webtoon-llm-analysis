from sklearn.decomposition import PCA
from sklearn.manifold import SpectralEmbedding
from sklearn.manifold import MDS

from scipy.spatial import KDTree

import numpy as np
from glob import glob
import matplotlib.pyplot as plt

'''
    cluster.py:
        Generates plots for embeddings of each webtoon episode and performs data analyses.

        Dimensionality reduction algorithm options (provided by scikit-learn):
            'pca': Principal Component Analysis
            'spectral': Spectral Embedding
            'mds': Multidimensional scaling
'''

EP_NUMBER = 10
DIMENSIONALITY_REDUCTION = 'pca'
SIZE = 'small'

data = []
titles = []
genres = []
for toon in glob("*/"):
    data.append([])
    if SIZE == 'small':
        srch = "*/embedding.txt"
    elif SIZE == 'large':
        srch = "*/embedding_lg.txt"

    for embed in glob(toon + srch):
        with open(embed, "r") as f:
            x = f.read().split("\n")
            if len(x) == 1 and x[0] == '':
                continue
            arr = np.array([float(y) for y in x])
        data[-1].append(arr)
    if len(data[-1]) != EP_NUMBER:
        data = data[:-1]
    else:
        titles.append(toon[:-1])
        with open(toon + "info.txt") as f:
            x = f.read().split("\n")[1]
            genres.append(x[x.index("\t") + 1:])

data = np.array(data)
num_toons = len(titles)

data_mean = np.mean(data, axis=1)
data_mean = data_mean / np.sqrt(np.sum(np.square(data_mean), axis=1, keepdims=True)) # normalize
dists = -1 * np.sum(np.expand_dims(data_mean, 1) * np.expand_dims(data_mean, 0), axis=2) # calculate cosine distance
originality = "\n".join([str(x) for x in sorted(zip(np.mean(np.sort(dists, axis=1)[:, :5], axis=1), titles))])
dists = np.argsort(dists, axis=-1) # get indices
recs = list(map(lambda x: [titles[y] for y in x], dists.tolist()))

if SIZE == "small":
    lg_str = ""
elif SIZE == "large":
    lg_str = "_lg"
with open("recommendations" + lg_str + ".tsv", "w") as f:
    f.write("Webtoon\tMost to Least Similar" + ("\t" * (num_toons - 2)) + "\n")
    f.write("\n".join(["\t".join(rec) for rec in recs]))
with open("originality" + lg_str + ".tsv", "w") as f:
    f.write("Most Alike\n")
    f.write(originality + "\n")
    f.write("Least Alike")

data = np.reshape(data, (num_toons*EP_NUMBER,-1))
data = data / np.sqrt(np.sum(np.square(data), axis=1, keepdims=True)) # normalize since we use cosine dist

if DIMENSIONALITY_REDUCTION == 'pca':
    transformer = PCA(n_components=2, random_state=0)
    transformer.fit(data)
    data = transformer.transform(data)
elif DIMENSIONALITY_REDUCTION == 'spectral':
    transformer = SpectralEmbedding(n_components=2)
    data = transformer.fit_transform(data)
elif DIMENSIONALITY_REDUCTION == 'mds':
    transformer = MDS(n_components=2)
    data = transformer.fit_transform(data)

data = np.reshape(data, (num_toons, EP_NUMBER, -1))
data = np.mean(data, axis=1)

all_genres = sorted(list(set(genres)))
genre_lgd = [False] * len(all_genres)

for idx, toon in enumerate(titles):
    genre_idx = all_genres.index(genres[idx])
    if genre_lgd[genre_idx]:
        plt.scatter(data[idx, 0], data[idx, 1], color=plt.cm.tab10(genre_idx))
    else:
        plt.scatter(data[idx, 0], data[idx, 1], label=genres[idx], color=plt.cm.tab10(genre_idx))
        genre_lgd[genre_idx] = True
    plt.annotate(toon.replace("_", " "), (data[idx, 0], data[idx, 1]))
plt.legend()
figure = plt.gcf() # get current figure
figure.set_size_inches(16, 12)
if SIZE == "small":
    plt.savefig('dimensionality_reduced.png')
elif SIZE == "large":
    plt.savefig('dimensionality_reduced_lg.png')
