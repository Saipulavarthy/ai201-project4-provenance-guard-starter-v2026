"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics

import config

# The marks punctuation_density counts. Full stops and apostrophes are left
# out: every writer uses full stops, and apostrophes are part of words.
_PUNCTUATION = set(",;:-–—?!()\"“”")

# Only the first this-many words go into the type-token ratio, so that a long
# text doesn't score as repetitive just for being long.
_TTR_WINDOW = 100


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies.

    Returns:
        The standard deviation of sentence lengths (in words) divided by their
        mean — the coefficient of variation. 0.0 means every sentence is the
        same length; higher means more varied, which points toward human.

    Fewer than two sentences has no spread to measure and returns 0.0. Note
    what that means downstream: a one-sentence submission looks maximally
    even, so it scores as AI-like on this measure.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0

    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0

    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary, which
        points toward human. 0.0 for text with no words.

    This measure falls as text gets longer, because common words repeat, so
    only the first 100 words are counted. Texts shorter than that are still
    measured on all their words, so very short text tends to score high.
    """
    tokens = words(text)[:_TTR_WINDOW]
    if not tokens:
        return 0.0

    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length.

    Returns:
        Punctuation marks per word. Counts commas, semicolons, colons, dashes,
        question and exclamation marks, parentheses and double quotes — not
        full stops or apostrophes. Higher points toward human. 0.0 for text
        with no words.

    Hyphens inside words ("well-known") count as dashes.
    """
    total_words = len(words(text))
    if total_words == 0:
        return 0.0

    marks = sum(1 for ch in text if ch in _PUNCTUATION)
    return marks / total_words


def _ai_likeness(value: float, ai_at: float, human_at: float) -> float:
    """
    Map a raw measure onto 0–1, where 1.0 is AI-like.

    At or below `ai_at` scores 1.0, at or above `human_at` scores 0.0, and
    in between falls on a straight line.
    """
    if human_at == ai_at:
        return 1.0 if value <= ai_at else 0.0

    score = (human_at - value) / (human_at - ai_at)
    return min(max(score, 0.0), 1.0)


def ai_likenesses(text: str) -> dict[str, float]:
    """Each measure's AI-likeness, 0–1, keyed by the measure's name."""
    return {
        "sentence_length_spread": _ai_likeness(
            sentence_length_spread(text), config.SPREAD_AI_AT, config.SPREAD_HUMAN_AT
        ),
        "type_token_ratio": _ai_likeness(
            type_token_ratio(text), config.TTR_AI_AT, config.TTR_HUMAN_AT
        ),
        "punctuation_density": _ai_likeness(
            punctuation_density(text), config.PUNCT_AI_AT, config.PUNCT_HUMAN_AT
        ),
    }


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    The rule: each of the three measures is mapped onto AI-likeness with a
    clamped straight line between the anchors in config.py (low spread, low
    vocabulary variety and low punctuation all point toward AI), and the three
    AI-likenesses are averaged with equal weight.

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    scores = ai_likenesses(text)
    return round(sum(scores.values()) / len(scores), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    likeness = ai_likenesses(text)

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread              {sentence_length_spread(text):.4f}")
    print(f"type_token_ratio                    {type_token_ratio(text):.4f}")
    print(f"punctuation_density                 {punctuation_density(text):.4f}")
    print(f"sentence_length_spread AI-likeness  {likeness['sentence_length_spread']:.4f}")
    print(f"type_token_ratio AI-likeness        {likeness['type_token_ratio']:.4f}")
    print(f"punctuation_density AI-likeness     {likeness['punctuation_density']:.4f}")
    print(f"style_signal                        {style_signal(text):.4f}   (higher = more likely AI)")
