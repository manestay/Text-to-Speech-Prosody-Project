import jieba
from praatio import tgio

FLAT2ORIG = './flat_to_orig_path.txt'
WORD2PINYIN = "/home/ubuntu/software/kaldi-trunk/egs/aishell2/s5/data/local/DaCiDian/word_to_pinyin.txt"
PINYIN2PHONE = "/home/ubuntu/software/kaldi-trunk/egs/aishell2/s5/data/local/DaCiDian/pinyin_to_phone.txt"

def get_ipus(tg):
    syllable_tier = tg.tierDict['syllable']
    entries =  [entry for entry in syllable_tier.entryList if entry[2] not in set(["#", "##"])]
    xmins = [entry[0] for entry in entries]
    xmaxs = [entry[1] for entry in entries]
    text = [entry[2] for entry in entries]

    ipus = []
    for ipu in text:
        ipu = ipu.replace(' ', '').replace("？", '').replace("#", '')
        words = list(jieba.cut(ipu))
        ipus.append((" ").join(words))
    return ipus, xmins, xmaxs

def load_flat2orig(fname=FLAT2ORIG):
    d = {}
    with open(fname, 'r') as f:
        for line in f:
            key, value = line.strip().split('\t', 1)
            d[key] = value
    return d

def load_word2phone(w2pin_fname=WORD2PINYIN, pin2phon_fname=PINYIN2PHONE):
    w2pin = load_word2pinyin(w2pin_fname)
    pin2phon = load_pinyin2phone(pin2phon_fname)
    w2phon = {}
    for word, prons in w2pin.items():
        w2phon[word] = []
        for pinyin in prons:
            pinyin_list = []
            for p in pinyin.split(' '):
                translit, tone = p.split('_', 1)
                pinyin_list.append('{}_{}'.format(pin2phon[translit], tone))
            w2phon[word].append(tuple(pinyin_list))
    return w2phon


def load_word2pinyin(w2pin_fname=WORD2PINYIN):
    d = {}
    with open(w2pin_fname) as f:
        lines = f.readlines()
    for line in lines:
        word, rest = line.split('\t', 1)
        prons = rest.strip().split(';')
        d[word] = prons
    return d

def load_pinyin2phone(pin2phon_fname=PINYIN2PHONE):
    d = {}
    with open(pin2phon_fname) as f:
        lines = f.readlines()
    for line in lines:
        word, phone = line.split('\t', 1)
        d[word] = phone.strip()
    return d

def main():
    load_word2phone()

if __name__ == "__main__":
    main()
