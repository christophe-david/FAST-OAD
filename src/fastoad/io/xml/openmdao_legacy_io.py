"""
Readers for legacy XML format
"""
#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA/ISAE
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from importlib_resources import open_text

from fastoad.io.xml import OMCustomXmlIO
from fastoad.io.xml.translator import VarXpathTranslator
from . import resources

CONVERSION_FILENAME_1 = 'legacy1.txt'


class OMLegacy1XmlIO(OMCustomXmlIO):
    """
    Reader for legacy XML format (version "1")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        translator = VarXpathTranslator()

        with open_text(resources, CONVERSION_FILENAME_1) as translation_table:
            translator.read_translation_table(translation_table)

        self.xml_unit_attribute = 'unit'
        self.set_translator(translator)
