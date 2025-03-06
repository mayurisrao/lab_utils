import math
import numpy as np
from sparam import general_line_interpolate


def gen_VSD_50(temp, b, length):    
    k = 1.380649 * (10**(-23)) #  m2 kg s-2 K-1
    noise = np.array([math.sqrt(50*k*temp*b)] * length)

    print(f'Generated VSD for {temp}K and Spectral Res {round(b)} Hz @ 50 Ohms')
    return noise



def read_TA_V(file, R):
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
    
    return np.array(ta_linear_residues), np.array(V_nu), np.array(freq_residues)



def V_to_TA(V_nu):
    return (V_nu**2)/(1.38e-23  * 50)



def noise_generator(SNR_dB, V):

    # Calculate signal power in the frequency domain
    signal_power = np.mean(np.abs(V)**2)

    # Calculate noise power based on desired SNR
    noise_power = signal_power / (10**(SNR_dB / 10))

    # Generate flat Gaussian noise in the frequency domain
    noise = np.sqrt(noise_power) * (np.random.normal(size=V.shape) + 1j * np.random.normal(size=V.shape))

    return noise
