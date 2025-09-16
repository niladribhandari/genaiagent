"""
Pluralization utility for proper English grammar in code generation.
"""

from typing import Dict, List


class PluralizationEngine:
    """Handle English pluralization rules for code generation."""
    
    # Irregular plurals that don't follow standard rules
    IRREGULAR_PLURALS = {
        'policy': 'policies',
        'company': 'companies',
        'category': 'categories',
        'country': 'countries',
        'city': 'cities',
        'party': 'parties',
        'facility': 'facilities',
        'authority': 'authorities',
        'priority': 'priorities',
        'entity': 'entities',
        'activity': 'activities',
        'opportunity': 'opportunities',
        'community': 'communities',
        'university': 'universities',
        'family': 'families',
        'library': 'libraries',
        'dictionary': 'dictionaries',
        'factory': 'factories',
        'history': 'histories',
        'memory': 'memories',
        'story': 'stories',
        'mystery': 'mysteries',
        'injury': 'injuries',
        'entry': 'entries',
        'query': 'queries',
        'theory': 'theories',
        'strategy': 'strategies',
        'person': 'people',
        'child': 'children',
        'man': 'men',
        'woman': 'women',
        'mouse': 'mice',
        'goose': 'geese',
        'foot': 'feet',
        'tooth': 'teeth',
        'leaf': 'leaves',
        'knife': 'knives',
        'life': 'lives',
        'wife': 'wives',
        'half': 'halves',
        'shelf': 'shelves',
        'wolf': 'wolves',
        'calf': 'calves',
        'elf': 'elves',
        'loaf': 'loaves',
        'thief': 'thieves',
        'chief': 'chiefs',
        'roof': 'roofs',
        'proof': 'proofs',
        'staff': 'staff',
        'fish': 'fish',
        'sheep': 'sheep',
        'deer': 'deer',
        'series': 'series',
        'species': 'species',
        'means': 'means',
        'data': 'data',
        'information': 'information'
    }
    
    # Words ending in these letters get 'es' instead of 's'
    ES_ENDINGS = ['s', 'sh', 'ch', 'x', 'z', 'ss']
    
    # Words ending in consonant + 'y' change 'y' to 'ies'
    CONSONANTS = 'bcdfghjklmnpqrstvwxz'
    
    @classmethod
    def pluralize(cls, word: str) -> str:
        """
        Convert a singular word to its plural form using English pluralization rules.
        
        Args:
            word: The singular word to pluralize
            
        Returns:
            The plural form of the word
        """
        if not word:
            return word
            
        word_lower = word.lower()
        
        # Check irregular plurals first
        if word_lower in cls.IRREGULAR_PLURALS:
            plural_lower = cls.IRREGULAR_PLURALS[word_lower]
            # Preserve original capitalization
            return cls._preserve_case(word, plural_lower)
        
        # Handle words ending in consonant + 'y' -> change 'y' to 'ies'
        if word_lower.endswith('y') and len(word_lower) > 1:
            if word_lower[-2].lower() in cls.CONSONANTS:
                plural = word[:-1] + 'ies'
                return plural
        
        # Handle words ending in 'f' or 'fe' -> change to 'ves'
        if word_lower.endswith('f'):
            plural = word[:-1] + 'ves'
            return plural
        elif word_lower.endswith('fe'):
            plural = word[:-2] + 'ves'
            return plural
        
        # Handle words ending in 'o' -> add 'es' (with exceptions)
        if word_lower.endswith('o'):
            # Exceptions that just add 's'
            o_exceptions = ['photo', 'piano', 'halo', 'auto', 'memo', 'radio', 'studio', 'video']
            if word_lower not in o_exceptions:
                plural = word + 'es'
                return plural
        
        # Handle words ending in sounds that need 'es'
        for ending in cls.ES_ENDINGS:
            if word_lower.endswith(ending):
                plural = word + 'es'
                return plural
        
        # Default: add 's'
        return word + 's'
    
    @classmethod
    def _preserve_case(cls, original: str, transformed: str) -> str:
        """
        Preserve the capitalization pattern of the original word.
        
        Args:
            original: The original word with its capitalization
            transformed: The lowercase transformed word
            
        Returns:
            The transformed word with preserved capitalization
        """
        if not original or not transformed:
            return transformed
            
        # If original is all uppercase
        if original.isupper():
            return transformed.upper()
        
        # If original starts with uppercase (title case)
        if original[0].isupper():
            return transformed[0].upper() + transformed[1:]
        
        # Otherwise, return as lowercase
        return transformed


# Convenience function for direct use
def pluralize(word: str) -> str:
    """
    Pluralize a word using English pluralization rules.
    
    Args:
        word: The singular word to pluralize
        
    Returns:
        The plural form of the word
        
    Examples:
        >>> pluralize('Policy')
        'Policies'
        >>> pluralize('User')
        'Users'
        >>> pluralize('Company')
        'Companies'
    """
    return PluralizationEngine.pluralize(word)


def singularize(word: str) -> str:
    """
    Convert a plural word to its singular form (basic implementation).
    
    Args:
        word: The plural word to singularize
        
    Returns:
        The singular form of the word (best effort)
    """
    if not word:
        return word
        
    word_lower = word.lower()
    
    # Reverse lookup in irregular plurals
    for singular, plural in PluralizationEngine.IRREGULAR_PLURALS.items():
        if word_lower == plural:
            return PluralizationEngine._preserve_case(word, singular)
    
    # Basic rules (not comprehensive)
    if word_lower.endswith('ies') and len(word) > 3:
        return word[:-3] + 'y'
    elif word_lower.endswith('ves'):
        return word[:-3] + 'f'
    elif word_lower.endswith('es') and len(word) > 2:
        # Check if it's a word that naturally ends in 'es'
        base = word[:-2]
        if base.endswith(tuple(PluralizationEngine.ES_ENDINGS[:-1])):  # Exclude 'ss'
            return word[:-2]
        return word[:-1]  # Just remove 's'
    elif word_lower.endswith('s') and len(word) > 1:
        return word[:-1]
    
    return word  # Return as-is if can't singularize


# Export main functions
__all__ = ['pluralize', 'singularize', 'PluralizationEngine']
