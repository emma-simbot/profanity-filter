from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Tuple

import dill
import pytest
import spacy.language
from ordered_set import OrderedSet
from profanity_filter import Config
from profanity_filter.profanity_filter import ProfanityFilter
from profanity_filter.types_ import (AnalysesTypes, Language,
                                     ProfaneWordDictionaries)


@dataclass
class Config:
    analyses: AnalysesTypes = frozenset()
    censor_whole_words: bool = True
    deep_copy: bool = False
    dill: bool = False
    languages: Tuple[Language, ...] = ('en_core_web_sm', 'ru_core_news_sm')


def create_profane_word_dictionaries(**kwargs) -> ProfaneWordDictionaries:
    return defaultdict(lambda: OrderedSet(), **kwargs)


@pytest.fixture
def empty_profane_word_dictionaries() -> ProfaneWordDictionaries:
    return create_profane_word_dictionaries()


@pytest.fixture
def pf(request) -> ProfanityFilter:
    config: Config = request.param
    result = ProfanityFilter(
        languages=config.languages,
        analyses=config.analyses,
        censor_whole_words=config.censor_whole_words,
    )
    for analysis in config.analyses:
        if analysis not in result.analyses:
            pytest.skip(f"Couldn't initialize {analysis.value} analysis")
    if config.deep_copy:
        result = deepcopy(result)
    if config.dill:
        result = dill.loads(dill.dumps(result))
    return result


@pytest.fixture
def nlp(pf) -> spacy.language.Language:
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(pf.spacy_component('en_core_web_sm'), last=True)
    return nlp


def with_config(config: Config):
    def decorator(f):
        return pytest.mark.parametrize(
            'pf',
            [config, replace(config, deep_copy=True), replace(config, dill=True)],
            indirect=True,
            ids=['new', 'deep_copy', 'dill'],
        )(f)

    return decorator


TEST_STATEMENT = "Hey, I like unicorns, chocolate, oranges and man's blood, turd!"
TEST_STATEMENT_WITH_PROFANE_PHRASE = "Hey, cut your arm"
CLEAN_STATEMENT = "Hey there, I like chocolate too mate."
