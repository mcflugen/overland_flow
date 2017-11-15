#! /usr/bin/env python
import argparse
import re

import yaml

from landlab import RasterModelGrid, CLOSED_BOUNDARY
from landlab.core import load_params
from landlab.plot import imshow_grid
from landlab.io.netcdf import write_raster_netcdf
from landlab.bmi.bmi_bridge import TimeStepper


yaml.add_implicit_resolver(
    u'tag:yaml.org,2002:float',
    re.compile(u'''^(?:
     [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
    |[-+]?\\.(?:inf|Inf|INF)
    |\\.(?:nan|NaN|NAN))$''', re.X),
    list(u'-+0123456789.'))


class RasterModel(object):

    def __init__(self, grid=None, clock=None, fields=None, **kwds):
        self._clock = TimeStepper(**clock)
        if grid.pop('_type', 'raster_model_grid') != 'raster_model_grid':
            raise ValueError('not a raster grid')

        try:
            filepath = grid.pop('from_file')
        except KeyError:
            self._grid = RasterModelGrid.from_dict(grid)
        else:
            self._grid = RasterModelGrid.from_file(filepath, **grid)

        if fields is not None:
            self._grid.add_fields(**fields)

        self._components = ()

        self._params = dict(grid=grid, clock=clock)
        self._params.update(**kwds)

    @property
    def grid(self):
        return self._grid

    @property
    def clock(self):
        return self._clock

    def advance_components(self, dt):
        for component in self._components:
            component.run_one_step(dt)

    def run_one_step(self, dt=None, output=None, names=None):
        """Run each component for one time step."""
        dt = dt or self.clock.step

        self.advance_components(dt)
        self.clock.advance(step=dt)

        if output:
            write_raster_netcdf(output, self.grid, append=True, names=names)

    def run(self, output=None, names=None):
        """Run the model until complete."""
        if output:
            write_raster_netcdf(output, self.grid, append=False, names=names)

        try:
            while 1:
                self.run_one_step(output=output, names=names)
        except StopIteration:
            pass

    @classmethod
    def argparser(cls, *args, **kwds):
        parser = argparse.ArgumentParser(*args, **kwds)

        parser.add_argument('file', nargs='?', help='model configuration file')
        parser.add_argument('--output', help='output netcdf file')
        parser.add_argument('--fields', action='append', default=[],
                            help='fields to write to netcdf file')
        parser.add_argument('--with-citations', action='store_true',
                            help='Print citations for components used')
        parser.add_argument('--verbose', action='store_true', help='be verbose')
        parser.add_argument('--dry-run', action='store_true',
                            help='do not actually run the model')
        parser.add_argument('--set', action='append', default=[],
                            help='set model parameters')
        parser.add_argument('--plot', choices=cls.LONG_NAME.keys(), default=None,
                            help='value to plot')

        return parser

    @classmethod
    def main(cls):
        parser = cls.argparser()

        args = parser.parse_args()

        params = load_model_params(param_file=args.file,
                                   defaults=cls.DEFAULT_PARAMS,
                                   dotted_params=args.set)

        if args.verbose:
            print(yaml.dump(params, default_flow_style=False))

        model = cls(**params)

        if args.with_citations:
            from landlab.core.model_component import registry
            print(registry.format_citations())

        if not args.dry_run:
            model.run(output=args.output, names=args.fields or None)

            if args.plot:
                imshow_grid(model.grid,
                            model.grid.at_node[cls.LONG_NAME[args.plot]],
                            at='node', show=True, cmap='Blues')

    @property
    def params(self):
        return self._params

    def format_params(self):
        return yaml.dump(self.params, default_flow_style=False)


def load_params_from_strings(values):
    params = dict()
    for param in values:
        dotted_name, value = param.split('=')
        params.update(dots_to_dict(dotted_name, yaml.load(value)))

    return params


def dots_to_dict(name, value):
    base = {}
    level = base
    names = name.split('.')
    for k in names[:-1]:
        level[k] = dict()
        level = level[k]
    level[names[-1]] = value
    return base


def dict_to_dots(d):
    dots = []
    for names in walk_dict(d):
        dots.append('.'.join(names[:-1]) + '=' + str(names[-1]))
    return dots


def walk_dict(indict, prev=None):
    prev = prev[:] if prev else []

    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in walk_dict(value, [key] + prev):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                # yield prev + [key, value]
                for v in value:
                    for d in walk_dict(v, [key] + prev):
                        yield d
            else:
                yield prev + [key, value]
    else:
        yield indict


def load_model_params(param_file=None, defaults=None, dotted_params=()):
    params = defaults or {}

    if param_file:
        params_from_file = load_params(param_file)
        dotted_params += dict_to_dots(params_from_file) + dotted_params
        for group in params.keys():
            params[group].update(params_from_file.get(group, {}))

    params_from_cl = load_params_from_strings(dotted_params)
    for group in params.keys():
        params[group].update(params_from_cl.get(group, {}))

    return params
