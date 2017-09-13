"""
Script for uploading data from a local sqlite file to the web server.
"""

import sys
import json
import argparse
from openmdao.api import WebRecorder
from openmdao.recorders.sqlite_reader import SqliteCaseReader

def upload(sqlite_file, token, name=None, case_id=None, suppress_output=False):
    """
    Upload sqlite recording to the web server.

    Parameters
    ----------
    sqlite_file : str
        The location of the sqlite file.
    token : str
        The web recorder token.
    name : str
        The name of the recording (defaults to None).
    case_id : str
        The case_id if this upload is intended to update a recording.
    suppress_output : bool
        Indicates whether or not the upload status should be printed.
    """
    reader = SqliteCaseReader(sqlite_file)
    recorder = WebRecorder(token, name)

    if not suppress_output:
        print('Data Uploader: Recording driver iteration data')
    _upload_driver_iterations(reader.driver_cases, recorder)

    if not suppress_output:
        print('Data Uploader: Recording system iteration data')
    _upload_system_iterations(reader.system_cases, recorder)

    if not suppress_output:
        print('Data Uploader: Recording solver iteration data')
    _upload_solver_iterations(reader.solver_cases, recorder)

    recorder._record_driver_metadata('Driver', json.dumps(reader.driver_metadata))
    for item in reader.solver_metadata:
        recorder._record_solver_metadata(reader.solver_metadata[item]['solver_options'],
            reader.solver_metadata[item]['solver_class'], '')

    if not suppress_output:
        print('Finished uploading')

def _upload_system_iterations(new_list, recorder):
    """
    Upload all system iterations to the web server.

    Parameters
    ----------
    new_list : [SystemCase]
        The list of system case data from the reader.
    recorder : WebRecorder
        The web recorder used to upload this data.
    """
    case_keys = new_list.list_cases()
    for case_key in case_keys:
        data = new_list.get_case(case_key)
        inputs = []
        outputs = []
        residuals = []
        if data.inputs != None:
            for n in data.inputs.dtype.names:
                inputs.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.inputs[n])
                })
        if data.outputs != None:
            for n in data.outputs.dtype.names:
                outputs.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.outputs[n])
                })
        if data.residuals != None:
            for n in data.residuals.dtype.names:
                residuals.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.residuals[n])
                })

        data.inputs = inputs
        data.outputs = outputs
        data.residuals = residuals
        recorder._record_system_iteration(data.counter, data.iteration_coordinate,
            data.success, data.msg, data.inputs, data.outputs, data.residuals)

def _upload_solver_iterations(new_list, recorder):
    """
    Upload all slver iterations to the web server.

    Parameters
    ----------
    new_list : [SolverCase]
        The list of solver case data from the reader.
    recorder : WebRecorder
        The web recorder used to upload this data.
    """
    case_keys = new_list.list_cases()
    for case_key in case_keys:
        data = new_list.get_case(case_key)
        outputs = []
        residuals = []
        if data.outputs != None:
            for n in data.outputs.dtype.names:
                outputs.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.outputs[n])
                })
        if data.residuals != None:
            for n in data.residuals.dtype.names:
                residuals.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.residuals[n])
                })

        data.outputs = outputs
        data.residuals = residuals
        recorder._record_solver_iteration(data.counter, data.iteration_coordinate,
            data.success, data.msg, data.abs_err, data.rel_err, data.outputs,
            data.residuals)

def _upload_driver_iterations(new_list, recorder):
    """
    Upload all driver iterations to the web server.

    Parameters
    ----------
    new_list : [DriverCase]
        The list of driver case data from the reader.
    recorder : WebRecorder
        The web recorder used to upload this data.
    """
    case_keys = new_list.list_cases()
    for case_key in case_keys:
        data = new_list.get_case(case_key)
        desvars = []
        responses = []
        objectives = []
        constraints = []
        if data.desvars != None:
            for n in data.desvars.dtype.names:
                desvars.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.desvars[n])
                })
        if data.responses != None:
            for n in data.responses.dtype.names:
                responses.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.responses[n])
                })
        if data.objectives != None:
            for n in data.objectives.dtype.names:
                objectives.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.objectives[n])
                })
        if data.constraints != None:
            for n in data.constraints.dtype.names:
                constraints.append({
                    'name': n,
                    'values': recorder.convert_to_list(data.constraints[n])
                })

        data.desvars = desvars
        data.responses = responses
        data.objectives = objectives
        data.constraints = constraints
        recorder._record_driver_iteration(data.counter, data.iteration_coordinate,
            data.success, data.msg, data.desvars, data.responses,
            data.objectives, data.constraints)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sqlite_file", help="the location of the sqlite file whose data\
                        needs to be uploaded", type=str)
    parser.add_argument("token", help="the web server token used for the web recorder",
                        type=str)
    parser.add_argument("-n", "--name", help="the name to give to this recording", type=str)
    parser.add_argument("-c", "--case_id", help="the case ID if you want to update an existing \
                        recording")
    args = parser.parse_args()

    upload(args.sqlite_file, args.token, args.name, args.case_id)
