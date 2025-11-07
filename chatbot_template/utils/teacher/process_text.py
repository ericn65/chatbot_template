from __future__ import annotations

import string
from pathlib import Path
from typing import Any

import nltk
import numpy as np

from chatbot_template.config.general_config import LANGUAGE, MIN_WORD_LENGTH
from chatbot_template.utils.enums import TextFeatureType

# Download NLTK resources if not present
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOPWORDS: set[str] = set(stopwords.words(LANGUAGE))
"""Stopword list for the specified language."""


class TextProcessor:
    """Text processor for computing linguistic and statistical features."""

    def __init__(self, language: str = LANGUAGE) -> None:
        """
        Initialize the text processor.

        Parameters
        ----------
        language : str
            Language used for tokenization and stopword removal.
        """
        self.language: str = language
        self.stopwords: set[str] = STOPWORDS

    # ----------------------------------------------------------

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize the input text into words.

        Parameters
        ----------
        text : str
            Input text to tokenize.

        Returns
        -------
        tokens : list of str
            List of lowercased tokens without punctuation.
        """
        tokens = word_tokenize(text.lower())
        tokens = [
            tok for tok in tokens if tok.isalpha() and len(tok) >= MIN_WORD_LENGTH
        ]
        return tokens

    # ----------------------------------------------------------

    def extract(
        self,
        text: str,
        feature_type: TextFeatureType,
        save_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """
        Extract features from text according to the selected mode.

        Parameters
        ----------
        text : str
            Input text to analyze.
        feature_type : TextFeatureType
            Type of features to extract (BASIC, LEXICAL, LIWC_SIM).
        save_path : str or Path, optional
            If provided, saves the resulting dictionary as a `.npy` file.

        Returns
        -------
        features : dict
            Dictionary of extracted features.
        """
        tokens = self._tokenize(text)

        if feature_type == TextFeatureType.BASIC:
            features = self._basic_features(tokens, text)

        elif feature_type == TextFeatureType.LEXICAL:
            features = self._lexical_features(tokens)

        elif feature_type == TextFeatureType.LIWC_SIM:
            features = self._liwc_like_features(tokens, text)

        else:
            raise ValueError(f"Unknown feature type: {feature_type}")

        if save_path is not None:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(save_path, np.array([features]), allow_pickle=True)

        return features

    # ----------------------------------------------------------

    def _basic_features(self, tokens: list[str], text: str) -> dict[str, Any]:
        """
        Compute basic text statistics.

        Parameters
        ----------
        tokens : list of str
            Tokenized text.
        text : str
            Original input text.

        Returns
        -------
        features : dict
            Basic metrics such as number of words, characters, punctuation, etc.
        """
        word_count = len(tokens)
        char_count = len(text)
        punct_count = sum(1 for ch in text if ch in string.punctuation)
        avg_word_length = np.mean([len(w) for w in tokens]) if tokens else 0.0

        return {
            "word_count": word_count,
            "char_count": char_count,
            "punctuation_count": punct_count,
            "avg_word_length": avg_word_length,
        }

    # ----------------------------------------------------------

    def _lexical_features(self, tokens: list[str]) -> dict[str, Any]:
        """
        Compute lexical richness features.

        Parameters
        ----------
        tokens : list of str
            Tokenized text.

        Returns
        -------
        features : dict
            Lexical diversity metrics such as type-token ratio and stopword ratio.
        """
        if not tokens:
            return {
                "unique_words": 0,
                "type_token_ratio": 0.0,
                "stopword_ratio": 0.0,
            }

        unique_words = len(set(tokens))
        type_token_ratio = unique_words / len(tokens)
        stopword_ratio = sum(1 for t in tokens if t in self.stopwords) / len(tokens)

        return {
            "unique_words": unique_words,
            "type_token_ratio": type_token_ratio,
            "stopword_ratio": stopword_ratio,
        }

    # ----------------------------------------------------------

    def _liwc_like_features(self, tokens: list[str], text: str) -> dict[str, Any]:
        """
        Compute simplified LIWC-like psycholinguistic features.

        Parameters
        ----------
        tokens : list of str
            Tokenized text.
        text : str
            Original input text.

        Returns
        -------
        features : dict
            Approximation of LIWC categories such as emotion, pronouns, etc.
        """
        if not tokens:
            return {}

        # Example simplified LIWC-style word categories
        liwc_categories: dict[str, set[str]] = {
            "positive_emotion": {"happy", "love", "great", "good", "nice", "amazing"},
            "negative_emotion": {"sad", "bad", "angry", "hate", "terrible", "awful"},
            "first_person": {"i", "me", "my", "mine"},
            "second_person": {"you", "your", "yours"},
            "third_person": {"he", "she", "they", "them"},
        }

        counts = {cat: 0 for cat in liwc_categories}
        for token in tokens:
            for cat, vocab in liwc_categories.items():
                if token in vocab:
                    counts[cat] += 1

        total_words = len(tokens)
        normalized = {
            f"{cat}_ratio": count / total_words for cat, count in counts.items()
        }

        return {**counts, **normalized}
