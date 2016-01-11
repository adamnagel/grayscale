from openmdao.core.component import Component
import json
from flask import Flask
import time


class TestThing(Component):
    def __init__(self):
        super(TestThing, self).__init__()

        self.add_param('Param1', val=0.5, units='m')
        self.add_output('Output1', val=0.0)

    def solve_nonlinear(self, params, unknowns, resids):
        #time.sleep(0.5)
        unknowns['Output1'] = params['Param1']


app = Flask(__name__)
components = dict()
interface_descriptions = dict()


@app.route('/list_components')
def list_components():
    return json.dumps(interface_descriptions)


@app.route('/<component_id>/interface')
def interface(component_id):
    return json.dumps(interface_descriptions[component_id])


@app.route('/<component_id>/solve_nonlinear/<submission_data>')
def solve_nonlinear(component_id, submission_data):
    start_time = time.time()

    params = json.loads(str(submission_data))
    unknowns = dict()
    thecomponent = components[component_id]
    thecomponent.solve_nonlinear(params, unknowns, dict())

    elapsed_time = time.time() - start_time

    return json.dumps({'unknowns': unknowns, 'metadata': {'execution_time': elapsed_time}})


def Add(component, component_id):
    ipd = component._init_params_dict
    iud = component._init_unknowns_dict
    interface_description = {'Parameters': dict(), 'Unknowns': dict()}
    for k, v in ipd.iteritems():
        interface_description['Parameters']['k'] = v

    for k, v in iud.iteritems():
        interface_description['Unknowns']['k'] = v

    interface_descriptions[component_id] = interface_description
    components[component_id] = component


if __name__ == '__main__':
    c = TestThing()
    Add(c, 'test_thing')

    app.run()
