import subprocess
from glob import glob
from enchant.checker import SpellChecker
from tqdm import tqdm

'''
    tess.py:
        Use Tesseract to convert webtoon panels to text.
        Also, delete some gibberish lines.
'''

def is_in_english(quote): # code source: https://stackoverflow.com/questions/3788870/how-to-check-if-a-word-is-an-english-word-with-python
    d = SpellChecker("en_US")
    d.set_text(quote)
    errors = [err.word for err in d]
    return False if ((len(errors) > 1) or (len(quote.split()) - len(errors)) < 3) else True

for ep in glob("*/ep-*/"):
    print(ep)
    all_text = {}
    for img in tqdm(glob(ep + "imgs/obj-*.*")):
        path = img[:img.rindex("/") + 1]
        num = int(img[img.rindex("-") + 1:img.rindex(".")])

        subprocess.run(["tesseract", img, path + "text-" + str(num)], stderr=subprocess.DEVNULL) # run tesseract

        with open(path + "text-" + str(num) + ".txt", "r") as f:
            text = f.read()

        text = text.replace("\n\n", "\n\t") # use tab character to preserve double newlines, which are usually new speech bubbles
        text = text.split("\n")
        text = [l for l in text if is_in_english(l)] # delete low-quality lines
        text = " ".join(text)
        text = text.replace("\t", "\n")

        all_text[num] = text

    with open(ep + "all_text.txt", "w") as f:
        f.write("\n".join([all_text[i] for i in sorted(all_text) if len(all_text[i]) > 0])) # join it all together into a coherent script
