import math

from collections import Counter

def calcu_entropy(name:str, n_gram:int=1):
    if len(name) < n_gram:
        return 0.0
    name = name.encode('utf-8')

    ngrams = [name[idx:idx+n_gram] for idx in range(len(name)-n_gram+1)]
    counts = Counter(ngrams)
    total = len(ngrams)

    entropy = 0.0
    for count in counts.values():
        prob = count / total
        entropy += prob * math.log2(1/prob)
        
    return entropy