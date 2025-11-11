from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse


def test_lexical_response_minimal():
    """LexicalResponse with minimal fields."""
    lexical = LexicalResponse(
        lemma="άνδρας",
        word={"άνδρας"},
        translations={"man", "male"},
        features={"case": "nom", "gender": "masc", "number": "sg"},
    )
    assert lexical.lemma == "άνδρας"
    assert lexical.word == {"άνδρας"}
    assert lexical.features["case"] == "nom"


def test_lexical_response_allows_none_word():
    """LexicalResponse allows None for word field."""
    lexical = LexicalResponse(
        lemma="test",
        word=None,
        translations={"test"},
        features={},
    )
    assert lexical.word is None


def test_lexical_response_allows_none_translations():
    """LexicalResponse allows None for translations field."""
    lexical = LexicalResponse(
        lemma="test",
        word={"test"},
        translations=None,
        features={},
    )
    assert lexical.translations is None


def test_generate_response_with_lexicals():
    """GenerateResponse contains template and lexicals."""
    lexicals = [
        LexicalResponse(
            lemma="ο",
            word={"ο"},
            translations={"the"},
            features={"case": "nom", "gender": "masc", "number": "sg"},
        ),
        LexicalResponse(
            lemma="άνδρας",
            word={"άνδρας"},
            translations={"man"},
            features={"case": "nom", "gender": "masc", "number": "sg"},
        ),
    ]

    response = GenerateResponse(
        template="[article:nom:masc:sg] [noun:nom:masc:sg]",
        lexicals=lexicals,
    )

    assert response.template == "[article:nom:masc:sg] [noun:nom:masc:sg]"
    assert len(response.lexicals) == 2
    assert response.lexicals[0].lemma == "ο"


def test_generate_response_empty_lexicals():
    """GenerateResponse allows empty lexicals list."""
    response = GenerateResponse(template="test", lexicals=[])
    assert response.lexicals == []
