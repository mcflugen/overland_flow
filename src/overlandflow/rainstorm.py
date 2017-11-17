from matplotlib.pyplot import figure, show
from numpy import arange, sin, pi
from scipy import interpolate
import matplotlib.pyplot as plt

import numpy as np
from scipy.interpolate import interp1d
from landlab import RasterModelGrid, Component


def smooth_heaviside(x, out=None, k=.5):
    old_settings = np.seterr(over='ignore')
    try:
        return np.divide(1., (1. + np.exp( -2. * k * np.asarray(x))), out=out)
    except Exception:
        raise
    finally:
        np.seterr(**old_settings)


def smooth_boxcar(x, start=-.5, stop=.5, k=.5, out=None):
    x = np.asarray(x)
    return np.subtract(smooth_heaviside(x - start, k=k),
                       smooth_heaviside(x - stop, k=k), out=out)


class RainTimeSeries(Component):

    _name = 'Rain Storm'

    _time_units = 's'

    _input_var_names = ()

    _output_var_names = (
        'rain_rate',
    )

    _var_units = {
        'rain_rate': 'm / s',
    }

    _var_mapping = {
        'rain_rate': 'grid',
    }

    _var_doc = {
        'rain_rate': 'Rain rate',
    }

    def __init__(self, grid, filepath, kind='linear', **kwds):
        """Generate sea level values.

        Parameters
        ----------
        grid: ModelGrid
            A landlab grid.
        filepath: str
            Name of csv-formatted sea-level file.
        kind: str, optional
            Kind of interpolation as a string (one of 'linear',
            'nearest', 'zero', 'slinear', 'quadratic', 'cubic').
            Default is 'linear'.
        """
        super(RainTimeSeries, self).__init__(grid, **kwds)

        data = np.loadtxt(filepath, delimiter=',')
        self._rain_rate = interp1d(data[:, 0], data[:, 1], kind=kind,
                                   copy=True, assume_sorted=True,
                                   bounds_error=True)

        self._time = start

    @property
    def time(self):
        return self._time

    def run_one_step(self, dt):
        self._time += dt
        self.grid.at_grid['rain_rate'] = self._rain_rate(self.time)


class RainStepFunction(RainTimeSeries):

    def __init__(self, grid, start=0., duration=1., magnitude=1., **kwds):
        """Generate rain rate values using a step function.

        Parameters
        ----------
        grid: ModelGrid
            A landlab grid.
        start : float
            Start of the rain storm.
        duration : float, optional
            Length of the storm.
        magnitude : float, optional
            Magnitude of the storm.
        """
        Component.__init__(self, grid, **kwds)

        self._rain_rate = lambda time: (magnitude *
                                        smooth_boxcar(time, start=start,
                                                      stop=start + duration))

        # self._rain_rate = lambda time: .5 * magnitude * (
        #     smooth_heaviside(time - start) +
        #     smooth_heaviside( - (time - (duration + start))))

        self._time = 0.
