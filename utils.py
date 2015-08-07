import collections

import ui


def number_prompt(options, prompt, str_func):
    if not str_func:
        str_func = str
    for n, option in enumerate(options, 1):
        ui.message('[%d] %s' % (n, str_func(option)))
    while True:
        value = ui.get_char()
        if value == 'q':
            return None
        try:
            return options[int(value) - 1]
        except (ValueError, IndexError):
            ui.message("Invalid choice. Choose 1-%d or 'q'" % len(options))


def eletterate(options, reserved_letters=None):
    if not reserved_letters:
        reserved_letters = []
    letters = list('abcdefghijklmnopqrstuvwxyz')
    for letter in reserved_letters:
        if letter in letters:
            letters.remove(letter)
    for letter, option in zip(letters, options):
        yield letter, option


def letter_prompt(options, prompt, str_func):
    if not str_func:
        str_func = str
    loppies = dict(eletterate(options, 'q'))
    dd = dict([
        (l, (str_func(option), option)) for (l, option) in loppies.items()
    ])
    return ui.prompt(prompt, dd)
    while True:
        value = ui.get_char()
        if value == 'q':
            return None
        try:
            return loppies[value]
        except (ValueError, IndexError):
            ui.message("Invalid choice." % len(options))


def fuzzy_filter(string, words):
    def word_thingy(string, word):
        for letter in string:
            if letter in word:
                word = word[word.index(letter):]
            else:
                return False
        return True

    return filter(lambda word: word_thingy(string, word), words)


def letters_for_word_tuples(word_tuples):
    """ (word, object) """
    words = [word for (word, ob) in word_tuples]

    lfw = letters_for_words(words)
    output = {}
    for letters, word in lfw.items():
        word_count = words.count(word)
        if word_count > 1:
            del lfw[letters]
            items = [ob for ob in word_tuples if ob[0] == word]
            for n, item in enumerate(items, 1):
                output['%s%d' % (letters, n)] = item
        else:
            item = [ob for ob in word_tuples if ob[0] == word]
            output[letters] = item[0]
    return output


def letters_for_words(words):
    """
    input: [words]
    returns {letters: word}
    """
    word_set = set(words)
    diccy = collections.defaultdict(list)
    diccy[''] = [(_sig_word(w), w) for w in word_set]
    while any([len(v) > 1 for v in diccy.values()]):
        for letters, words in [(k, v) for (k, v) in diccy.items() if len(v) > 1]:
            del diccy[letters]
            for sig_word, word in words:
                diccy['%s%s' % (letters, sig_word[len(letters)])].append((sig_word, word))
    return dict([
        (letters, word[0][1]) for (letters, word) in diccy.items()
    ])


def _sig_word(string):
    parts = string.lower().split()
    no_stop_words = filter(lambda x: x not in stopwords, parts)
    if no_stop_words:
        return no_stop_words[0]
    else:
        return parts[0]


def flatten_array(ary):
    return [item for sublist in ary for item in sublist]


def sentence(ary):
    """ Pass an array of strings """
    if len(ary) > 1:
        ary[-1] = "and %s" % ary[-1]

    if len(ary) > 2:
        return ", ".join(ary)
    else:
        return " ".join(ary)

stopwords = set([u'i', u'me', u'my', u'myself', u'we', u'our', u'ours',
                 u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he',
                 u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its',
                 u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what',
                 u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is',
                 u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had',
                 u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and',
                 u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at',
                 u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through',
                 u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up',
                 u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further',
                 u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all',
                 u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such',
                 u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too',
                 u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now'])
