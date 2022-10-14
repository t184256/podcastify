# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import feedgen.ext.base
from feedgen.util import xml_elem


class SimpleChaptersExtension(feedgen.ext.base.BaseExtension):
    PSC_NS = 'http://podlove.org/simple-chapters'

    @classmethod
    def extend_ns(cls):
        return {'psc': cls.PSC_NS}


class SimpleChaptersEntryExtension(feedgen.ext.base.BaseEntryExtension):
    PSC_NS = 'http://podlove.org/simple-chapters'

    def __init__(self):
        self.__psc_chapters = []

    def add(self, start, title):  # link and url not implementend
        self.__psc_chapters.append({'start': start, 'title': title})

    def extend_rss(self, entry):
        if self.__psc_chapters:
            chapters = xml_elem(f'{{{self.PSC_NS}}}chapters', entry)
            for e in self.__psc_chapters:
                chapter = xml_elem(f'{{{self.PSC_NS}}}chapter', chapters)
                for k, v in e.items():
                    chapter.attrib[k] = str(v)
        return entry
