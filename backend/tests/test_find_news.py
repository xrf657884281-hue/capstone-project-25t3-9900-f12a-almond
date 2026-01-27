import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.find_news import RelatedNewsFinder


def create_finder() -> RelatedNewsFinder:
    """
    Helper to instantiate the finder while bypassing spaCy requirements.
    """
    finder = RelatedNewsFinder()
    finder.nlp = None  # Avoid loading spaCy during tests
    return finder


def test_validate_query_specificity_rejects_single_common_word():
    finder = create_finder()
    assert not finder.validate_query_specificity("china")
    assert finder.validate_query_specificity("nvidia growth")


def test_compute_entity_frequencies_counts_case_insensitively():
    finder = create_finder()
    text = (
        "Nvidia dominates the AI chip market. "
        "Investors believe NVIDIA will keep growing as Nvidia expands production."
    )
    entities = ["Nvidia", "AI chip", "Tesla"]
    frequencies = finder.compute_entity_frequencies(text, entities)

    assert frequencies["Nvidia"] == 3
    assert frequencies["AI chip"] == 1
    assert frequencies["Tesla"] == 0


def test_build_search_query_prioritizes_multi_word_entities():
    finder = create_finder()
    text = (
        "Nvidia Corp shares dropped in the Australian market as Nvidia Corp faces new competition. "
        "Analysts in Australia question China's response."
    )
    entities = ["Nvidia Corp", "China", "Australian market"]
    keywords = ["nvidia", "market", "competition"]
    entity_frequencies = {"Nvidia Corp": 2, "China": 1, "Australian market": 1}

    query = finder.build_search_query(text, entities, keywords, entity_frequencies)

    # Multi-word entity should appear first
    assert query.startswith("Nvidia Corp")
    # Keywords should be included after entities without duplication
    assert "market" in query
    # Query should remain reasonably short
    assert len(query.split()) <= 7

