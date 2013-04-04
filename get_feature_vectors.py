import pickle
import os
import sys

fv_type = ["bow", "filtered", "stemmed", "filtered_stemmed", "named_entities", "pos_tags", "user_mentions", "hashtags"]
feature_type = ["p_sanitized_tokens", "p_filtered_tokens", "p_stemmed_tokens", "p_stemmed_filtered_tokens", "p_named_entities", "p_pos_tags", "p_user_mentions", "p_hashtags"]
quartile = [1001, 660, 494]
HASHTAG_IDX = 7
MENTIONS_IDX = 6
NAMED_ENTITIES_IDX = 4
POS_IDX = 5

HEADER = """@RELATION techcrunch
@ATTRIBUTE pub_date DATE "yyyy-MM-dd HH:mm:ss"
@ATTRIBUTE word_count NUMERIC
@ATTRIBUTE hashtag NUMERIC
@ATTRIBUTE mention NUMERIC
"""
SENTIMENT_HEADER = """@ATTRIBUTE pos_score NUMERIC
@ATTRIBUTE neg_score NUMERIC
@ATTRIBUTE obj_score NUMERIC
"""
NAMED_ENTITY_HEADER = """@ATTRIBUTE neidx NUMERIC
"""
#@ATTRIBUTE clickrate NUMERIC
END_HEADER = """@ATTRIBUTE class {1,2}
@DATA
"""


def get_dict(user_id, type_idx):
  dict_file = user_id + "/support_data/" + fv_type[type_idx] + ".id.pkl"
  print dict_file
  return pickle.load(open(dict_file))
  
def basic_features(tweet, h, u, start_idx):
  ret = []
  ret += [(start_idx, "\'" + str(tweet.created_at) + "\'"), (start_idx + 1, str(len(tweet.p_sanitized_tokens)))]
  print ret
  if len(tweet.p_hashtags) > 0 and tweet.p_hashtags[0] in h:
    ret.append((start_idx + 2, str(h[tweet.p_hashtags[0]])))
  if len(tweet.p_user_mentions) > 0 and tweet.p_user_mentions[0] in u:
    ret.append((start_idx + 3, str(u[tweet.p_user_mentions[0]])))
  return ret

def sentiment_features(tweet, start_idx):
  ret = []
  pos, neg, obj = zip(*tweet.p_sentiment_scores)
  ret += [ (start_idx , str(sum(pos)/len(pos))), (start_idx + 1, str(sum(neg)/len(neg))), (start_idx + 2, str(sum(obj)/len(obj)))]
  return ret

def pos_features(tweet, p_ids, start_idx):
  ret = []
  for p in tweet.p_pos_tags.keys():
    if p in p_ids:
      ret.append((start_idx + p_ids[p], str(tweet.p_pos_tags[p])))
  return ret

def named_entity_id(t, ne_dict):
  if hasattr(t, "p_named_entities"):
   for ne in t.p_named_entities:
     if ne.lower() in ne_dict:
       return ne_dict[ne.lower()]
       
   for ne in t.p_named_entities:
     sub_nes = ne.split()
     for sne in sub_nes:
       if sne.lower() in ne_dict:
         return ne_dict[sne.lower()]           
  return -1

def named_entity_features(tweet, ne_dict, start_idx):
  n_id = named_entity_id(tweet, ne_dict)
  if n_id != -1:
    return [(start_idx, str(n_id + 1))]
  return [(start_idx, "?")]
  
def dict_features(d, l, start_idx):
  ret = []
  l = [w.lower() for w in l]
  for f in set(l):
    if f.lower() in d:
      ret.append((start_idx + d[f.lower()], "1"))
  return ret

def dict_header(feature_dict, prefix):
  ret = ""
  for i, k in enumerate(sorted(feature_dict.keys())):
    ret += "\n@ATTRIBUTE "+ prefix + str(i) +" NUMERIC"
  return ret

def get_class(ctr):
  if ctr > 700:
    return 1
  return 2
  
def generate_arff(user_id, type_idx, include_sentiment, include_pos, include_ne):
  ifname = user_id + "/feature_data/tweets.pkl"
  ofname = user_id + "/feature_files/" + user_id + "-" + fv_type[type_idx] + "-" + str(include_sentiment) + str(include_pos) + str(include_ne) +  ".arff"
  fvs = ""
  header = HEADER
  if include_sentiment == 1:  
    header += SENTIMENT_HEADER
  if include_pos == 1:    
    pos_dict = get_dict(user_id, POS_IDX)
    header += dict_header(pos_dict, "pos")
  if include_ne == 1:    
    ne_dict = get_dict(user_id, NAMED_ENTITIES_IDX)
    header += NAMED_ENTITY_HEADER
  if type_idx != -1:
    feature_dict = get_dict(user_id, type_idx)
    header += dict_header(feature_dict, "wf")
  header += END_HEADER
  fvs = []
  tweets = pickle.load(open(ifname))
  h = get_dict(user_id, HASHTAG_IDX)
  u = get_dict(user_id, MENTIONS_IDX)
  for t in tweets:
    if not hasattr(t, "p_ctr") or t.p_ctr == -1:
      continue
    fv_str = "{ "
    fv = []
    fv +=  basic_features(t, h, u, 0)
    next_idx = 4
    if include_sentiment == 1:
      fv += sentiment_features(t, next_idx)
      next_idx += 3
    
    if include_pos == 1:
      fv += pos_features(t, pos_dict, next_idx)
      next_idx += len(pos_dict)
      
    if include_ne == 1:
      fv += named_entity_features(t, ne_dict, next_idx)
      next_idx += 1
         
    if type_idx != -1:
      feature_list = getattr(t, feature_type[type_idx])
      fv += dict_features(feature_dict, feature_list, next_idx)
      next_idx += len(feature_dict)
    fv.sort()      
    for f in fv:
      fv_str += str(f[0]) + " " + str(f[1]) + ", "
    fv_str += str(next_idx) + " " + str(get_class(t.p_ctr)) + " }"
#    fv_str += str(next_idx) + " " + str(t.p_ctr) + " }"
#    fv_str += " }"
    fvs.append(fv_str)
  
  f = open(ofname, "w")
  fcontents = header + "\n".join(fvs)
  f.write(fcontents.encode('utf-8'))
  f.close()
      
if __name__ == "__main__":
  if len(sys.argv) != 6:
    print "ERROR : [Enter a Username, type_idx, sentiment_flag, pos_flag, ne_flag]"
  else:
    user_id = sys.argv[1]
    type_idx = int(sys.argv[2])
    include_sentiment = int(sys.argv[3])
    include_pos = int(sys.argv[4])
    include_ne = int(sys.argv[5])
    print "Starting processing for ", user_id, fv_type[type_idx], include_sentiment, include_pos, include_ne
    generate_arff(user_id, type_idx, include_sentiment, include_pos, include_ne)

