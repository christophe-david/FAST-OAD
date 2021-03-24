"""
Test module for configuration.py
"""
#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2021 ONERA & ISAE-SUPAERO
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

import os
import os.path as pth
import shutil
from shutil import rmtree

import openmdao.api as om
import pytest
import tomlkit

from fastoad.io.configuration.configuration import (
    FASTOADProblemConfigurator,
    KEY_INPUT_FILE,
    KEY_OUTPUT_FILE,
    TABLE_MODEL,
)
from ..exceptions import (
    FASTConfigurationBadOpenMDAOInstructionError,
    FASTConfigurationError,
    FASTConfigurationNanInInputFile,
)

DATA_FOLDER_PATH = pth.join(pth.dirname(__file__), "data")
RESULTS_FOLDER_PATH = pth.join(pth.dirname(__file__), "results")


@pytest.fixture(scope="module")
def cleanup():
    rmtree(RESULTS_FOLDER_PATH, ignore_errors=True)


def test_problem_definition(cleanup):
    """ Test conf definition from configuration files """

    # no input file
    conf = FASTOADProblemConfigurator()
    with pytest.raises(FASTConfigurationError) as exc_info:
        conf.load(pth.join(DATA_FOLDER_PATH, "missing_input_file.toml"))
    assert exc_info.value.missing_key == KEY_INPUT_FILE

    # no output file
    conf = FASTOADProblemConfigurator()
    with pytest.raises(FASTConfigurationError) as exc_info:
        conf.load(pth.join(DATA_FOLDER_PATH, "missing_output_file.toml"))
    assert exc_info.value.missing_key == KEY_OUTPUT_FILE

    # Missing model definition
    conf = FASTOADProblemConfigurator()
    with pytest.raises(FASTConfigurationError) as exc_info:
        conf.load(pth.join(DATA_FOLDER_PATH, "missing_model.toml"))
    assert exc_info.value.missing_section == TABLE_MODEL

    # Incorrect attribute
    conf = FASTOADProblemConfigurator()
    conf.load(pth.join(DATA_FOLDER_PATH, "invalid_attribute.toml"))
    with pytest.raises(FASTConfigurationBadOpenMDAOInstructionError) as exc_info:
        problem = conf.get_problem(read_inputs=False)
    assert exc_info.value.key == "model.cycle.other_group.nonlinear_solver"

    # Reading of a minimal conf (model = ExplicitComponent)
    conf = FASTOADProblemConfigurator()
    conf.load(pth.join(DATA_FOLDER_PATH, "disc1.toml"))
    problem = conf.get_problem(read_inputs=False)
    assert isinstance(problem.model.system, om.ExplicitComponent)

    # Reading of correct conf definition
    conf = FASTOADProblemConfigurator()
    conf.load(pth.join(DATA_FOLDER_PATH, "valid_sellar.toml"))
    assert conf.input_file_path == pth.join(RESULTS_FOLDER_PATH, "inputs.xml")
    assert conf.output_file_path == pth.join(RESULTS_FOLDER_PATH, "outputs.xml")


def test_problem_definition_with_xml_ref(cleanup):
    """ Tests what happens when writing inputs using data from existing XML file"""
    conf = FASTOADProblemConfigurator(pth.join(DATA_FOLDER_PATH, "valid_sellar.toml"))

    result_folder_path = pth.join(RESULTS_FOLDER_PATH, "problem_definition_with_xml_ref")
    conf.input_file_path = pth.join(result_folder_path, "inputs.xml")
    conf.output_file_path = pth.join(result_folder_path, "outputs.xml")

    input_data = pth.join(DATA_FOLDER_PATH, "ref_inputs.xml")
    conf.write_needed_inputs(input_data)

    problem = conf.get_problem(read_inputs=True, auto_scaling=True)
    # runs evaluation without optimization loop to check that inputs are taken into account
    problem.setup()
    problem.run_model()

    assert problem["f"] == pytest.approx(28.58830817, abs=1e-6)
    problem.write_outputs()


def test_problem_definition_with_custom_xml(cleanup):
    """ Tests what happens when writing inputs using existing XML with some unwanted var"""
    conf = FASTOADProblemConfigurator(pth.join(DATA_FOLDER_PATH, "valid_sellar.toml"))

    result_folder_path = pth.join(RESULTS_FOLDER_PATH, "problem_definition_with_custom_xml")
    conf.input_file_path = pth.join(result_folder_path, "inputs.xml")
    conf.output_file_path = pth.join(result_folder_path, "outputs.xml")

    input_data = pth.join(DATA_FOLDER_PATH, "ref_inputs.xml")
    os.makedirs(result_folder_path, exist_ok=True)
    shutil.copy(input_data, conf.input_file_path)

    problem = conf.get_problem(read_inputs=True, auto_scaling=True)
    problem.setup()
    problem.run_model()

    assert problem["f"] == pytest.approx(28.58830817, abs=1e-6)
    problem.write_outputs()


def test_problem_definition_with_nan_inputs(cleanup):
    """ Tests what happens when writing inputs using existing XML with some unwanted var"""
    conf = FASTOADProblemConfigurator(pth.join(DATA_FOLDER_PATH, "valid_sellar.toml"))

    input_data_path = pth.join(DATA_FOLDER_PATH, "nan_inputs.xml")
    os.makedirs(RESULTS_FOLDER_PATH, exist_ok=True)
    shutil.copy(input_data_path, conf.input_file_path)

    with pytest.raises(FASTConfigurationNanInInputFile) as exc:
        problem = conf.get_problem(read_inputs=True, auto_scaling=True)
        assert exc.input_file_path == input_data_path
        assert exc.nan_variable_names == ["x"]


def test_problem_definition_with_xml_ref_run_optim(cleanup):
    """
    Tests what happens when writing inputs using data from existing XML file
    and running an optimization problem
    """
    conf = FASTOADProblemConfigurator(pth.join(DATA_FOLDER_PATH, "valid_sellar.toml"))

    result_folder_path = pth.join(RESULTS_FOLDER_PATH, "problem_definition_with_xml_ref_run_optim")
    conf.input_file_path = pth.join(result_folder_path, "inputs.xml")

    input_data = pth.join(DATA_FOLDER_PATH, "ref_inputs.xml")
    conf.write_needed_inputs(input_data)

    # Runs optimization problem with semi-analytic FD
    problem1 = conf.get_problem(read_inputs=True)
    problem1.setup()
    problem1.run_model()
    assert problem1["f"] == pytest.approx(28.58830817, abs=1e-6)
    problem1.run_driver()
    assert problem1["f"] == pytest.approx(3.18339395, abs=1e-6)
    problem1.output_file_path = pth.join(result_folder_path, "outputs_1.xml")
    problem1.write_outputs()

    # Runs optimization problem with monolithic FD
    problem2 = conf.get_problem(read_inputs=True)
    problem2.model.approx_totals()
    problem2.setup()
    problem2.run_model()  # checks problem has been reset
    assert problem2["f"] == pytest.approx(28.58830817, abs=1e-6)
    problem2.run_driver()
    assert problem2["f"] == pytest.approx(3.18339395, abs=1e-6)
    problem2.output_file_path = pth.join(result_folder_path, "outputs_2.xml")
    problem2.write_outputs()


def test_set_optimization_definition(cleanup):
    """
    Tests the modification of the optimization definition in the .toml
    configuration file
    """
    reference_file = pth.join(DATA_FOLDER_PATH, "valid_sellar.toml")
    editable_file = pth.join(RESULTS_FOLDER_PATH, "editable_valid_sellar.toml")

    # copy(reference_file, editable_file)

    conf = FASTOADProblemConfigurator(reference_file)

    optimization_def = {
        "design_var": {
            "x": {"name": "x", "lower": 0, "upper": 20},
            "z": {"name": "z", "lower": 0, "upper": 10},
        },
        "constraint": {"gg1": {"name": "gg1", "upper": 10}, "gg2": {"name": "gg2", "upper": 0},},
        "objective": {"f": {"name": "f"}},
    }

    optimization_conf = {
        "design_var": [
            {"name": "x", "lower": 0, "upper": 20},
            {"name": "z", "lower": 0, "upper": 10},
        ],
        "constraint": [{"name": "gg1", "upper": 10}, {"name": "gg2", "upper": 0}],
        "objective": [{"name": "f"}],
    }

    with open(reference_file, "r") as file:
        d = file.read()
        conf_dict = tomlkit.loads(d)
    conf_dict_opt = conf_dict["optimization"]
    # Should be different
    assert optimization_conf != conf_dict_opt

    conf.set_optimization_definition(optimization_def)
    conf.save(editable_file)
    with open(editable_file, "r") as file:
        d = file.read()
        conf_dict = tomlkit.loads(d)
    conf_dict_opt = conf_dict["optimization"]
    # Should be equal
    assert optimization_conf == conf_dict_opt
