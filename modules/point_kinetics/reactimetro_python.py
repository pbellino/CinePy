#!/usr/bin/env python3

import numpy as np
from typing import Union, Tuple
import warnings

def reactimetro_python(
    n: np.ndarray,
    time_input: Union[float, np.ndarray],
    lam: np.ndarray,
    b: np.ndarray,
    Lstar: float,
    Q_in: Union[float, np.ndarray] = 0.0,
    validate_inputs: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Solves numerically the inverse kinetics equation to get the reactivity as a
    function of time.

    This function implements the inverse kinetics method for nuclear reactor
    physics, calculating reactivity from neutron density measurements using the
    point kinetics equations.

    Parameters:
    -----------
    n : np.ndarray
        Neutron density measurements (shape: (Nr,))
    time_input : float or np.ndarray
        If float: Time interval separation (dt) between each point in n [s]
        If array: Time vector with same length as n [s]
    lam : np.ndarray
        Decay constants of delayed neutron precursors [1/s] (shape: (Ng,))
    b : np.ndarray
        Delayed neutron fraction (beta_i / beta_total) (shape: (Ng,))
        Should sum to 1.0 for proper normalization
    Lstar : float
        Reduced reproduction time (Lambda / beta_effective) [s]
    Q_in : float or np.ndarray, optional
        Neutron source strength. If array, must satisfy len(Q_in) == len(n)
        Default: 0.0
    validate_inputs : bool, optional
        Whether to perform input validation. Default: True

    Returns:
    --------
    rho : np.ndarray
        Reactivity as a function of time (shape: (Nr,))
    t : np.ndarray
        Time vector [s] (shape: (Nr,))
    D : np.ndarray
        Auxiliary variable used in inverse kinetic method (shape: (Nr,))

    Raises:
    -------
    ValueError
        If input arrays have incompatible dimensions or contain invalid values
    """

    if validate_inputs:
        _validate_inputs(n, time_input, lam, b, Lstar, Q_in)

    # Convert inputs to numpy arrays with appropriate dtypes
    n = np.asarray(n, dtype=np.float64)
    lam = np.asarray(lam, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    Nr = len(n)
    Ng = len(lam)

    # Handle time input - check if it's scalar or array
    if np.isscalar(time_input):
        # Scalar dt case (backward compatibility)
        dt = float(time_input)
        t = np.arange(Nr, dtype=np.float64) * dt
        is_uniform_dt = True
        uniform_dt = dt
    else:
        # Time vector case
        t = np.asarray(time_input, dtype=np.float64)
        if len(t) != Nr:
            raise ValueError('Time vector must have the same length as neutron density array')
        is_uniform_dt = False
        # Check if time vector is actually uniform (for optimization)
        if Nr > 1:
            dt_array = np.diff(t)
            if np.allclose(dt_array, dt_array[0], rtol=1e-12):
                is_uniform_dt = True
                uniform_dt = dt_array[0]

    # Handle Q_in input
    if np.isscalar(Q_in):
        Q = np.full(Nr, Q_in, dtype=np.float64)
    else:
        Q = np.asarray(Q_in, dtype=np.float64)

    # Pre-allocate arrays
    c = np.zeros((Ng, Nr), dtype=np.float64)
    rho = np.zeros(Nr, dtype=np.float64)
    D = np.zeros(Nr, dtype=np.float64)

    # Pre-calculate terms for uniform time step case
    if is_uniform_dt:
        # Pre-calculate exponential decay factors (vectorized)
        exp_factors = np.exp(-lam * uniform_dt)
        one_minus_exp = 1.0 - exp_factors

        # Pre-calculate commonly used terms
        b_over_lam_Lstar = b / (lam * Lstar)
        one_minus_exp_over_lam_dt = one_minus_exp / (lam * uniform_dt)
    else:
        # For non-uniform case, we'll calculate these per iteration
        b_over_lam_Lstar = b / (lam * Lstar)

    # Initial conditions: precursors at equilibrium
    c[:, 0] = n[0] * b_over_lam_Lstar

    # Initial reactivity
    if n[0] != 0:
        rho[0] = -Lstar * Q[0] / n[0]
    else:
        rho[0] = 0.0
        warnings.warn("Initial neutron density is zero, setting initial reactivity to 0")

    # Main calculation loop
    for k in range(1, Nr):
        # Calculate time step for this interval
        if is_uniform_dt:
            dt_k = uniform_dt
        else:
            dt_k = t[k] - t[k-1]

        # Neutron density derivative
        dn_dt = (n[k] - n[k-1]) / dt_k
        D[k] = dn_dt

        # Update precursor concentrations
        dn = n[k] - n[k-1]

        if is_uniform_dt:
            # Optimized calculation for uniform time steps (vectorized)
            term1 = c[:, k-1] * exp_factors
            term2 = b_over_lam_Lstar * (
                n[k-1] * one_minus_exp - one_minus_exp_over_lam_dt * dn + dn
            )
            c[:, k] = term1 + term2
        else:
            # Non-uniform time steps - calculate per group
            exp_factors_k = np.exp(-lam * dt_k)
            one_minus_exp_k = 1.0 - exp_factors_k

            term1 = c[:, k-1] * exp_factors_k
            term2 = b_over_lam_Lstar * (
                n[k-1] * one_minus_exp_k -
                one_minus_exp_k / (lam * dt_k) * dn +
                dn
            )
            c[:, k] = term1 + term2

        # Update D with precursor contributions
        D[k] -= np.sum(lam * c[:, k])

        # Calculate reactivity
        # As in LabVIEW
        # rho[k] = 1 + Lstar * (D[k] - Q[k]) / n[k-1]
        # As it should be
        rho[k] = 1.0 + Lstar * (D[k] - Q[k]) / n[k]

    return rho, t, D


def _validate_inputs(n, time_input, lam, b, Lstar, Q_in):
    """Validate input parameters for reactimetro function."""

    # Convert to numpy arrays for validation
    n = np.asarray(n)
    lam = np.asarray(lam)
    b = np.asarray(b)

    # Check dimensions
    if n.ndim != 1:
        raise ValueError("Neutron density 'n' must be a 1D array")

    if lam.ndim != 1:
        raise ValueError("Decay constants 'lam' must be a 1D array")

    if b.ndim != 1:
        raise ValueError("Delayed neutron fractions 'b' must be a 1D array")

    if len(lam) != len(b):
        raise ValueError("Arrays 'lam' and 'b' must have the same length")

    # Check for valid values
    if len(n) < 2:
        raise ValueError("Neutron density array 'n' must have at least 2 points")

    # Validate time input
    if np.isscalar(time_input):
        if time_input <= 0:
            raise ValueError("Time step 'dt' must be positive")
    else:
        time_array = np.asarray(time_input)
        if time_array.ndim != 1:
            raise ValueError("Time vector must be a 1D array")
        if len(time_array) != len(n):
            raise ValueError("Time vector must have the same length as neutron density array")
        if len(time_array) < 2:
            raise ValueError("Time vector must have at least 2 points")

        # Check that time is strictly increasing
        dt_array = np.diff(time_array)
        if np.any(dt_array <= 0):
            raise ValueError("Time vector must be strictly increasing")

    if np.any(lam <= 0):
        raise ValueError("All decay constants 'lam' must be positive")

    if np.any(b <= 0):
        raise ValueError("All delayed neutron fractions 'b' must be positive")

    if Lstar <= 0:
        raise ValueError("Reduced reproduction time 'Lstar' must be positive")

    if np.any(n < 0):
        raise ValueError("Neutron density 'n' values must be non-negative")

    # Check Q_in dimensions
    if not np.isscalar(Q_in):
        Q_in = np.asarray(Q_in)
        if len(Q_in) != len(n):
            raise ValueError("Source strength array 'Q_in' must have the same length as 'n'")

    # Check normalization of b (with tolerance)
    b_sum = np.sum(b)
    if not np.isclose(b_sum, 1.0, rtol=1e-3):
        warnings.warn(f"Delayed neutron fractions 'b' sum to {b_sum:.6f}, expected ~1.0")
