from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers.agile import PythonLexer
from pygments import highlight
from pygments.token import *
from pygments.style import Style
from pygments.formatters import get_formatter_by_name
import sys

from lark import Token
from numpy import ndarray


class PycalcStyle(Style):
    styles = {
        Comment:                'italic #205020',
        String:                 '#905050',
        Name:                   '#EEEEEE',
        Name.Variable:          '#F0F0F0',
        Name.Variable.Magic:    '#A0A0A0',
        Name.Function:          'bold #7A7A7A',
        Name.Constant:          '#C0FFC0',
        Operator:               '#7A7A7A',
        Operator.Word:          '#505090',
        Punctuation:            '#FFFFFF',
    }

class PycalcLexer(RegexLexer):
    name = 'pycalc'
    state = None

    tokens = {
        'root' : [
            (r'#.*', Comment),
            (r'\"(.+?)\"', String),
            (r'[a-zA-Z][a-zA-Z0-9]*', Name),
            (r'\d+', Name.Constant),
            (r'=>', Operator.Word),
            (r'[=+\-/*^&\|!]+', Operator),
            (r'[\[\]\(\)]+', Punctuation),
        ]
    }

    def get_tokens_unprocessed(self, text):
        for index, token, value in super(PycalcLexer, self).get_tokens_unprocessed(text):
            if token is Name and self.state.ctx.contains(value):
                fx = self.state.ctx.get(value)
                if callable(fx) and fx is not ndarray:
                    yield index, Name.Function, value
                elif isinstance(fx, ndarray):
                    yield index, Name.Variable.Magic, value
                else:
                    yield index, Name.Variable, value
            else:
                yield index, token, value
        