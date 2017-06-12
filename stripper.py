import re
import string
import six

import gensim


class WikiStripper(object):
    """Generic wikipedia articles stripper

    Strips off illegal characters and markups.
    """

    def __init__(self, valid_unicodes=(), invalid_unicodes=(),
                 preserve_lists=False):
        """
        Arguments:
            valid_unicodes: List of valid unicode ranges. Must be
                provided with tuples denoting left and right limits in integer
                (inclusive). Invalid unicodes take precedence over valid ones.
            invalid_unicodes: List of invalid unicode ranges. Must be
                provided with tuples denoting left and right limits in integer
                (inclusive). Invalid unicodes take precedence over valid ones.
            perserve_lists: Boolean. Indicates whether to preserve text in
                list markups (order, unordered etc.)
        """
        self.valid_unicodes = valid_unicodes
        self.invalid_unicodes = invalid_unicodes
        self.preserve_lists = preserve_lists
        self.uni_patterns = []
        self.xml_removal_patterns = [
            re.compile(r"<\!\-\-((?!\-\-\>).)*\-\-\>", re.DOTALL), # html comments
            re.compile(r"(<\w+[^>]*/>)", re.DOTALL), # uni tags
            re.compile(r"(<(?P<tag>\w+)[^>]*>((?!</?\w+[^>]*>).)*<\/(?P=tag)[^>]*>)", re.DOTALL) # bounded tags
        ]
        self.markup_removal_patterns = [
            re.compile(r"^\-\-+$", re.MULTILINE),
            re.compile(r"\([^\(\)]*\)"),
            re.compile(r"\[[^\[\]]*\]"),
            re.compile(r"\{[^\{\}]*\}"),
            re.compile(r"\:\{[^\{\}]*\}"),
            re.compile(r"^\# ?REDIRECT.*$", re.MULTILINE),
            re.compile(r"^;.*$", re.MULTILINE),
            re.compile(r"(?P<tag>\=+)((?!(?P=tag)).)*(?P=tag)"),
        ]
        self.replace_patterns = [
            re.compile(r"\[\[\:?(\w+\:)?(\w+\:)?(?P<text>((?!\]\])[^=\|])+)(\#[^\|]+)?\]\]"), # free links
            re.compile(r"\[\[[^\|]+\|(?P<text>((?!\]\])[^=\|])+)\|?\]\]"), # renamed links with pipe tricks
            re.compile(r"\[[^\|\s]+ (?P<text>[^=\[\]\|]+)\]"), # external links
            re.compile(r"'''(?P<text>((?!''').)+)'''"),
            re.compile(r"''(?P<text>((?!'').)+)''"),
        ]

        list_patterns = [
            re.compile(r"^(\:+|\#+|\*+)(?P<text>.*)$", re.MULTILINE),
        ]

        if preserve_lists:
            self.replace_patterns.extend(list_patterns)
        else:
            self.markup_removal_patterns.extend(list_patterns)

        if valid_unicodes:
            valids = []
            for s, e in valid_unicodes:
                s_str = six.unichr(s)
                e_str = six.unichr(e)
                valids.append("{}-{}".format(s_str, e_str))

            valid_pat = re.compile(r"[^{}]".format("".join(valids)),
                                   re.UNICODE)
            self.uni_patterns.append(valid_pat)

        if invalid_unicodes:
            invalids = []
            for s, e in invalid_unicodes:
                s_str = six.unichr(s)
                e_str = six.unichr(e)

                invalids.append("{}-{}".format(s_str, e_str))

            invalid_pat = re.compile(r"[{}]".format("".join(invalids)),
                                     re.UNICODE)
            self.uni_patterns.append(invalid_pat)

        dbws_pat = re.compile(r"(\s)\s*")

        self.dbws_pattern = dbws_pat

    def _remove_markup(self, text):
        while True:
            _text = text

            for pat in self.xml_removal_patterns:
                text = pat.sub("", text)
            
            if text == _text:
                break

        while True:
            _text = text
        
            for pat in self.replace_patterns:
                text = pat.sub(r"\g<text>", text)

            for pat in self.markup_removal_patterns:
                text = pat.sub("", text)

            if text == _text:
                break

        return text

    def __call__(self, text):
        text = gensim.utils.to_unicode(text, "utf8", errors="ignore")
        text = gensim.utils.decode_htmlentities(text)

        text = self._remove_markup(text)

        for pat in self.uni_patterns:
            text = pat.sub("", text)

        text = self.dbws_pattern.sub(r"\g<1>", text)

        return text
