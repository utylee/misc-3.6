from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

MULTI_RE = r'([*/_-]{2})(.*?)\2'

class MultiPattern(Pattern):
    def handleMatch(self, m):
        if m.group(2) ==  '**':
            # BOLD
            tag == 'strong'
        el = etree.Element(tag)
        el.text = m.group(3)
        return el

class MultiExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        multi = MultiPattern(MULTI_RE)
        md.inlinePatterns['multi'] = multi
