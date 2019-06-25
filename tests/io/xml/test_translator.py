"""
Test module for translator.py
"""
#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2019  ONERA/ISAE
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

import pytest

from fastoad.io.xml.translator import VarXpathTranslator


def test_translator():
    """ Tests all methods of VarXpathTranslator"""
    translator = VarXpathTranslator()
    indices = range(10)
    var_list = ['var%i' % i for i in indices]
    xpath_list = ['xpath%i' % i for i in indices]

    # test with lists of different lengths -> error
    var_list2 = ['var0'] + var_list
    with pytest.raises(IndexError) as exc_info:
        translator.set(var_list2, xpath_list)
    assert exc_info is not None

    # Filling correct lists
    translator.set(var_list, xpath_list)

    assert translator.variable_names == var_list
    assert translator.xpaths == xpath_list

    for i in indices:
        assert translator.get_xpath('var%i' % i) == 'xpath%i' % i
        assert translator.get_variable_name('xpath%i' % i) == 'var%i' % i

    with pytest.raises(ValueError) as exc_info:
        _ = translator.get_xpath('unknown_var')
    assert exc_info is not None

    with pytest.raises(ValueError) as exc_info:
        _ = translator.get_variable_name('unknown_path')
    assert exc_info is not None
