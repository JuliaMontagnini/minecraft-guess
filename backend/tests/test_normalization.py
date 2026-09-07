from app.game_service import normalize_guess


def test_lowercase():
    assert (
        normalize_guess("VACA")
        == normalize_guess("vaca")
    )


def test_accent_removal():
    assert (
        normalize_guess(
            "Câmaras do Desafio"
        )
        ==
        normalize_guess(
            "Camaras do Desafio"
        )
    )


def test_extra_spaces():
    assert (
        normalize_guess(
            "  Vaca   Cogumelo  "
        )
        ==
        "vaca cogumelo"
    )


def test_unicode_and_case():
    assert (
        normalize_guess("ESPECTRO")
        ==
        normalize_guess("Espectro")
    )