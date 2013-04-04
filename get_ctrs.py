import urlparse
import httplib
import urllib2
import json
import sys
import pickle
from tokenizer import Tokenizer

def get_ctr(url, subdomain):
  burl = "https://api-ssl.bitly.com/v3/link/clicks?access_token=866c9aa78d244551c1611ac198db8946035f1099&link=http%3A%2F%2F" + subdomain + "%2F"
  res_str = urllib2.urlopen(burl + url).read()
  try:
    res = json.loads(res_str)
    return res["data"]["link_clicks"]
  except:
    print res_str, tweet, url  
  return -1

def extract_url_hash(url, subdomain):
  l = url.split(subdomain + "/")
  if len(l) > 1:
    return subdomain, l[-1]
  else:
    l = url.split("bit.ly" + "/")
    if len(l) > 1:
      return "bit.ly", l[-1]
    else:
      return subdomain, None

def resolve_url_redirect(url, depth=0):
    o = urlparse.urlparse(url,allow_fragments=True)
    conn = httplib.HTTPConnection(o.netloc)
    path = o.path
    if o.query:
        path +='?'+o.query
    conn.request("HEAD", path)
    res = conn.getresponse()
    headers = dict(res.getheaders())
    return headers['location']

def add_ctr(tweet, subdomain):
  if tweet.p_urls and len(tweet.p_urls) == 1:
    res_url = resolve_url_redirect(tweet.p_urls[0])
    setattr(tweet, 'p_res_url', res_url)
    subdomain, url_hash = extract_url_hash(res_url, subdomain)
    if url_hash:
      setattr(tweet, 'p_url_hash', url_hash)
      ctr = get_ctr(url_hash, subdomain)
      setattr(tweet, 'p_ctr', ctr)
    else:
      print "[Valid hash not found, URL]\n ", res_url, tweet.text
  else:
    print "[URL count not 1]\n ", tweet.p_urls

def add_ctrs(ip_file_path, op_file_path, subdomain):
  tweets = pickle.load(open(ip_file_path, "r"))
  print ip_file_path, op_file_path, len(tweets)
  for t in tweets:
    add_ctr(t, subdomain)
  pickle.dump(tweets, open(op_file_path, "w"))

def parse_tweet(tweet, toker):
  toks = toker.tokenize(tweet)
  txt = []
  urls = []
  users = []
  hashtags = []
  for w in toks:
    if w[0] == "@":
      users.append(w)
    elif w[0] == "#":
      hashtags.append(w)
      txt.append(w[1:])
    elif w[0:7] == "http://":
      urls.append(w)
    else:
      txt.append(w)
  return " ".join(txt), urls, users, hashtags


def add_features(tweet, toker):
  txt, urls, users, hashtags = parse_tweet(tweet.text, toker)
  if len(urls) > 1:
    print "[More than 1 URL present]\n URLs: ", urls
  if len(urls) < 1:
    print "[No URLs present]\n Text:", tweet.text
  setattr(tweet, 'p_tokenized_text', txt)
  setattr(tweet, 'p_urls', urls)
  setattr(tweet, 'p_user_mentions', users)
  setattr(tweet, 'p_hashtags', hashtags)
  
def pre_process(ip_file_path, op_file_path, case=False):
  toker = Tokenizer(preserve_case=case)    
  tweets = pickle.load(open(ip_file_path, "r"))
  print ip_file_path, op_file_path, len(tweets)
  for t in tweets:
    add_features(t, toker)
  pickle.dump(tweets, open(op_file_path, "w"))

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print "Enter a Username and subdomain and preserve_case_flag"
  else:
    user_id = sys.argv[1]
    subdomain = sys.argv[2] 
    preserve_case_flag = bool(int(sys.argv[3]))
    print "Starting processing for ", user_id, subdomain, preserve_case_flag
    ifname = user_id + "/raw_data/tweets.pkl"
    ofname = user_id + "/ctr_data/tweets.pkl"
    pre_process(ifname, ofname, preserve_case_flag)
    add_ctrs(ofname, ofname, subdomain)
    
    
