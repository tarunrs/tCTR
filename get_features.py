import sys
import pickle
from tokenizer import Tokenizer
from collections import defaultdict
from sentiwordnet import SentiWordNetCorpusReader
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

toker = Tokenizer(preserve_case=True)
SWN_FILENAME = "SentiWordNet_3.0.0_20130122.txt"
swn = SentiWordNetCorpusReader(SWN_FILENAME)
ps = PorterStemmer()
lmtzr = WordNetLemmatizer()

def capitalize_nouns(t):
  if t[1][0] == "N":
    return (t[0].capitalize(), t[1])
  return (t[0],t[1])

def delete_from_list(l, to_delete):
  for i, el in enumerate(l):
    if el in to_delete:
      del l[i]

def sanitize_for_nltk(tweet, preserve_case=False):
  # First we lower case. Tokenize. Remove links hashtags and mentions. Then do POS tagging. Then we capitalize Nouns and return a list of tokens
  #s = tweet.text.lower()
  toks = toker.tokenize(tweet.text)
  delete_from_list(toks, tweet.p_user_mentions + tweet.p_hashtags + tweet.p_urls)
  toks = [t.lower() for t in toks]
  if toks[-1] == "by":
    del toks[-1]
  p = nltk.pos_tag(toks)
  toks = map(capitalize_nouns, p) 
  setattr(tweet, 'p_sanitized_tokens', list(zip(*toks)[0]))

def get_named_entities(s):
  p = nltk.pos_tag(s)
  ne_chunks = nltk.ne_chunk(p, binary=True)
  nes = [n for n in ne_chunks if hasattr(n, "node")]
  named_entities = []
  for ne in nes:
    leaves = ne.leaves()
    ws = " ".join(zip(*leaves)[0])
    named_entities.append(ws)
  return named_entities

def add_named_entities(tweet):
  sanitize_for_nltk(tweet)
  setattr(tweet, 'p_named_entities', get_named_entities(tweet.p_sanitized_tokens))

def add_bow(tweet):
  words = tweet.p_sanitized_tokens
  filtered_words = [w.lower() for w in words if not w.lower() in stopwords.words('english')]
  stemmed_words = [ps.stem(w.lower()) for w in words]
  stemmed_filtered_words = [ps.stem(w.lower()) for w in filtered_words]
  lemma_words = [lmtzr.lemmatize(w.lower()) for w in words]
  setattr(tweet, 'p_filtered_tokens', filtered_words)
  setattr(tweet, 'p_stemmed_tokens', stemmed_words)
  setattr(tweet, 'p_stemmed_filtered_tokens', stemmed_filtered_words)
  setattr(tweet, 'p_lemma_tokens', lemma_words)

def get_sentiment_score(w):
  sets = swn.senti_synsets(w)
  if len(sets) > 0 and sets[0]:
    scores = sets[0]
    return scores.pos_score, scores.neg_score, scores.obj_score
  else:
    wn_syn = wn.synsets(w)
    if len(wn_syn) > 0:
      sets = swn.senti_synsets(wn_syn[0].name.split(".")[0])      
      if len(sets) > 0 and sets[0] :
        scores = sets[0]
        return scores.pos_score, scores.neg_score, scores.obj_score
  return 0.0, 0.0, 0.0
    
def add_sentiment_scores(tweet):
  words = tweet.p_sanitized_tokens
  scores = []
  for w in words:
    pos_score, neg_score, obj_score = get_sentiment_score(w)
    scores.append((pos_score, neg_score, obj_score))
  setattr(tweet, 'p_sentiment_scores', scores)
  setattr(tweet, 'p_senti_word_count', len(scores))

def add_pos_tags(tweet):
  p = nltk.pos_tag(tweet.p_sanitized_tokens)
  tags = list(zip(*p)[1])
  pos_tags = defaultdict(int)
  for tag in tags:
    pos_tags[tag] += 1
  setattr(tweet, 'p_pos_tags', pos_tags)
  
def add_features(tweet):
  add_named_entities(tweet)
  add_bow(tweet)
  add_sentiment_scores(tweet)
  add_pos_tags(tweet)

def dump_features(ifname, ofname):
  tweets = pickle.load(open(ifname))
  for i, t in enumerate(tweets):
    if hasattr(t, 'p_ctr'):
      add_features(t)
    if i % 500 == 0:
      print i
  pickle.dump(tweets, open(ofname, "w"))


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Enter a Username"
  else:
    user_id = sys.argv[1] 
    print "Starting processing for:", user_id
    ifname = user_id + "/ctr_data/tweets.pkl"
    #ifname = user_id + "/feature_data/tweets.pkl"
    ofname = user_id + "/feature_data/tweets.pkl"
    dump_features(ifname, ofname)
    
