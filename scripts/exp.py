from syntaxis.lib.syntaxis import Syntaxis

template = "[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg] [verb:present:active:ter:sg]"

# import pudb; pudb.set_trace()
s = Syntaxis()
tokens = s.generate_sentence(template)
