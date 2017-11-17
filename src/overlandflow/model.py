import numpy as np
import scipy

from .raster_model import RasterModel
from .rainstorm import RainStepFunction
from .mannings import DepthDependentManningsN

from landlab.components import (OverlandFlow, SoilInfiltrationGreenAmpt,
                                FlowDirectorSteepest,
                                DepressionFinderAndRouter, FlowAccumulator)
from landlab.utils.depth_dependent_roughness import depth_dependent_mannings_n
from landlab import FIXED_VALUE_BOUNDARY


class OverlandFlowModel(RasterModel):

    DEFAULT_PARAMS = {
        'grid': {
            '_type': 'raster',
            'from_file': 'square_test_basin.asc',
        },
        'fields': {
            'at_node': [('soil_water_infiltration__depth', .001)],
            'at_link': [('mannings_n', 0.055)],
        },
        'clock': {
            'start': 0.,
            'stop': 100.,
            'step': 2.,
        },
        'overland_flow': {
            'h_init': 0.00001,
            'alpha': 0.7,
            'mannings_n': 0.03,
            'g': scipy.constants.g,
            'theta': 0.8,
            'rainfall_intensity': 0.0,
            'steep_slopes': False,
        },
        'soil_infiltration_green_ampt': {
            'hydraulic_conductivity': 0.005,
            'soil_bulk_density': 1590.,
            'rock_density': 2650.,
        },
        'rain_step_function': {
            'start': 3600.,
            'duration': 3600.,
            'magnitude': 60. * 1e-3 / (60. * 60.),
        },
        'depth_dependent_mannings_n': {
            'min_mannings_n': 0.06,
            'index_flow_depth': 0.003,
            'veg_drag_exponent': -1. / 3.,
        },
    }


    LONG_NAME = {
        'dz': 'surface_water__depth',
        'infiltration_depth': 'soil_water_infiltration__depth',
        'q': 'surface_water__discharge',
    }

    def __init__(self, grid=None, clock=None, fields=None,
                 overland_flow=None, soil_infiltration_green_ampt=None,
                 rain_step_function=None, depth_dependent_mannings_n=None):
        super(OverlandFlowModel, self).__init__(grid=grid, clock=clock,
                                                fields=fields)

        self.grid.status_at_node[:256] = FIXED_VALUE_BOUNDARY
        self.grid.status_at_node[-256:] = FIXED_VALUE_BOUNDARY

        self.overland_flow = OverlandFlow(self.grid, **overland_flow or {})
        self.soil_infiltration_green_ampt = SoilInfiltrationGreenAmpt(
            self.grid, **soil_infiltration_green_ampt or {})
        self.rain_step_function = RainStepFunction(
            self.grid, **rain_step_function or {})
        self.manning_n = DepthDependentManningsN(
            self.grid, **depth_dependent_mannings_n or {})

        FlowAccumulator(
            self.grid, 'topographic__elevation',
            flow_director=FlowDirectorSteepest,
            depression_finder=DepressionFinderAndRouter).run_one_step()

        self.components = (
            self.rain_step_function,
            self.manning_n,
            self.overland_flow,
            self.soil_infiltration_green_ampt,
        )

    def advance_components(self, duration):
        now = self.clock.time
        stop = now + duration
        while now < stop:
            dt = self.overland_flow.calc_time_step()
            if now + dt > stop:
                dt = stop - now

            self.rain_step_function.run_one_step(dt=dt)

            self.overland_flow.rainfall_intensity = self.grid.at_grid['rain_rate']

            self.manning_n.run_one_step()

            # Updating the field of Manning's n for the OverlandFlow calculation.
            self.grid.at_link['mannings_n'] = self.grid.map_min_of_link_nodes_to_link('mannings_n')

            self.overland_flow.run_one_step(dt=dt)
            self.soil_infiltration_green_ampt.run_one_step(dt=dt)

            now += dt


if __name__ == '__main__':
    OverlandFlowModel.main()
