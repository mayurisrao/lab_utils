import cmath
import numpy as np
import math
import matplotlib.pyplot as plt
from sparam import s_extract


def ideal_switch_gen(freq, switchon):
   """
    Generates an ideal transfer switch S-parameter matrix in complex form.

    This function creates an S-parameter matrix for a 4-port ideal switch 
    based on given frequency points. The S-parameters are expressed in dB.

    Parameters
    ----------
    freq : list or numpy.ndarray Frequency points (in Hz) at which the S-parameters are calculated. The length of this array determines the number of frequency points in the generated S-parameter matrix.

    switchon : bool True if on (Transfer Switch in crossed state) else False (Transfer Switch in through state)

    Returns
    -------
    numpy.ndarray
    A 3D array containing the S-parameter matrices for each frequency point,
    shape (len(freq_), 4, 4).

    Example
    -------
    >>> freq_points = np.array([1e9, 2e9, 3e9])  # Frequency points in Hz
    >>> s_matrix = ideal_switch_gen(freq_points)
    """
   freq_ = freq
   val1 = 0
   val2 = 1
   
   if switchon:
       s11_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s12_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s13_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s14_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

       s21_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s22_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s23_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s24_ = [cmath.rect(val2, math.radians(0))]*len(freq_)

       s31_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s32_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s33_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s34_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

       s41_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s42_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s43_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s44_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
   else:
       s11_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s12_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s13_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s14_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

       s21_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s22_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s23_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s24_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

       s31_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s32_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s33_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s34_ = [cmath.rect(val2, math.radians(0))]*len(freq_)

       s41_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s42_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
       s43_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
       s44_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

   # Construct the S-matrix
   s_matrix_disp = [
    [s11_[0], s12_[0], s13_[0], s14_[0]],
    [s21_[0], s22_[0], s23_[0], s24_[0]],
    [s31_[0], s32_[0], s33_[0], s34_[0]],
    [s41_[0], s42_[0], s43_[0], s44_[0]]
   ]

    # Print the matrix with 'j' for imaginary numbers
   if switchon:
       print("\n\nS-Matrix of Ideal Switch On:\n")
   else:
       print("\n\nS-Matrix of Ideal Switch Off:\n")
   for row in s_matrix_disp:
      print(" | ".join(str(val) for val in row))


   sarray_interp = [s11_, s12_, s13_, s14_, s21_, s22_,s23_,s24_, s31_,s32_,s33_,s34_, s41_, s42_, s43_, s44_]

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i],                    sarray_interp[2][i], sarray_interp[3][i]],
                              [sarray_interp[4][i], sarray_interp[5][i], sarray_interp[6][i], sarray_interp[7][i]],
                              [sarray_interp[8][i], sarray_interp[9][i], sarray_interp[10][i],sarray_interp[11][i]],
                              [sarray_interp[12][i],sarray_interp[13][i],sarray_interp[14][i],sarray_interp[15][i]] ]))

   return np.array(Sarray)   



def ideal_rrc_gen(freq_):
   
   s11_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s12_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s13_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s14_ = [cmath.rect(0, math.radians(0))]*len(freq_)

   s21_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s22_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s23_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s24_ = [cmath.rect(0.707, math.radians(90))]*len(freq_)

   s31_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s32_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s33_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s34_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)

   s41_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s42_ = [cmath.rect(0.707, math.radians(90))]*len(freq_)
   s43_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s44_ = [cmath.rect(0, math.radians(0))]*len(freq_)

   
   # Construct the S-matrix
   s_matrix_disp = [
    [s11_[0], s12_[0], s13_[0], s14_[0]],
    [s21_[0], s22_[0], s23_[0], s24_[0]],
    [s31_[0], s32_[0], s33_[0], s34_[0]],
    [s41_[0], s42_[0], s43_[0], s44_[0]]
   ]

    # Print the matrix with 'j' for imaginary numbers
   print("\n\nS-Matrix of Ideal RRC:\n")
   for row in s_matrix_disp:
      print(" | ".join(str(val) for val in row))

   sarray_interp = [s11_, s12_, s13_, s14_, s21_, s22_,s23_,s24_, s31_,s32_,s33_,s34_, s41_, s42_, s43_, s44_]

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i],                    sarray_interp[2][i], sarray_interp[3][i]],
                              [sarray_interp[4][i], sarray_interp[5][i], sarray_interp[6][i], sarray_interp[7][i]],
                              [sarray_interp[8][i], sarray_interp[9][i], sarray_interp[10][i],sarray_interp[11][i]],
                              [sarray_interp[12][i],sarray_interp[13][i],sarray_interp[14][i],sarray_interp[15][i]] ]))

   return np.array(Sarray)   


def perturbed_rrc_gen(freq_, amppert, phasepert):
   amppert_ = 10**(np.array(amppert)/20)
   s11_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s12_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s13_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s14_ = [cmath.rect(0, math.radians(0))]*len(freq_)

   s21_ = [cmath.rect(0.707+amppert_[1], math.radians(-90 + phasepert[1]))]*len(freq_)
   s22_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s23_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s24_ = [cmath.rect(0.707, math.radians(90))]*len(freq_)

   s31_ = [cmath.rect(0.707+amppert_[2], math.radians(-90 + phasepert[2]))]*len(freq_)
   s32_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s33_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s34_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)

   s41_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   s42_ = [cmath.rect(0.707, math.radians(90))]*len(freq_)
   s43_ = [cmath.rect(0.707, math.radians(-90))]*len(freq_)
   s44_ = [cmath.rect(0, math.radians(0))]*len(freq_)
   
   # Construct the S-matrix
   s_matrix_disp = [
    [s11_[0], s12_[0], s13_[0], s14_[0]],
    [s21_[0], s22_[0], s23_[0], s24_[0]],
    [s31_[0], s32_[0], s33_[0], s34_[0]],
    [s41_[0], s42_[0], s43_[0], s44_[0]]
   ]

    # Print the matrix with 'j' for imaginary numbers
   print("\n\nS-Matrix of Ideal RRC:\n")
   for row in s_matrix_disp:
      print(" | ".join(str(val) for val in row))

   sarray_interp = [s11_, s12_, s13_, s14_, s21_, s22_,s23_,s24_, s31_,s32_,s33_,s34_, s41_, s42_, s43_, s44_]

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i],                    sarray_interp[2][i], sarray_interp[3][i]],
                              [sarray_interp[4][i], sarray_interp[5][i], sarray_interp[6][i], sarray_interp[7][i]],
                              [sarray_interp[8][i], sarray_interp[9][i], sarray_interp[10][i],sarray_interp[11][i]],
                              [sarray_interp[12][i],sarray_interp[13][i],sarray_interp[14][i],sarray_interp[15][i]] ]))

   return np.array(Sarray)   


def ideal_amp_gen(freq_, gain):
   
   s11_ = [0]*len(freq_)
   s12_ = [cmath.rect(gain, math.radians(0))]*len(freq_)
   
   s21_ = [cmath.rect(gain, math.radians(0))]*len(freq_)
   s22_ = [0]*len(freq_)
   
   # Construct the S-matrix
   s_matrix_disp = [
    [s11_[0], s12_[0]],
    [s21_[0], s22_[0]]
   ]

    # Print the matrix with 'j' for imaginary numbers
   print("\n\nS-Matrix of Ideal Amplifier:\n")
   for row in s_matrix_disp:
      print(" | ".join(str(val) for val in row))

   sarray_interp = [s11_, s12_, s21_, s22_]

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i]] ,
                              [sarray_interp[2][i], sarray_interp[3][i]] ]))
      
   return np.array(Sarray)   


def ideal_delayline_gen(freq_, l):
   """
    Generates an delay line s matrix
    """      
   freq_ = np.array(freq_)
   theta = (((2*np.pi)*freq_)/299792458)*l

   s11_ = [0]*len(freq_)
   s12_ = np.cos(theta) + 1j * np.sin(theta)
   s21_ = s12_   
   s22_ = [0]*len(freq_)   

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[s11_[i], s12_[i]] ,
                              [s21_[i], s22_[i]] ]))
      
   return np.array(Sarray)  
 

def correlator(input1, input2, x, plot):

    cross_correlation_out = input1 * np.conj(input2)
    # print(input1[0])
    # print(np.conj(input2)[0])
    # print(cross_correlation_out[0])
    #print(np.abs(input1[0]), np.abs(cross_correlation_out))

    if plot:
        # Create a 1x2 grid for two subplots side by side
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        # First plot: Correlation amplitude
        axs[0].plot(x, np.real(cross_correlation_out), label='real corr signal')
        axs[0].set_ylabel('Correlation Power real')
        axs[0].set_xlabel('Frequency (in Hz)')
        axs[0].grid()
        axs[0].legend()
        # Second plot: Correlation phase
        axs[1].plot(x, np.imag(cross_correlation_out), label='imag corr signal')
        axs[1].set_ylabel('Correlation Power imag')
        axs[1].set_xlabel('Frequency (in Hz)')
        axs[1].grid()
        axs[1].legend()
        # Adjust layout to prevent overlap
        fig.tight_layout()    
    return cross_correlation_out


def feeder2port(block_smatrix, input, freq_):

    threshold = 1e-15  # Define the threshold for small values
    b = []     
    for i in range(len(freq_)):
        a = np.array([input[0][i], input[1][i]])
        a = np.squeeze(a[:, None])
        result = np.dot(block_smatrix[i], a)
        
        # Apply threshold to remove small real and imaginary parts
        result.real[np.abs(result.real) < threshold] = 0
        result.imag[np.abs(result.imag) < threshold] = 0
        
        b.append(result) 
    
    # Split the results into separate arrays for each port
    b1 = np.array([((sub_array[0].real) + 1j * (sub_array[0].imag)) for sub_array in b])
    b2 = np.array([((sub_array[1].real) + 1j * (sub_array[1].imag)) for sub_array in b])
    
    return [b1, b2]


def feeder4port(block_smatrix, input, freq_):
    threshold = 1e-15  # Define the threshold for small values
    b = [] 
    
    for i in range(len(freq_)):
        a = np.array([input[0][i], input[1][i], input[2][i], input[3][i]])
        a = np.squeeze(a[:, None])
        result = np.matmul(block_smatrix[i], a)
        
        # Apply threshold to remove small real and imaginary parts
        result.real[np.abs(result.real) < threshold] = 0
        result.imag[np.abs(result.imag) < threshold] = 0
        
        b.append(result) 
    
    # Split the results into separate arrays for each port
    b1 = np.array([((sub_array[0].real) + 1j * (sub_array[0].imag)) for sub_array in b])
    b2 = np.array([((sub_array[1].real) + 1j * (sub_array[1].imag)) for sub_array in b])
    b3 = np.array([((sub_array[2].real) + 1j * (sub_array[2].imag)) for sub_array in b])
    b4 = np.array([((sub_array[3].real) + 1j * (sub_array[3].imag)) for sub_array in b])

    return [b1, b2, b3, b4]


def chain4ports(title, devices_sparam_list, input, freq_, plot):

    #input_save = input
    for _, device in enumerate(devices_sparam_list):     
        if device.shape[1] == 4:      
            #print(np.abs(input[1][0]))
            b_ = feeder4port(device, input, freq_)
            input = [b_[1], b_[0], b_[3], b_[2]]
            

    if plot:
        # Create a figure with two subplots in one row
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Plot amplitude on the left subplot (ax1)
        ax1.plot(freq_, np.abs(b_[0]), linestyle='-', label='$Out_{1}$')
        ax1.plot(freq_, np.abs(b_[1]), linestyle='--', label='$Out_{2}$')
        ax1.plot(freq_, np.abs(b_[2]), linestyle='-', label='$Out_{3}$')
        ax1.plot(freq_, np.abs(b_[3]), linestyle='--', label='$Out_{4}$')

        # Customize the left subplot
        ax1.set_xlabel("Frequency")
        ax1.set_ylabel("Amplitude")
        ax1.set_title(f"{title} - Amplitude")
        ax1.legend(loc='best')  # Legend for amplitude on the left
        ax1.grid(True)

        # Plot phase on the right subplot (ax2)
        ax2.plot(freq_, np.angle(b_[0], deg=True), linestyle='-', label='$Out_{1}$ Phase')
        ax2.plot(freq_, np.angle(b_[1], deg=True), linestyle='--', label='$Out_{2}$ Phase')
        ax2.plot(freq_, np.angle(b_[2], deg=True), linestyle='--', label='$Out_{3}$ Phase')
        ax2.plot(freq_, np.angle(b_[3], deg=True), linestyle='-', label='$Out_{4}$ Phase')

        # Customize the right subplot
        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Phase (Degrees)")
        ax2.set_title(f"{title} - Phase")
        ax2.legend(loc='best')  # Legend for phase on the right
        ax2.grid(True)

        # Adjust layout for clarity
        fig.tight_layout()

        # Show the plot
        plt.show()

    return np.array(b_)


def chain2ports(title, devices_sparam_list, input, freq_, plot):
    #input_save = input
    for _, device in enumerate(devices_sparam_list):         
        if device.shape[1] == 2:      
            b_ = feeder2port(device, input, freq_)
            input = [b_[0], b_[1]]

    if plot:
        # Create a figure with two subplots in one row
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Plot amplitude on the left subplot (ax1)
        ax1.plot(freq_, np.real(b_[0]), linestyle='-', label='$Out_{1} real$')
        ax1.plot(freq_, np.real(b_[1]), linestyle='--', label='$Out_{2} real$')

        # Customize the left subplot
        ax1.set_xlabel("Frequency")
        ax1.set_ylabel("Amplitude")
        ax1.set_title(f"{title} - Amplitude")
        ax1.legend(loc='best')  # Legend for amplitude on the left
        ax1.grid(True)

        # Plot phase on the right subplot (ax2)
        ax2.plot(freq_, np.imag(b_[0]), linestyle='-', label='$Out_{1}$ imag')
        ax2.plot(freq_, np.imag(b_[1]), linestyle='--', label='$Out_{2}$ imag')

        # Customize the right subplot
        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Phase (Degrees)")
        ax2.set_title(f"{title} - Phase")
        ax2.legend(loc='best')  # Legend for phase on the right
        ax2.grid(True)

        # Adjust layout for clarity
        fig.tight_layout()

        # Show the plot
        plt.show()

    return np.array(b_)