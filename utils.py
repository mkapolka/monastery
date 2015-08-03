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
