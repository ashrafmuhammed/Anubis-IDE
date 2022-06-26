import sys
from typing import Literal
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages

STYLES = {
       'keyword': format('blue'),
      'operator': format('red'),
       'brace': format('darkGray'),
       'class': format('blue'),
       'classID': format('black', 'bold italic'),
       'string': format('magenta'),
       'string2': format('darkMagenta'),
       'comment': format('darkGreen', 'italic'),
       'numbers': format('purple'),
        'logicalOperators': format('green'),
        'literalKeywords':format('lightBlue'),
        'accessKeywords': format('lightBlue'),
        'typeKeywords':format('blue')


   }

class CSharpHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the C Sharp language.
    """
    #CSharp keywords
    keywords =[

    #Modifier Keywords
        'abstract', 'async', 'const', 'event',
        'extern', 'new', 'override', 'partial',
        'readonly', 'sealed', 'static', 'unsafe', 
        'virtual', 'volatile',

    #Access Modifier Keywords
        'public', 'private', 'protected', 'internal',
    
    #Statement Keywords
        'if', 'else', 'switch', 'case', 'do', 'for',
        'foreach', 'in', 'while', 'break', 'continue',
        'default', 'goto', 'return', 'yield', 'throw',
        'try', 'catch', 'finally', 'checked', 'unchecked',
        'fixed', 'lock',

    #Namespace Keywords
        'using', '. operator' , ':: operator', 'extern alias',

    #Operator Keywords
        'as', 'await', 'is', 'new', 'sizeof', 'typeof',
        'stackalloc', 'checked', 'unchecked',

    #Contextual Keywords
        'add', 'var', 'dynamic', 'global', 'set', 'value',

    #Query Keywords
        'from', 'where', 'select', 'group', 'into', 'orderby',
        'join', 'let', 'in', 'on', 'equals', 'by', 'ascending', 'descending'
    ]

    literalKeywords = [
        'null', 'false', 'true', 'value', 'void'
    ]

    typeKeywords = [
        'bool', 'byte', 'char', 'class', 'decimal',
         'double', 'enum', 'float', 'int', 'long', 
         'sbyte', 'short', 'string', 'struct', 'uint', 
         'ulong', 'ushort'
    ]

    accessKeywords = [
        'base','this'
    ]

    # CSharp operators
    operators = [
        '=',
        # logical
        '!', '?', ':',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '\%', '\+\+', '--',
        # Assignment
        '\+=', '-=', '\*=', '/=', '\%=', '<<=', '>>=', '\&=', '\^=', '\|=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Logical Operators
    logicalOperators = [
        '&&','\|\|', '!','<<','>>'
    ]

    # braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CSharpHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CSharpHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CSharpHighlighter.braces]
        rules += [(r'%s' % b, 0, STYLES['logicalOperators'])
                  for b in CSharpHighlighter.logicalOperators]
        
        rules += [(r'\b%s\b' % w, 0, STYLES['literalKeywords'])
                  for w in CSharpHighlighter.literalKeywords]
        rules += [(r'\b%s\b' % w, 0, STYLES['accessKeywords'])
                  for w in CSharpHighlighter.accessKeywords]
        rules += [(r'\b%s\b' % w, 0, STYLES['typeKeywords'])
                  for w in CSharpHighlighter.typeKeywords]
    

        # All other rules
        rules += [

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # Comments from '//' until a newline
            (r'//[^\n]*', 0, STYLES['comment']),

           

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),

            # Class
            (r'\bClass\b',0,STYLES['class']),

            # 'class' followed by an identifier	
            (r'\bclass\b\s*(\w+)', 1, STYLES['classID']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False