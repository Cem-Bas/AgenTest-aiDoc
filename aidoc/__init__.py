"""
AiDoc - Advanced Web Console Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AiDoc is a powerful web console analysis tool that helps developers identify
and debug issues in web applications.

Basic usage:

    >>> from aidoc import analyze_url
    >>> results = analyze_url('https://example.com')

For more information, please see: https://github.com/agentest/aidoc
"""

__version__ = '1.0.0'
__author__ = 'AgenTest.ai'
__license__ = 'MIT'

from .AiDoc import main as analyze_url

__all__ = ['analyze_url']
