# Webtoon semantic analysis

I whipped this up over a weekend to test out [Cohere](https://docs.cohere.ai)'s platform and to also see if romance webcomics are *really* all the same. I like reading webcomics so why not use LLMs to analyze them, plus I've read a *lot* of these webtoons so this is a neat exercise in convincing myself that LLMs actually work, even if they tend to do so in very high-dimensional and obscure ways.

## How it works

In the final analysis, I kept 48 popular webcomics scraped off of the [Webtoons](https://www.webtoons.com/en/) platform with Selenium Wire. Each webcomic had its first 10 episodes OCR'd with Tesseract, cleaned minimally, and then embedded in 4096 dimensions with Cohere's API and averaged out to form one high-dim embedding for each webcomic.

## Results

### Does it work?

Kind of... For such a visual medium, a surprising amount can be gleaned from just the text. There's one noticeable exception: the horror webtoon [Everything is Fine](https://www.webtoons.com/en/horror/everything-is-fine/list?title_no=2578), which uses mostly visual irony and subtly strange conversation to achieve its effect, is horribly misclassified as... romance?

In case it's not clear, this is what I mean by visual irony:

![Panel: "What a nice day" while looking out at pouring rain.](./everything_is_fine.png)

To be fair to the LLM, there are no other horror webtoons, so it might've been forced to classify it with romance, but still... The misclassification appears to be a little less egregious on the [large model](./dimensionality_reduction_lg.png) than the [small model](./dimensionality_reduction.png). Scale is all you need?

If I were to actually do this, I'd definitely use a multimodal method. But for today I'm just interested in slapping an LLM on it and calling it a day.

### What does it tell us?

Here's the embeddings of each of the 48 webtoons with PCA, colored by genre:

![PCA result of large model's embeddings](./dimensionality_reduction_lg.png)

If I had to guess, the two significant axes are left-to-right romance to action and top-down native English to translated English (many more translated Korean webcomics are at the bottom.) A lot of the fantasy webtoons in the middle have a lot of romance in them.

Now to answer the pivotal questions, are romance webtoons really all the same? Take a look at [originality.tsv](../originality.tsv), which scores each webcomic based off the average cosine distance to its five closest neighbors. The most ``unique" with this metric is UnOrdinary, which makes sense as it's a pretty unique comic. Interestingly enough, almost all the ones I like and read are near the bottom, so I guess I'm a novelty seeker. It's surprising that the LLM can glean this much from a shoddily put together script on my side and I think it's really cool.

On the other hand, the least unique webtoons are pretty much all romance. So if you feel that romance is all the same, here's some definitive evidence for that.

### Can we make it a recommendation engine?

Since clearly I only want to read webtoons similar to the ones I already like, we can make these embeddings into a recommendation engine via employing nearest neighbors. The recommendations generated can be found in [recommendations_lg.tsv](../recommendations_lg.tsv).  They're overall pretty good, I'd say; for example, *Suitor Armor* is one of the recommendations for *Like Wind on a Dry Branch* and I definitely think these go together. On the other hand, the recommendations for *Everything is Fine* is just horrible, as expected.

### Thoughts on the Cohere API

It was very easy to use, which I really like. As promised, you can pretty much plug and play. On the other hand, it seemed a bit unwieldy to customize at all, or to ask the model to look for things in particular rather than just embedding (it would have been fun to try to ask it to rate quality, for example.) Perhaps that'd be possible with a generative model.
