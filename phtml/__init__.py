from copy import deepcopy
from cStringIO import StringIO


INDENT_SIZE = 2


def escape(text, quote=True):
    for k, v in ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'):
        text = text.replace(k, v)

    if quote:
        for k, v in ('"', '&quot;'), ("'", '&#x27;'):
            text = text.replace(k, v)

    return text


class Block(object):
    """List of renderable items."""

    whitespace_sensitive = False
    safe = False

    def __init__(self, name):
        self.name = name
        self.children = ()

    def __repr__(self):
        return 'Block(%r)' % self.name

    def __call__(self, *children):
        self.children = children
        return self

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        is_last_item = lambda: i == len(self.children) - 1

        for i, child in enumerate(self.children):
            self._write_single(out, child, indent, context)

            if not self.whitespace_sensitive and not is_last_item():
                out.write('\n')

        return out.getvalue()

    def _write_single(self, out, child, indent, context):
        if isinstance(child, Block):
            child.__str__(out, indent, **context)
        else:
            if callable(child) and not isinstance(child, _TagMeta):
                s = child(context)
            else:
                s = child

            # Convert to string
            if isinstance(s, unicode):
                s = s.encode('utf-8')
            else:
                s = str(s)

            if not isinstance(child, _TagMeta):
                if not self.safe:
                    s = escape(s)

            # Write content
            if not self.whitespace_sensitive:
                lines = s.splitlines(True)
                for line in lines:
                    out.write(' ' * indent)
                    out.write(line)
            else:
                out.write(s)

    def copy(self):
        return deepcopy(self)

    def render(self, **context):
        return self.__str__(**context)

    def __setitem__(self, block_name, *children):
        """Fill all the Blocks with same block_name
        in this tag recursively.
        """
        blocks = self._find_blocks(block_name)
        for b in blocks:
            b(*children)

    def _find_blocks(self, name):
        blocks = []
        for i, c in enumerate(self.children):
            if isinstance(c, Block) and c.name == name:
                blocks.append(c)
            elif isinstance(c, Tag):
                blocks += c._find_blocks(name)
        return blocks


class _TagMeta(type):
    """Type of the Tag. (type(Tag) == TagMeta)
    """
    def __str__(cls):
        """Renders as empty tag."""
        return '<%s></%s>' % (cls.__name__, cls.__name__)


class Tag(Block):

    __metaclass__ = _TagMeta

    doctype = None

    def __init__(self, *children, **attributes):
        # Only children or attributes may be set at a time.
        assert ((bool(children) ^ bool(attributes))
                or (not children and not attributes))

        self.children = children
        self.attributes = attributes

    def __call__(self, *children):
        """Set children of this tag."""
        self.children = children
        return self

    def __repr__(self):
        return '%s()' % self.name

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        # Write doctype
        if self.doctype:
            out.write(' ' * indent)
            out.write(self.doctype)
            out.write('\n')

        # Indent opening tag
        out.write(' ' * indent)

        # Open tag
        out.write('<%s' % self.name)

        self._write_attributes(out)

        # Close opening tag
        out.write('>')

        if self.children:
            # Newline after opening tag
            if not self.whitespace_sensitive:
                out.write('\n')

            # Write content
            super(Tag, self).__str__(out, indent + INDENT_SIZE, **context)

            if not self.whitespace_sensitive:
                # Newline after content
                out.write('\n')
                # Indent closing tag
                out.write(' ' * indent)

        # Write closing tag
        out.write('</%s>' % self.name)

        return out.getvalue()

    def _write_attributes(self, out):
        for k, v in self.attributes.items():
            # Some attribute names such as "class" conflict
            # with reserved keywords in Python. These must
            # be postfixed with underscore by user.
            if k.endswith('_'):
                k = k.rstrip('_')

            if isinstance(v, unicode):
                v = v.encode('utf-8')

            out.write(' %s="%s"' % (k, v))

    @property
    def name(self):
        return self.__class__.__name__


class _SelfClosingTagMeta(_TagMeta):
    def __str__(cls):
        """Renders as self closing tag."""
        return '<%s/>' % cls.__name__


class SelfClosingTag(Tag):

    __metaclass__ = _SelfClosingTagMeta

    def __init__(self, **attributes):
        super(SelfClosingTag, self).__init__(**attributes)

    def __call__(self, *args, **kwargs):
        raise Exception("Self closing tag can't have children")

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        # Indent
        out.write(' ' * indent)

        # Open tag
        out.write('<%s' % self.name)

        self._write_attributes(out)

        # Close tag
        out.write('/>')

        return out.getvalue()


class WhitespaceSensitiveTag(Tag):
    whitespace_sensitive = True


class head(Tag): pass
class body(Tag): pass
class title(Tag): pass
class div(Tag): pass
class p(Tag): pass
class h1(Tag): pass
class h2(Tag): pass
class h3(Tag): pass
class h4(Tag): pass
class h5(Tag): pass
class h6(Tag): pass
class u(Tag): pass
class b(Tag): pass
class i(Tag): pass
class s(Tag): pass
class a(Tag): pass
class em(Tag): pass
class strong(Tag): pass
class span(Tag): pass
class font(Tag): pass
class del_(Tag): pass
class ins(Tag): pass
class ul(Tag): pass
class ol(Tag): pass
class li(Tag): pass
class dd(Tag): pass
class dt(Tag): pass
class dl(Tag): pass
class article(Tag): pass
class section(Tag): pass
class nav(Tag): pass
class aside(Tag): pass
class header(Tag): pass
class footer(Tag): pass
class audio(Tag): pass
class video(Tag): pass
class object_(Tag): pass
class embed(Tag): pass
class param(Tag): pass
class fieldset(Tag): pass
class legend(Tag): pass
class button(Tag): pass
class textarea(Tag): pass
class label(Tag): pass
class select(Tag): pass
class option(Tag): pass
class table(Tag): pass
class thead(Tag): pass
class tbody(Tag): pass
class tr(Tag): pass
class th(Tag): pass
class td(Tag): pass
class caption(Tag): pass
class blockquote(Tag): pass
class cite(Tag): pass
class q(Tag): pass
class abbr(Tag): pass
class acronym(Tag): pass
class address(Tag): pass


class meta(SelfClosingTag): pass
class link(SelfClosingTag): pass
class br(SelfClosingTag): pass
class hr(SelfClosingTag): pass
class input(SelfClosingTag): pass


class code(WhitespaceSensitiveTag): pass
class samp(WhitespaceSensitiveTag): pass
class pre(WhitespaceSensitiveTag): pass
class var(WhitespaceSensitiveTag): pass
class kbd(WhitespaceSensitiveTag): pass
class dfn(WhitespaceSensitiveTag): pass


class html(Tag):
    doctype = '<!DOCTYPE html>'
