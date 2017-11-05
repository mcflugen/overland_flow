from landlab import Component


def depth_dependent_mannings_n(water_depth, min_mannings_n=0.06,
                               index_flow_depth=0.003,
                               veg_drag_exponent=(-1./3.), out=None):
    """Calculate Mannings N based on water depth.

    Calculate the Manning N parameter spatially with values based on
    water depths.

    Parameters
    ----------
    water_depth : ndarray of float
        Array of water depth values (m).
    min_mannings_n : float
        Minimum Manning's n coefficient for a given landscape,
        following Chow, 1959. (s m^(-1./3.))
    index_flow_depth : float
        Flow depth above which it is assumed that Manning's n is
        constant. (m)
    veg_drag_exponent : float
        Exponent related to vegetation drag effects, which increases
        effective Manning's n at low flow conditions.
    """
    if out is None:
        out = np.empty_like(water_depth)
    out.fill(min_mannings_n)

    is_below_threshold = water_depth <= index_flow_depth
    out[is_below_threshold] *= (water_depth[is_below_threshold] /
                                index_flow_depth) ** veg_drag_exponent

    return out


class DepthDependentManningsN(Component):

    _name = 'Depth-dependent Manning N parameter'

    _input_var_names = (
        'surface_water__depth',
    )

    _output_var_names = (
        'mannings_n',
    )

    _time_units = ''

    _var_units = {
        'surface_water__depth': 'm',
        'mannings_n': 'm^(-1/3) s',
    }

    _var_mapping = {
        'surface_water__depth': 'node',
        'mannings_n': 'node',
    }

    _var_doc = {
        'surface_water__depth': 'Water depth',
        'mannings_n': 'Manning N parameter',
    }

    def __init__(self, grid, min_mannings_n=0.06, index_flow_depth=0.003,
                 veg_drag_exponent=- 1. / 3., **kwds):

        super(DepthDependentManningsN, self).__init__(grid, **kwds)

        self._min_mannings_n = min_mannings_n
        self._index_flow_depth = index_flow_depth
        self._veg_drag_exponent = veg_drag_exponent

        if 'mannings_n' not in self.grid.at_node:
            self.grid.add_empty('mannings_n', at='node')

    @property
    def min_mannings_n(self):
        return self._min_mannings_n

    @property
    def index_flow_depth(self):
        return self._index_flow_depth

    @property
    def veg_drag_exponent(self):
        return self._veg_drag_exponent

    def run_one_step(self, dt=None):
        water_depth = self.grid.at_node['surface_water__depth']
        manning_n = self.grid.at_node['mannings_n']

        depth_dependent_mannings_n(
            water_depth, min_mannings_n=self.min_mannings_n,
            index_flow_depth=self.index_flow_depth,
            veg_drag_exponent=self.veg_drag_exponent, out=manning_n)
