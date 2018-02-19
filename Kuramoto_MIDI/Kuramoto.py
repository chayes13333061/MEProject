# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:01:04 2018

@author: Chris
"""

from __future__ import print_function
import numpy as np
from scipy.integrate import ode

class Kuramoto(object): 
    
    """
    Implementation of Kuramoto coupling model [1] with harmonic terms
    and possible perturbation.
    It uses NumPy and Scipy's implementation of Runge-Kutta 4(5)
    for numerical integration.
    Usage example:
    >>> kuramoto = Kuramoto(initial_values)
    >>> phase = kuramoto.solve(X)
    [1] Kuramoto, Y. (1984). Chemical Oscillations, Waves, and Turbulence
        (Vol. 19). doi: doi.org/10.1007/978-3-642-69689-3
    """
    _noises = { 'logistic': np.random.logistic,
                'normal': np.random.normal,
                'uniform': np.random.uniform,
                'custom': None
              }

    noise_types = _noises.keys()

    def __init__(self, init_values, noise=None):
        """
        Passed arguments should be a dictionary with NumPy arrays
        for initial phase (Y0), intrisic frequencies (W) and coupling
        matrix (K).
        """
        self.dtype = np.float32

        self.dt = 1.
        self.init_phase = np.array(init_values['Y0'])
        self.W = np.array(init_values['W'])
        self.K = np.array(init_values['K'])

        self.n_osc = len(self.W)
        self.m_order = self.K.shape[0]

        self.noise = noise


    @property
    def noise(self):
        """Sets perturbations added to the system at each timestamp.
        Noise function can be manually defined or selected from
        predefined by assgining corresponding name. List of available
        pertrubations is reachable through `noise_types`. """
        return self._noise

    @noise.setter
    def noise(self, _noise):

        self._noise = None
        self.noise_params = None
        self.noise_type = 'custom'

        # If passed a function
        if callable(_noise):
            self._noise = _noise

        # In case passing string
        elif isinstance(_noise, str):

            if _noise.lower() not in self.noise_types:
                self.noise_type = None
                raise NameError("No such noise method")

            self.noise_type = _noise.lower()
            self.update_noise_params(self.dt)

            noise_function = self._noises[self.noise_type]
            self._noise = lambda: np.array([noise_function(**p) for p in self.noise_params])

    def update_noise_params(self, dt):
        self.scale_func = lambda dt: dt/np.abs(self.W**2)
        scale = self.scale_func(dt)

        if self.noise_type == 'uniform':
            self.noise_params = [{'low':-s, 'high': s} for s in scale]
        elif self.noise_type in self.noise_types:
            self.noise_params = [{'loc':0, 'scale': s} for s in scale]
        else:
            pass

    def kuramoto_ODE(self, t, y, arg):
        """General Kuramoto ODE of m'th harmonic order.
           Argument `arg` = (w, k), with
            w -- iterable frequency
            k -- 3D coupling matrix, unless 1st order
            """
        w, k = arg
        yt = y[:,None]
        dy = y-yt

        phase = w.astype(self.dtype)
        if self.noise != None:
            n = self.noise().astype(self.dtype)
            dy += n
        
        for m, _k in enumerate(k):
            phase += np.sum(_k*np.sin((m+1)*dy),axis=1)
        
        return phase

    def kuramoto_ODE_jac(self, t, y, arg):
        """Kuramoto's Jacobian passed for ODE solver."""

        w, k = arg
        yt = y[:,None]
        dy = y-yt

        phase = [m*k[m-1]*np.cos(m*dy) for m in range(1,1+self.m_order)]
        phase = np.sum(phase, axis=0)

        for i in range(self.n_osc):
            phase[i,i] = -np.sum(phase[:,i])

        return phase

    def solve(self, t):
        """Solves Kuramoto ODE for time series `t` with initial
        parameters passed when initiated object.
        """
        dt = t[1]-t[0]
        if self.dt != dt and self.noise_type != 'custom':
            self.dt = dt
            self.update_noise_params(dt)

        kODE = ode(self.kuramoto_ODE, jac=self.kuramoto_ODE_jac)
        kODE.set_integrator("dopri5")

        # Set parameters into model
        kODE.set_initial_value(self.init_phase, t[0])
        kODE.set_f_params((self.W, self.K))
        kODE.set_jac_params((self.W, self.K))

        if self._noise != None:
            self.update_noise_params(dt)

        phase = np.empty((self.n_osc, len(t)))
        
        # Run ODE integrator
        for idx, _t in enumerate(t[1:]):
            phase[:,idx] = kODE.y
            kODE.integrate(_t)

        phase[:,-1] = kODE.y
        
        return phase
