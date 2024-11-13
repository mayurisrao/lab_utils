import math
import numpy as np
from sparam import general_line_interpolate


def gen_VSD_50(temp, b, length):
    """
    Generates an Voltage Spectral Density based on Additive White Gaussian Noise (AWGN) source for given temperature 
    and bandwidth parameters.

    This function computes the noise voltage for a given temperature (in Kelvin), 
    bandwidth (in Hertz), and the length of the noise signal frequency points.

    Parameters
    ----------
    temp : float
        The temperature in Kelvin (K) at which the noise is generated.

    b : float
        The bandwidth in Hertz (Hz) over which the noise is measured.

    length : int
        The number of frequency points over which noise is to be generated.

    Returns
    -------
    noise : np.ndarray
        A NumPy array containing the generated noise samples. Each sample is the same 
        value representing the root mean square (RMS) noise voltage at the specified 
        temperature and bandwidth.

    Notes
    -----
    The generated noise is based on the Johnson-Nyquist noise formula:
    V_noise = sqrt(4 * k * T * B), where:
        - k is the Boltzmann constant (1.380649 x 10^-23 m² kg s⁻² K⁻¹)
        - T is the temperature in Kelvin
        - B is the bandwidth in Hertz

    Example
    -------
    >>> noise_samples = noise_50(300, 1e6, 1000)
    >>> print(noise_samples)
    """

    k = 1.380649 * (10**(-23)) #  m2 kg s-2 K-1

    noise = np.array([math.sqrt(50*k*temp*b)] * length)
    print(f'Generated VSD for {temp}K and Spectral Res {round(b)} Hz @ 50 Ohms')
    return noise



def TA_to_V(file, R):
    # load the input
    freq_residues = []
    linear_residues = []

    with open(file, 'r') as file:
        lines = file.readlines()
        
        # Check for the correct header
        for line in lines:
            parts = line.split()
            freq_residues.append(float(parts[0])*(1e9))
            linear_residues.append(float(parts[-1]))

    ta_linear_residues = []

    freq_residues = np.array(freq_residues)
    linear_residues = np.array(linear_residues)

    apsera_freq = np.linspace(min(freq_residues), max(freq_residues), num=len(freq_residues))  
    ta_linear_residues = general_line_interpolate(freq_residues, apsera_freq, linear_residues)

    V_nu = np.sqrt((1.38e-23)*R*ta_linear_residues)

    return np.array(V_nu), np.array(freq_residues)

    