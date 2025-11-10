"""Translation mappings between syntaxis and modern_greek_inflexion constants."""

from modern_greek_inflexion import resources

from syntaxis.models import constants as c

# Syntaxis -> modern_greek_inflexion mappings
SYNTAXIS_TO_MGI = {
    # Gender
    c.MASCULINE: resources.MASC,
    c.FEMININE: resources.FEM,
    c.NEUTER: resources.NEUT,
    # Number
    c.SINGULAR: resources.SG,
    c.PLURAL: resources.PL,
    # Case
    c.NOMINATIVE: resources.NOM,
    c.ACCUSATIVE: resources.ACC,
    c.GENITIVE: resources.GEN,
    c.VOCATIVE: resources.VOC,
    # Tense (constants match MGI values directly)
    c.PRESENT: resources.PRESENT,
    c.AORIST: resources.AORIST,
    c.PARATATIKOS: resources.PARATATIKOS,
    # Voice (constants match MGI values directly)
    c.ACTIVE: resources.ACTIVE,
    c.PASSIVE: resources.PASSIVE,
    # Mood
    c.INDICATIVE: resources.IND,
    c.IMPERATIVE: resources.IMP,
    # Person (constants match MGI values directly)
    c.FIRST: resources.PRI,
    c.SECOND: resources.SEC,
    c.THIRD: resources.TER,
    # Aspect
    c.PERFECT: resources.PERF,
    c.IMPERFECT: resources.IMPERF,
}

# Reverse mapping for translating mgi results back to syntaxis
MGI_TO_SYNTAXIS = {v: k for k, v in SYNTAXIS_TO_MGI.items()}
