from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers.agile import PythonLexer
from pygments import highlight
from pygments.token import *
from pygments.formatters import get_formatter_by_name
import sys

from newlang import State
from lark import Token

class PycalcLexer(RegexLexer):
    name = 'pycalc'

    tokens = {
        'root' : [
            (r'#.*', Comment),
            (r'[a-zA-Z][a-zA-Z0-9]*(.*)', Name.Function),
            (r'[a-zA-Z][a-zA-Z0-9]*', Name.Variable),
        ]
    }
        