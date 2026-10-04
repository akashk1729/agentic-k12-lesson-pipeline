from src.gates.quote_gate import quote_exists


def test_valid_quote_passes():

    book_text = """
    A freely suspended magnet comes to rest along the
    north-south direction.
    """

    quote = "A freely suspended magnet comes to rest along the north-south direction."

    assert quote_exists(quote, book_text)


def test_fake_quote_fails():

    book_text = """
    A freely suspended magnet comes to rest along the
    north-south direction.
    """

    fake_quote = "A freely suspended magnet always points towards the east."

    assert not quote_exists(fake_quote, book_text)