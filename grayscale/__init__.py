'''
curl http://localhost:5000/example2/interface
curl --data '{"Param1": 1, "a_string": "x"}' -H 'Content-Type:application/json;charset=UTF-8' http://localhost:5000/example2/solve_nonlinear
'''

from openmdao.core.component import Component
import json
from flask import Flask, request
import time


class TestThing(Component):
    def __init__(self):
        super(TestThing, self).__init__()

        self.add_param('Param1', val=0.5, units='m')
        self.add_param('a_string', val='default', pass_by_obj=True)
        self.add_output('Output1', val=0.0)
        self.add_output('a_string_twice', val='', pass_by_obj=True)

    def solve_nonlinear(self, params, unknowns, resids):
        time.sleep(0.5)
        unknowns['Output1'] = params['Param1'] + 2
        unknowns['a_string_twice'] = params['a_string'] * 2


class OriginalTestThing(Component):
    def __init__(self):
        super(OriginalTestThing, self).__init__()

        self.add_param('Param1', val=0.5, units='m')
        self.add_output('Output1', val=0.0)

    def solve_nonlinear(self, params, unknowns, resids):
        time.sleep(0.5)
        unknowns['Output1'] = params['Param1']


app = Flask(__name__)
components = dict()
interface_descriptions = dict()


@app.route('/list_components')
def list_components():
    return json.dumps(interface_descriptions)


@app.route('/<component_id>/interface')
def interface(component_id):
    description = interface_descriptions.get(component_id)
    if description is None:
        return '{} is not known'.format(component_id), 404
    return json.dumps(interface_descriptions)


@app.route('/<component_id>/solve_nonlinear/<submission_data>')
def solve_nonlinear(component_id, submission_data):
    params = json.loads(str(submission_data))
    start_time = time.time()
    unknowns = dict()
    thecomponent = components[component_id]
    thecomponent.solve_nonlinear(params, unknowns, dict())

    elapsed_time = time.time() - start_time

    return json.dumps({'unknowns': unknowns, 'metadata': {'execution_time': elapsed_time}})


@app.route('/<component_id>/solve_nonlinear', methods=['POST'])
def solve_nonlinear_post(component_id):
    params = request.get_json()
    start_time = time.time()
    unknowns = dict()
    thecomponent = components.get(component_id)
    if thecomponent is None:
        return '{} is not known'.format(component_id), 404
    thecomponent.solve_nonlinear(params, unknowns, dict())

    elapsed_time = time.time() - start_time

    return json.dumps({'unknowns': unknowns, 'metadata': {'execution_time': elapsed_time}})


def Add(component, component_id):
    ipd = component._init_params_dict
    iud = component._init_unknowns_dict
    interface_description = {'Parameters': dict(), 'Unknowns': dict()}
    for k, v in ipd.iteritems():
        interface_description['Parameters'][k] = v

    for k, v in iud.iteritems():
        interface_description['Unknowns'][k] = v

    interface_descriptions[component_id] = interface_description
    components[component_id] = component


if __name__ == '__main__':
    Add(TestThing(), 'example2')
    Add(OriginalTestThing(), 'example1')

    # app.run(debug=True)
    app.run()
