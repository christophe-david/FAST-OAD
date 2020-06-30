#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA & ISAE-SUPAERO
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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from fastoad.constants import FlightPhase
from fastoad.models.performances.mission.flight import Flight
from fastoad.models.performances.mission.flight_point import FlightPoint
from fastoad.models.performances.mission.polar import Polar
from fastoad.models.propulsion import EngineSet
from fastoad.models.propulsion.fuel_propulsion.rubber_engine import RubberEngine
from scipy.constants import knot, foot


def print_dataframe(df):
    """Utility for correctly printing results"""
    # Not used if all goes all well. Please keep it for future test setting/debugging.
    with pd.option_context(
        "display.max_rows", 20, "display.max_columns", None, "display.width", None
    ):
        print()
        print(df)


@pytest.fixture
def high_speed_polar() -> Polar:
    """Returns a dummy polar where max L/D ratio is about 16., around CL=0.5"""
    cl = np.arange(0.0, 1.5, 0.01)
    cd = 0.6e-1 * cl ** 2 + 0.016
    return Polar(cl, cd)


@pytest.fixture
def low_speed_polar() -> Polar:
    """Returns a dummy polar where max L/D ratio is around CL=0.5"""
    cl = np.arange(0.0, 2.0, 0.01)
    cd = 0.6e-1 * cl ** 2 + 0.03
    return Polar(cl, cd)


def test_flight(low_speed_polar, high_speed_polar):

    engine = RubberEngine(5.0, 30.0, 1500.0, 1.0e5, 0.95, 10000.0)
    propulsion = EngineSet(engine, 2)

    flight_calculator = Flight(
        propulsion=propulsion,
        reference_surface=120.0,
        low_speed_polar=low_speed_polar,
        high_speed_polar=high_speed_polar,
        cruise_mach=0.78,
        thrust_rates={FlightPhase.TAKEOFF: 1.0, FlightPhase.CLIMB: 0.93, FlightPhase.DESCENT: 0.4},
        cruise_distance=3.0e5,
    )

    flight_points = flight_calculator.compute(
        FlightPoint(true_airspeed=150.0 * knot, altitude=100.0 * foot, mass=70000.0),
    )

    print_dataframe(flight_points)

    plt.plot(flight_points.time, flight_points.altitude)
    plt.show()
