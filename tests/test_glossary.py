from nexus import glossary


def test_every_term_is_complete():
    for key, term in glossary.TERMS.items():
        assert key == key.lower() and " " not in key
        assert term.name and term.meaning and term.example


def test_lookup_by_key_name_and_spaces():
    assert glossary.lookup("npv").name.startswith("Net present value")
    assert glossary.lookup("NPV") is glossary.TERMS["npv"]
    assert glossary.lookup("break even") is glossary.TERMS["break-even"]
    assert glossary.lookup("beta") is glossary.TERMS["capm"]
    assert glossary.lookup("not a real term") is None


def test_keys_sorted():
    assert glossary.keys() == sorted(glossary.TERMS)
