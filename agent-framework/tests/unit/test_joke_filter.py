"""
Unit tests for joke filtering utility functions.
"""

import pytest
from prometheus_swarm.utils.joke_filter import filter_joke, clean_joke

def test_filter_joke_valid_joke():
    joke = "Why did the chicken cross the road? To get to the other side!"
    assert filter_joke(joke) == True

def test_filter_joke_too_long():
    long_joke = "A" * 300
    assert filter_joke(long_joke) == False

def test_filter_joke_with_blacklist():
    joke = "This is an offensive joke about something inappropriate"
    blacklist = ["offensive", "inappropriate"]
    assert filter_joke(joke, blacklist_words=blacklist) == False

def test_filter_joke_non_string_input():
    assert filter_joke(None) == False
    assert filter_joke(123) == False

def test_filter_joke_custom_max_length():
    joke = "Short joke here"
    assert filter_joke(joke, max_length=10) == False
    assert filter_joke(joke, max_length=20) == True

def test_clean_joke_valid_input():
    joke = "   A clean joke   "
    assert clean_joke(joke) == "A clean joke"

def test_clean_joke_non_string_input():
    assert clean_joke(None) == ""
    assert clean_joke(123) == ""

def test_filter_and_clean_together():
    joke = "   An offensive joke about bad things   "
    blacklist = ["offensive", "bad"]
    
    cleaned_joke = clean_joke(joke)
    assert filter_joke(cleaned_joke, blacklist_words=blacklist) == False