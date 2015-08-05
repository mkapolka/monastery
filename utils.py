def number_prompt(options, prompt, str_func):
    if not str_func:
        str_func = str
    for n, option in enumerate(options, 1):
        print '[%d] %s' % (n, str_func(option))
    while True:
        value = raw_input(prompt)
        if value == 'q':
            return None
        try:
            return options[int(value) - 1]
        except (ValueError, IndexError):
            print "Invalid choice. Choose 1-%d or 'q'" % len(options)


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
