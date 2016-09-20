# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File:        orbit.py
    Author:      Efrain Torres-Lomas
    Email:       efrain@fisica.ugto.mx
    Github:      https://github.com/elchinot7
    Description: ToDo

"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
# from mpl_toolkits.mplot3d import Axes3D
# plt.ion()
# from itertools import cycle
import sys
from utils import plot_quiver_2D, plot_quiver_3D


class Orbit(object):
    def __init__(self, init_cond, model, model_pars, t, label=''):
        self.init_cond = init_cond  # must be an collections.OrderedDict
        self.names = list(init_cond.keys())
        self.init = list(init_cond.values())
        self.Ndim = len(init_cond)      # int
        self.model = model              # method
        self.model_pars = model_pars    # list
        self.t = t                      # numpy array
        self.label = label
        self.solution = []
        self.is_solved = False

    def evolve(self, t=None):
        if self.is_solved:
            pass
        if t is None:
            t = self.t
        self.solution = odeint(self.model, self.init, t=t, args=(self.model_pars,))
        self.is_solved = True
        # return evolved

    def plot_orbit(self, ax, vars_to_plot, **kwargs):
        if len(vars_to_plot) > 3:
            sys.exit("We can't plot in Ndim > 3")

        if not all(key in self.names for key in vars_to_plot):  # check vars exist
            sys.exit("vars_to_plot are not a subset of vars")

        if kwargs is not None and 't' in kwargs:
            t = kwargs['t']
        else:
            t = None

        self.evolve(t=t)

        # plot_list = []
        indexes = []
        for key in vars_to_plot:
            # print key, self.init_cond[key]
            ind = self.init_cond.keys().index(key)
            indexes.append(ind)
            # plot_list.append(self.solution[:, ind])

        if len(vars_to_plot) is 2:
            # ax.plot(plot_list[0], plot_list[1], label=self.label, **kwargs)
            ax.plot(self.solution[:, indexes[0]], self.solution[:, indexes[1]], label=self.label, **kwargs)
        elif len(vars_to_plot) is 3:
            # ax.plot(plot_list[0], plot_list[1], plot_list[2], label=self.label, **kwargs)
            ax.plot(self.solution[:, indexes[0]], self.solution[:, indexes[1]], self.solution[:, indexes[2]],
                    label=self.label, **kwargs)

    def plot_function(self, ax, indep_vars, function, args=None, **kwargs):
        if args is not None and not all(key in self.names for key in args):  # check vars exist
            sys.exit("args are not a subset of vars")
        if not all(key in self.names for key in indep_vars):  # check indep_vars exist
            sys.exit("indep_vars are not a subset of vars")

        if kwargs is not None and 't' in kwargs:
            t = kwargs['t']
        else:
            t = None

        # Evolving...
        self.evolve(t=t)

        indep_vars_list = []
        for key in indep_vars:
            ind = self.init_cond.keys().index(key)
            indep_vars_list.append(self.solution[:, ind])

        if args is None:
            f = function([self.solution[:, 0], self.solution[:, 1]])
        else:
            args_list = []
            for key in args:
                ind = self.init_cond.keys().index(key)
                args_list.append(self.solution[:, ind])

            f = function(args_list)

        if len(indep_vars) == 1:
            x = indep_vars_list[0]
            ax.plot(x, f, **kwargs)
        elif len(indep_vars) == 2:
            x = indep_vars_list[0]
            y = indep_vars_list[1]
            ax.plot(x, y, f, **kwargs)

    def plot_flow_over_orbit(self, ax, vars_to_plot, flow_index=None, **kwargs):

        if flow_index is None:
            sys.exit("flow_index must be a list of integers")
        if any(not isinstance(x, int) for x in flow_index):
            print type(flow_index)
            sys.exit("flow_index must be a list of integers")

        if not self.is_solved:
            sys.exit("To plot the flow you must plot the orbit solution first")

        indexes = []
        for key in vars_to_plot:
            ind = self.init_cond.keys().index(key)
            indexes.append(ind)

        if len(indexes) > 1:
            x = np.array([self.solution[:, indexes[0]][i] for i in flow_index if (i < len(self.solution[:, indexes[0]]))])
            y = np.array([self.solution[:, indexes[1]][i] for i in flow_index if (i < len(self.solution[:, indexes[1]]))])

        if len(indexes) > 2:
            z = np.array([self.solution[:, indexes[2]][i] for i in flow_index if (i < len(self.solution[:, indexes[2]]))])

        if len(indexes) == 2:
            U, V = zip(*[self.model([x1, y1], self.model_pars) for x1, y1 in zip(x, y)])
            plot_quiver_2D(ax=ax, x=x, y=y, u=U, v=V, **kwargs)

        elif len(indexes) == 3:
            U, V, W = zip(*[self.model_pars([x1, y1, z1], self.model_pars) for x1, y1, z1 in zip(x, y, z)])
            plot_quiver_3D(ax=ax, x=x, y=y, z=z, u=U, v=V, w=W, **kwargs)

    def plot_flow_over_function(self, ax, indep_vars, function, function_dot,
                                flow_index, args=None, **kwargs):

        if flow_index is None:
            sys.exit("flow_index must be a list of integers")
        if any(not isinstance(x, int) for x in flow_index):
            print type(flow_index)
            sys.exit("flow_index must be a list of integers")

        if not self.is_solved:
            sys.exit("To plot the flow you must plot the orbit solution first")

        indep_vars_list = []
        indexes = []
        for key in indep_vars:
            ind = self.init_cond.keys().index(key)
            indexes.append(ind)
            indep_vars_list.append(self.solution[:, ind])

        # if args is None:
        #     f = function([self.solution[:, 0], self.solution[:, 1]])
        # else:
        #     args_list = []
        #     for key in args:
        #         ind = self.init_cond.keys().index(key)
        #         args_list.append(self.solution[:, ind])
        #     f = function(args_list)

        if self.Ndim > 0:
            x = np.array([self.solution[:, 0][i] for i in flow_index if (i < len(self.solution[:, 0]))])
        if self.Ndim > 1:
            y = np.array([self.solution[:, 1][i] for i in flow_index if (i < len(self.solution[:, 1]))])

        f = function([x, y])

        if self.Ndim == 2:
            U, V = zip(*[self.model([x1, y1], self.model_pars) for x1, y1 in zip(x, y)])
        # if len(indep_vars) > 0:
        #     U = VEL[:, 0]
        # if len(indep_vars) > 1:
        #     V = VEL[:, indexes[1]]

        f_dot = function_dot([x, y])

        if len(indep_vars) == 1:
            # W = zip(*[function_dot([x1, y1], args) for x1, y1 in zip(x, y)])
            plot_quiver_2D(ax=ax, x=x, y=f, u=U, v=f_dot, **kwargs)

        if len(indep_vars) == 2:
            # U, V, W = zip(*[function([x1, y1, z1], args) for x1, y1, z1 in zip(x, y, z)])
            plot_quiver_3D(ax=ax, x=x, y=y, z=f, u=U, v=V, w=f_dot, **kwargs)


def test_model(init, t=None, model_pars=[]):
    '''
    This defines the dynamical system for model
    :math:`V = m^2 \phi^2/2`
    '''
    x1 = init[0]
    y1 = init[1]
    # the model equations
    x1_dot = y1
    y1_dot = -x1 - 3.0 * y1 * np.sqrt(x1**2.0 + y1**2.0)
    return [x1_dot, y1_dot]


def test_function(args):
    x = args[0]
    y = args[1]
    return x + y**2


def test_function_dot(args):
    x = args[0]
    y = args[1]
    u, v = test_model([x, y])
    return u + 2*y*v

if __name__ == "__main__":
    import collections
    # import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)

    d0 = collections.OrderedDict()
    d0['x'] = 0
    d0['y'] = 1

    t = np.linspace(0.0, 1.0, 10)

    orbit = Orbit(init_cond=d0, model=test_model, model_pars=[], t=t,
                  label='label')

    orbit.plot_orbit(ax, vars_to_plot=['x', 'y'], lw=2, color='g')
    orbit.plot_flow_over_orbit(ax, vars_to_plot=['x', 'y'], width=0.005,
                               flow_index=[1, 2, 5, 10], color='g')
    orbit.plot_function(ax, indep_vars=['x'], function=test_function,
                        label='function', color='r', linewidth=2)
    orbit.plot_flow_over_function(ax, indep_vars=['x'], function=test_function,
                                  function_dot=test_function_dot,
                                  args=None, flow_index=[1, 3, 5, -2], width=0.005,
                                  color='r')
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.show()