import re
from bs4 import BeautifulSoup as soup
from snorkel.lf_helpers import *
import string
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords as nltk_stopwords
from db.kb import KnowledgeBase


##### ACRONYM EXTRACTION
# AcroPhenRel = candidate_subclass('AcroPhenRel', ['acro','phen'])

### LFs for extraction from tables
def LF1_digits(m):
    txt = m[1].get_span()
    frac_num = len([ch for ch in txt if ch.isdigit()]) / float(len(txt))
    return -1 if frac_num > 0.5 else +1

def LF1_short(m):
    txt = m[1].get_span()
    return -1 if len(txt) < 5 else 0


### LFs for extraction from text
# helper fns
def r2id(r):
    doc_id = r[0].parent.document.name
    str1, str2 = r[0].get_span(), r[1].get_span()
    acro = str1[1:-1]
    phen = str2.split(' (')[0]
    return (doc_id, acro, phen)

# positive LFs
def LF_acro_matches(m):
    _, acro, phen = r2id(m)
    words = phen.strip().split()
    if len(acro) == len(words):
        w_acro = ''.join([w[0] for w in words])
        if w_acro.lower() == acro.lower():
            return +1
    return 0

def LF_acro_matches_with_dashes(m):
    _, acro, phen = r2id(m)
    words = re.split(' |-', phen)
    if len(acro) == len(words) and len(words) > 0:
        w_acro = ''.join([w[0] for w in words if w])
        if w_acro.lower() == acro.lower():
            return +1
    return 0

def LF_acro_first_letter(m):
    _, acro, phen = r2id(m)
    if not any(l.islower() for l in phen): return 0
    words = phen.strip().split()
    if len(acro) <= len(words):
        if words[0].lower() == acro[0].lower():
            return +1
    return 0

def LF_acro_prefix(m):
    _, acro, phen = r2id(m)
    phen = phen.replace('-', '')
    if phen[:2].lower() == acro[:2].lower():
        return +5
    return 0

def LF_acro_matches_last_letters(m):
    _, acro, phen = r2id(m)
    words = phen.strip().split()
    prev_words = left_text(m[1], window=1) + words
    w_prev_acro = ''.join([w[0] for w in prev_words])
    if w_prev_acro.lower() == acro.lower(): return 0
    for r in (1,2):
        new_acro = acro[r:]
        if len(new_acro) < 3: continue
        if len(new_acro) == len(words):
            w_acro = ''.join([w[0] for w in words])
            if w_acro.lower() == new_acro.lower():
                return +1
    return 0

def LF_full_cell(m):
    """If only phrase in cell is A B C (XYZ), then it's correct"""
    if not hasattr(m[1].parent, 'cell'): return 0
    _, acro, phen = r2id(m)
    cell = m[1].parent.cell
    txt_cell = soup(cell.text).text if cell.text is not None else ''
    txt_span = m[1].get_span()
    return 1 if cell.text == txt_span or txt_cell == txt_span else 0

def LF_start(m):
    punc = ',.;!?()\'"'
    if hasattr(m[1].parent, 'cell'): return 0 # this is only for when we're within a sentence
    if m[1].get_word_start() == 0 or any(c in punc for c in left_text(m[1], window=1)):
        _, acro, phen = r2id(m)
        if phen[0].lower() == acro[0].lower(): 
            return +1
    return 0

# negative LFs
def LF_digits(m):
    txt = m[1].get_span()
    frac_num = len([ch for ch in txt if ch.isdigit()]) / float(len(txt))
    return -1 if frac_num > 0.5 else +1

def LF_short(m):
    _, acro, phen = r2id(m)
    return -1 if len(acro) == 1 else 0

def LF_lc(m):
    _, acro, phen = r2id(m)
    return -1 if all(l.islower() for l in acro) else 0

def LF_uc(m):
    _, acro, phen = r2id(m)
    return -2 if not any(l.islower() for l in phen) else 0

def LF_punc(m):
    _, acro, phen = r2id(m)
    punc = ',.;!?()'
    return -1 if any(c in punc for c in phen) else 0


### PHENOTYPE EXTRACTION (TEXT)
# Phenotype = candidate_subclass('SnorkelPhenotype', ['phenotype'])

punctuation = set(string.punctuation)
stemmer = PorterStemmer()

# load set of dictionary phenotypes
kb = KnowledgeBase()
phenotype_list = kb.get_phenotype_candidates()
phenotype_list = [phenotype for phenotype in phenotype_list]
phenotype_set = set(phenotype_list)

# load stopwords
with open('../data/phenotypes/snorkel/dicts/manual_stopwords.txt') as f:
    stopwords = {line.strip() for line in f}
stopwords.update(['analysis', 'age', 'drug', 'community', 'detect', 'activity', 'genome',
                  'genetic', 'phenotype', 'response', 'population', 'parameter', 'diagnosis',
                  'level', 'survival', 'maternal', 'paternal', 'clinical', 'joint', 'related',
                  'status', 'risk', 'protein', 'association', 'signal', 'pathway', 'genotype', 'scale',
                  'human', 'family', 'heart', 'general', 'chromosome', 'susceptibility', 'select', 
                  'medical', 'system', 'trait', 'suggest', 'confirm', 'subclinical', 'receptor', 
                  'class', 'adult', 'affecting', 'increase'])
stopwords.update(nltk_stopwords.words('english'))
stopwords = {stemmer.stem(word) for word in stopwords}

def get_phenotype(entity, stem=False):
    phenotype = entity.get_span()
    if stem: phenotype = stemmer.stem(phenotype)
    return phenotype.lower()

def stem_list(L):
    return [stemmer.stem(l.lower()) for l in L]

def span(c):
    return c if isinstance(c, TemporarySpan) else c[-1]

def has_stopwords(m):
    txt = span(m).get_span()
    txt = ''.join(ch for ch in txt if ch not in punctuation)
    words = txt.lower().split()
    return True if all(word in stopwords for word in words) or \
                  all(stemmer.stem(word) in stopwords for word in words) or \
                  all(change_name(word) in stopwords for word in words) else False

# positive LFs
def LF_first_sentence(m):
    return +15 if span(m).parent.position == 0 and not has_stopwords(m) else 0

def LF_from_regex(m):
    if span(m).parent.position == 0 and not regex_phen_matcher._f(span(m)) and not LF_bad_words(m): return +5
    else: return 0

def LF_with_acronym(m):
    post_txt = ''.join(right_text(m, attr='words', window=5))
    return +1 if re.search(r'\([A-Z]{2,4}\)', post_txt) else 0

def LF_many_words(m):
    return +1 if len(span(m).get_span().split()) >= 3 else 0

def LF_start_of_sentence(m):
    return +1 if m[0].get_word_start() <= 5 and not has_stopwords(m) and not LF_no_nouns(m) else 0

def LF_first_mention_in_sentence(m):
    context_id = m[0].parent.document.name, m[0].parent.sentence.position
    other_pos = [c.get_word_start() for c in candidate_by_sent[context_id]]
    return +1 if m.get_word_start() == min(other_pos) else 0

# negative LFs
def LF_bad_words(m):
    bad_words = ['disease', 'single', 'map', 'genetic variation', '( p <']
    return -100 if any(span(m).get_span().lower().startswith(b) for b in bad_words) else 0

def LF_short(m):
    txt = span(m).get_attrib_span('words', 3)
    return -50 if len(txt) < 5 else 0

def LF_no_nouns(m):
    return -10 if not any(t.startswith('NN') for t in span(m).get_attrib_tokens('pos_tags')) else 0

def LF_not_first_sentences(m):
    return -1 if span(m).parent.position > 1 else 0

def LF_stopwords(m):
    return -50 if has_stopwords(m) else 0


### PHENOTYPE EXTRACTION (TABLES)
# RsidPhenRel = candidate_subclass('RsidPhenRel', ['rsid','phen'])

bad_words = ['rs number', 'rs id', 'rsid']

# negative LFs
def LF_number(m):
    txt = m[1].get_span()
    frac_num = len([ch for ch in txt if ch.isdigit()]) / float(len(txt))
    return -1 if len(txt) > 5 and frac_num > 0.4 or frac_num > 0.6 else 0

def LF_bad_phen_mentions(m):
    if cell_spans(m[1].parent.cell, m[1].parent.table, 'row'): return 0
    top_cells = get_aligned_cells(m[1].parent.cell, 'col', infer=True)
    top_cells = [cell for cell in top_cells]
    try:
        top_phrases = [phrase for cell in top_cells for phrase in cell.phrases]
    except:
        for cell in top_cells:
            print cell, cell.phrases
    if not top_phrases: return 0
    matching_phrases = []
    for phrase in top_phrases:
        if any (phen_matcher._f_ngram(word) for word in phrase.text.split(' ')):
            matching_phrases.append(phrase)
    small_matching_phrases = [phrase for phrase in matching_phrases if len(phrase.text) <= 25]
    return -1 if not small_matching_phrases else 0

def LF_bad_word(m):
    txt = m[1].get_span()
    return -1 if any(word in txt for word in bad_words) else 0

# positive LFs
def LF_no_neg(m):
    return +1 if not any(LF(m) for LF in LF_tables_neg) else 0