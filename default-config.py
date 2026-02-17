# Configuration par défaut pour nerd-dictation avec ponctuation française
# Ce fichier est automatiquement installé dans ~/.config/nerd-dictation/nerd-dictation.py

# Dictionnaire des mots-nombres français vers leurs valeurs
_UNITS = {
    "zéro": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4,
    "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9,
    "dix": 10, "onze": 11, "douze": 12, "treize": 13, "quatorze": 14,
    "quinze": 15, "seize": 16, "dix-sept": 17, "dix-huit": 18, "dix-neuf": 19,
    "vingt": 20, "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60,
}

_MULTIPLIERS = {"cent": 100, "cents": 100, "mille": 1000, "million": 1_000_000,
                "millions": 1_000_000, "milliard": 1_000_000_000, "milliards": 1_000_000_000}

_ALL_NUMBER_WORDS = set(_UNITS) | set(_MULTIPLIERS) | {"et", "vingts"}


def _is_number_word(word):
    return word in _ALL_NUMBER_WORDS


def _parse_number_sequence(words):
    """Parse a list of French number words into an integer.

    Algorithm:
    - `current` accumulates the group in progress (0-999)
    - `result` accumulates the total across multiplier boundaries
    - milliard/million: result += (current or 1) * value, reset current
    - mille: result += (current or 1) * 1000, reset current
    - cent/cents: current = (current or 1) * 100
    - vingts after quatre (quatre-vingts): current = 80
    - other: current += value
    """
    result = 0
    current = 0

    i = 0
    while i < len(words):
        word = words[i]

        if word == "et":
            i += 1
            continue

        # Look-ahead: "quatre" + "vingt(s)" = 80
        if word == "quatre" and i + 1 < len(words) and words[i + 1] in ("vingt", "vingts"):
            current += 80
            i += 2
            continue

        if word in _UNITS:
            current += _UNITS[word]
            i += 1
            continue

        if word in ("cent", "cents"):
            if current == 0:
                current = 100
            else:
                current *= 100
            i += 1
            continue

        if word in ("vingts",):
            # Standalone "vingts" without preceding "quatre" (shouldn't happen in valid French)
            current += 20
            i += 1
            continue

        if word == "mille":
            if current == 0:
                result += 1000
            else:
                result += current * 1000
                current = 0
            i += 1
            continue

        if word in ("million", "millions", "milliard", "milliards"):
            mult = _MULTIPLIERS[word]
            if current == 0:
                result += mult
            else:
                result += current * mult
                current = 0
            i += 1
            continue

        i += 1

    result += current
    return result


def _convert_numbers(text):
    """Convert French number words in text to digits.

    Tokenizes on spaces, identifies consecutive number-word sequences,
    parses each sequence, and replaces with the computed digit.
    """
    tokens = text.split(" ")
    output = []
    num_words = []

    def flush_number():
        if num_words:
            value = _parse_number_sequence(num_words)
            output.append(str(value))
            num_words.clear()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        # Expand hyphenated words for number detection
        sub_tokens = token.split("-")

        # Check if all sub-tokens are number words
        all_number = all(_is_number_word(st) for st in sub_tokens if st)

        if all_number and sub_tokens:
            # "et" is only a number word if followed by "un", "une", or "onze"
            if sub_tokens == ["et"]:
                # Standalone "et" — check if next token starts a number with un/une/onze
                if i + 1 < len(tokens):
                    next_sub = tokens[i + 1].split("-")
                    next_first = next_sub[0] if next_sub else ""
                    if next_first in ("un", "une", "onze") and num_words:
                        num_words.append("et")
                        i += 1
                        continue
                # Not part of a number sequence
                flush_number()
                output.append(token)
                i += 1
                continue

            num_words.extend(sub_tokens)
            i += 1
            continue

        # Not a number word
        flush_number()
        output.append(token)
        i += 1

    flush_number()
    return " ".join(output)


def nerd_dictation_process(text):
    """
    Fonction de remplacement pour améliorer la ponctuation française
    et les expressions courantes.
    """

    # 1. Ponctuation multi-mots contenant des mots-nombres (AVANT conversion)
    # Ces expressions contiennent "deux", "et", "point" qui interféreraient avec le parseur
    text = text.replace(" point d'interrogation", " ?")
    text = text.replace(" point interrogation", " ?")
    text = text.replace(" interrogation", " ?")
    text = text.replace(" question", " ?")

    text = text.replace(" point d'exclamation", " !")
    text = text.replace(" point exclamation", " !")
    text = text.replace(" exclamation", " !")

    text = text.replace(" deux points", " :")
    text = text.replace(" point virgule", " ;")

    # Parenthèses et guillemets
    text = text.replace(" parenthèse ouverte", " (")
    text = text.replace(" parenthèse fermée", ")")
    text = text.replace(" guillemet ouvrant", ' "')
    text = text.replace(" guillemet fermant", '"')
    text = text.replace(" apostrophe", "'")

    # Navigation et formatage
    text = text.replace(" nouvelle ligne", "\n")
    text = text.replace(" retour à la ligne", "\n")
    text = text.replace(" tabulation", "\t")
    text = text.replace(" espace", " ")

    # Expressions communes
    text = text.replace(" arobase", "@")
    text = text.replace(" diese", "#")
    text = text.replace(" pourcentage", "%")
    text = text.replace(" étoile", "*")
    text = text.replace(" plus", "+")
    text = text.replace(" égal", "=")
    text = text.replace(" moins", "-")
    text = text.replace(" divisé par", "/")
    text = text.replace(" barre oblique", "/")

    # 2. Conversion des nombres
    text = _convert_numbers(text)

    # 3. Ponctuation simple APRÈS conversion (ces remplacements collent le signe au mot précédent)
    text = text.replace(" et commercial", "&")
    text = text.replace(" point", ".")
    text = text.replace(" virgule", ",")
    text = text.replace(" tiret", "-")

    # 4. Nettoyer les espaces en trop autour de certains signes
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace("( ", "(")
    text = text.replace(' "', '"')

    return text
