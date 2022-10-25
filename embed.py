import cohere
from glob import glob
import time

'''
    embed.py:
        Use Cohere API to generate embeddings of text.
'''

SIZE = 'large'

with open("cohere_api_key.txt", "r") as f:
    co = cohere.Client(f.read()[:-1])

for toon in glob("*/ep-1/"):
    texts = []
    src = []
    for text in glob(toon[:-6] + "/*/all_text.txt"):
        with open(text, "r") as f:
            src.append(text)
            x = f.read()
            texts.append(x)

    pairs = [(texts[i], src[i]) for i in range(len(texts)) if len(texts[i]) > 0]
    texts = [a[0] for a in pairs]
    src = [a[1] for a in pairs]
    print(toon)
    time.sleep(2)
    response = co.embed(texts=texts, truncate='RIGHT', model=SIZE).embeddings

    for idx, (fe, text) in enumerate(zip(src, texts)):
        if SIZE == 'small':
            filename = fe[:fe.rindex("/") + 1] + "embedding.txt"
        elif SIZE == 'large':
            filename = fe[:fe.rindex("/") + 1] + "embedding_lg.txt"
        with open(filename, "w") as f:
            f.write("\n".join([str(x) for x in response[idx]]))
