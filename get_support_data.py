import pickle
import sys
from collections import defaultdict

def add_to_dict(dic, tokens):
  for t in tokens:
    dic[t.lower()] += 1

def merge_dicts(dic_master, dic_slave):
  for k in dic_slave.keys():
    dic_master[k] += dic_slave[k]
    
def create_id_dict(dic, minthreshold, maxthreshold):
  ret_dict = dict()
  idx = 0
  for k in sorted(dic.keys()):
    if dic[k] > minthreshold and dic[k] < maxthreshold:
      ret_dict[k] = idx
      idx += 1
  return ret_dict

def dump(dic, fprefix, mint=1, maxt=3200):
  pickle.dump(dic, open(fprefix + ".c.pkl", "w"))
  pickle.dump(create_id_dict(dic, mint, maxt), open(fprefix + ".id.pkl", "w"))


def dump_support_data(ifname, ofname):
  tweets = pickle.load(open(ifname, "r"))
  ne = defaultdict(int)
  mentions = defaultdict(int)
  pos_tags = defaultdict(int)
  bigram_pos_tags = defaultdict(int)
  trigram_pos_tags = defaultdict(int)
  hashtags = defaultdict(int)
  bow = defaultdict(int)
  filtered_words = defaultdict(int)
  stemmed_bow = defaultdict(int)
  filtered_stemmed = defaultdict(int)
  for i, t in enumerate(tweets):
    if i % 500 == 0:
      print i
    if hasattr(t, "p_ctr") and t.p_ctr != -1:
      add_to_dict(bow, t.p_sanitized_tokens)
      add_to_dict(ne, t.p_named_entities)
      add_to_dict(mentions, t.p_user_mentions)
      add_to_dict(hashtags, t.p_hashtags)
      add_to_dict(filtered_words, t.p_filtered_tokens)
      add_to_dict(stemmed_bow, t.p_stemmed_tokens)
      add_to_dict(filtered_stemmed, t.p_stemmed_filtered_tokens)
      merge_dicts(pos_tags, t.p_pos_tags)
      merge_dicts(bigram_pos_tags, t.p_bigram_pos_tags)
      merge_dicts(trigram_pos_tags, t.p_trigram_pos_tags)
  dump(bow, ofname + "bow")
  dump(pos_tags, ofname + "pos_tags")
  dump(bigram_pos_tags, ofname + "bigram_pos_tags", 50)
  dump(trigram_pos_tags, ofname + "trigram_pos_tags", 50)
  dump(hashtags, ofname + "hashtags")
  dump(filtered_words, ofname + "filtered")
  dump(stemmed_bow, ofname + "stemmed")
  dump(filtered_stemmed, ofname + "filtered_stemmed")
  dump(ne, ofname + "named_entities")  
  dump(mentions, ofname + "user_mentions")
      
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "ERROR : [Enter a Username]"
  else:
    user_id = sys.argv[1] 
    print "Starting processing for ", user_id
    ifname = "data/" + user_id + "/feature_data/tweets.pkl"
    ofname = "data/" + user_id + "/support_data/"
    dump_support_data(ifname, ofname)

