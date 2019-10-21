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

import openmdao.api as om
from numpy.testing import assert_allclose

from fastoad.modules.performances.breguet import Breguet
from tests.testing_utilities import run_system


def test_breguet():
    # test 1
    ivc = om.IndepVarComp()
    ivc.add_output('altitude', 35000, units='ft')
    ivc.add_output('mach', 0.78)
    ivc.add_output('flight_distance', 500, units='NM')
    ivc.add_output('lift_to_drag_ratio', 16.)
    ivc.add_output('SFC', 1e-5, units='kg/N/s')
    ivc.add_output('MTOW', 74000, units='kg')

    problem = run_system(Breguet(), ivc)

    assert_allclose(problem['MZFW'], 65617., rtol=1e-3)
    assert_allclose(problem['fuel_weight'], 8382., rtol=1e-3)

    # test 2 in combination with an OpenMDAO engine model
    ivc = om.IndepVarComp()
    ivc.add_output('altitude', 35000, units='ft')
    ivc.add_output('mach', 0.78)
    ivc.add_output('flight_distance', 1500, units='NM')
    ivc.add_output('lift_to_drag_ratio', 16.)
    ivc.add_output('SFC', 1e-5, units='kg/N/s')
    ivc.add_output('MTOW', 74000, units='kg')
    ivc.add_output('phase', 3)

    problem = run_system(Breguet(), ivc)

    assert_allclose(problem['MZFW'], 62473., rtol=1e-3)
    assert_allclose(problem['fuel_weight'], 11526., rtol=1e-3)
