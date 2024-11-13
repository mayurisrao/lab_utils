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
   val1 = 10**(-120/20)
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
   """
    Generates an ideal rat race coupler (RRC) S-parameter matrix in complex form.

    This function creates an S-parameter matrix for a 4-port ideal rat race coupler
    filter based on given frequency points. The S-parameters are expressed in complex 
    values representing the filter characteristics.

    Parameters
    ----------
    freq_ : list or numpy.ndarray
        Frequency points (in Hz) at which the S-parameters are calculated. 
        The length of this array determines the number of frequency points 
        in the generated S-parameter matrix.

    Returns
    -------
    numpy.ndarray
        A 3D array containing the S-parameter matrices for each frequency point,
        shape (len(freq_), 4, 4).

    Example
    -------
    >>> freq_points = np.array([1e9, 2e9, 3e9])  # Frequency points in Hz
    >>> s_matrix = ideal_rrc_gen(freq_points)
    """
   
   s11_ = [0 + 0j]*len(freq_)
   s12_ = [0-0.707j]*len(freq_)
   s13_ = [0-0.707j]*len(freq_)
   s14_ = [0 + 0j]*len(freq_)

   s21_ = [0-0.707j]*len(freq_)
   s22_ = [0 + 0j]*len(freq_)
   s23_ = [0 + 0j]*len(freq_)
   s24_ = [0+0.707j]*len(freq_)

   s31_ = [0-0.707j]*len(freq_)
   s32_ = [0 + 0j]*len(freq_)
   s33_ = [0 + 0j]*len(freq_)
   s34_ = [0-0.707j]*len(freq_)

   s41_ = [0 + 0j]*len(freq_)
   s42_ = [0+0.707j]*len(freq_)
   s43_ = [0-0.707j]*len(freq_)
   s44_ = [0 + 0j]*len(freq_)

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


    # s11_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s12_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
    # s13_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
    # s14_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)

    # s21_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
    # s22_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s23_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s24_ = [cmath.rect(val2, math.radians(0))]*len(freq_)

    # s31_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
    # s32_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s33_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s34_ = [cmath.rect(val1, math.radians(0))]*len(freq_)

    # s41_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)
    # s42_ = [cmath.rect(val2, math.radians(0))]*len(freq_)
    # s43_ = [cmath.rect(val1, math.radians(0))]*len(freq_)
    # s44_ = [cmath.rect(0.00000001, math.radians(0))]*len(freq_)


#    s11_ = [0.00000001]*len(freq_)
#    s12_ = [0+0.707j]*len(freq_)
#    s13_ = [0-0.707j]*len(freq_)
#    s14_ = [0.00000001]*len(freq_)

#    s21_ = [cmath.rect(0.707, math.radians(0))]*len(freq_)
#    s22_ = [0.00000001]*len(freq_)
#    s23_ = [0-0.707j]*len(freq_)
#    s24_ = [cmath.rect(0.707, math.radians(0))]*len(freq_)

#    s31_ = [cmath.rect(0.707, math.radians(180))]*len(freq_)
#    s32_ = [0.00000001]*len(freq_)
#    s33_ = [0.00000001]*len(freq_)
#    s34_ = [cmath.rect(0.707, math.radians(180))]*len(freq_)

#    s41_ = [0.00000001]*len(freq_)
#    s42_ = [0+0.707j]*len(freq_)
#    s43_ = [0+0.707j]*len(freq_)
#    s44_ = [0.00000001]*len(freq_)

   sarray_interp = [s11_, s12_, s13_, s14_, s21_, s22_,s23_,s24_, s31_,s32_,s33_,s34_, s41_, s42_, s43_, s44_]

   Sarray = []
   for i in range(len(freq_)):
      Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i],                    sarray_interp[2][i], sarray_interp[3][i]],
                              [sarray_interp[4][i], sarray_interp[5][i], sarray_interp[6][i], sarray_interp[7][i]],
                              [sarray_interp[8][i], sarray_interp[9][i], sarray_interp[10][i],sarray_interp[11][i]],
                              [sarray_interp[12][i],sarray_interp[13][i],sarray_interp[14][i],sarray_interp[15][i]] ]))

   return np.array(Sarray)   


def ideal_amp_gen(freq_, gain):
   """
    Generates an ideal amplifier (no phase lag) S-parameter matrix in complex form.

    This function creates an S-parameter matrix for a 2-port ideal amplifier based on
    given frequency points. The S-parameters represent the reflection and transmission 
    characteristics of the amplifier.

    Parameters
    ----------
    $freq_$ : list or numpy.ndarray
        Frequency points (in Hz) at which the S-parameters are calculated. 
        The length of this array determines the number of frequency points 
        in the generated S-parameter matrix.
    gain : Gain of the amp in dB

    Returns
    -------
    numpy.ndarray
        A 3D array containing the S-parameter matrices for each frequency point,
        shape (len(freq_), 2, 2).

    Example
    -------
    >>> freq_points = np.array([1e9, 2e9, 3e9])  # Frequency points in Hz
    >>> s_matrix = ideal_amp_gen(freq_points, 3)
    """
   
   
   s11_ = [0.000001]*len(freq_)
   s12_ = [cmath.rect(gain, math.radians(0))]*len(freq_)
   
   s21_ = [cmath.rect(gain, math.radians(0))]*len(freq_)
   s22_ = [0.000001]*len(freq_)
   

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


def correlator(input1, input2, x):

    corr_amp = []
    corr_ph = []

    for i in range(len(input1)):
        corr_amp.append((np.abs(input1[i]) * np.abs(input2[i])))
        corr_ph.append(np.angle(input1[i]) + np.angle(np.conj(input2[i])))
        
    cross_correlation_out = np.array([cmath.rect(mag, phase) for mag, phase in zip(corr_amp, corr_ph)])

    # Create a 1x2 grid for two subplots side by side
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    # First plot: Correlation amplitude
    axs[0].plot(x, np.abs(cross_correlation_out), label='Corr signal amp')
    axs[0].set_ylabel('Correlation Power Mag')
    axs[0].set_xlabel('Frequency (in Hz)')
    axs[0].grid()
    axs[0].legend()

    # Second plot: Correlation phase
    axs[1].plot(x, np.degrees(np.angle(cross_correlation_out)), label='Corr signal phase')
    axs[1].set_ylabel('Correlation phase')
    axs[1].set_xlabel('Frequency (in Hz)')
    axs[1].grid()
    axs[1].legend()

    # Adjust layout to prevent overlap
    fig.tight_layout()
    
    return fig, cross_correlation_out


def feeder4port(title, block_smatrix, input1, input2, freq_, plot, flipinput):

    s21_ = s_extract(which_s='s21', s_matrix_=block_smatrix)
    s34_ = s_extract(which_s='s34', s_matrix_=block_smatrix)
    s31_ = s_extract(which_s='s31', s_matrix_=block_smatrix)
    s24_ = s_extract(which_s='s24', s_matrix_=block_smatrix)

    s12_ = s_extract(which_s='s12', s_matrix_=block_smatrix)
    s43_ = s_extract(which_s='s43', s_matrix_=block_smatrix)
    s13_ = s_extract(which_s='s13', s_matrix_=block_smatrix)
    s42_ = s_extract(which_s='s42', s_matrix_=block_smatrix)

    a1_ = input1
    a4_ = input2

    # b2_amp = []
    # b3_amp = []
    # b2_phase = []
    # b3_phase = []
    
    b2_ = []
    b3_ = []

    # Multiplying input voltage with S-parameters to get the output voltage
    for i in range(len(s21_)):

        if not flipinput:
            # b2_amp.append((np.abs(s21_[i]) * np.abs(a1_[i])) + (np.abs(s24_[i]) * np.abs(a4_[i])))
            # b3_amp.append((np.abs(s34_[i]) * np.abs(a4_[i])) + (np.abs(s31_[i]) * np.abs(a1_[i])))
            # b2_phase.append((np.angle(s21_[i]) * np.angle(a1_[i])) + (np.angle(s24_[i]) * np.angle(a4_[i])))
            # b3_phase.append((np.angle(s34_[i]) * np.angle(a4_[i])) + (np.angle(s31_[i]) * np.angle(a1_[i])))

            b2_.append((s21_[i]*a1_[i]) + (s24_[i]*a4_[i]))
            b3_.append((s34_[i]*a4_[i]) + (s31_[i]*a1_[i]))
                        
        else:
            # b2_amp.append((np.abs(s12_[i]) * np.abs(a1_[i])) + (np.abs(s13_[i]) * np.abs(a4_[i])))
            # b3_amp.append((np.abs(s43_[i]) * np.abs(a4_[i])) + (np.abs(s42_[i]) * np.abs(a1_[i])))
            # b2_phase.append((np.angle(s12_[i]) * np.angle(a1_[i])) + (np.angle(s13_[i]) * np.angle(a4_[i])))
            # b3_phase.append((np.angle(s43_[i]) * np.angle(a4_[i])) + (np.angle(s42_[i]) * np.angle(a1_[i])))

            b2_.append((s12_[i]*a1_[i]) + (s13_[i]*a4_[i]))
            b3_.append((s43_[i]*a4_[i]) + (s42_[i]*a1_[i]))

        # b2_ = [cmath.rect(mag, phase) for mag, phase in zip(b2_amp, b2_phase)]
        # b3_ = [cmath.rect(mag, phase) for mag, phase in zip(b3_amp, b3_phase)]

    # Convert b2_ and b3_ to numpy arrays for easier amplitude and phase extraction
    b2_ = np.array(b2_)
    b3_ = np.array(b3_)

    if plot:
        # Create a figure with two subplots (one row, two columns)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Plot amplitude in the first subplot (ax1)
        ax1.plot(freq_, np.abs(b2_), label='$Out_{2}$', linestyle='-')
        ax1.plot(freq_, np.abs(b3_), label='$Out_{3}$', linestyle='--')
        ax1.plot(freq_, np.abs(a1_), label='$In_{1}$', linestyle='-')
        ax1.plot(freq_, np.abs(a4_), linestyle='--', label='$In_{4}$')

        # Customize the amplitude subplot
        ax1.set_xlabel("Frequency")
        ax1.set_ylabel("Amplitude")
        ax1.set_title(f"{title} - Amplitude")
        ax1.legend(loc='upper left')
        ax1.grid()

        # Plot phase in the second subplot (ax2)
        ax2.plot(freq_, np.degrees(np.angle(b2_)), label='$Out_{2}$ Phase', linestyle='-', color='b')
        ax2.plot(freq_, np.degrees(np.angle(b3_)), label='$Out_{3}$ Phase', linestyle='--', color='orange')
        ax2.plot(freq_, np.degrees(np.angle(a1_)), label='$In_{1}$ Phase', linestyle='-', color='green')
        ax2.plot(freq_, np.degrees(np.angle(a4_)), label='$In_{4}$ Phase', linestyle='--', color='purple')

        # Customize the phase subplot
        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Phase (Degrees)")
        ax2.set_title(f"{title} - Phase")
        ax2.legend(loc='upper right')
        ax2.grid()

        # Adjust layout for clarity
        fig.tight_layout()

        # Return the figure
        return fig, b2_, b3_
    else:
        return b2_, b3_

def feeder2port(title, block_smatrix, input1, freq_, plot):
    a1_ = input1
    s21_ = s_extract('s21', block_smatrix)

    # b2_amp_ = []
    # b2_phase_ = []
    b2_ = []

    # Multiplying input voltage with S params to get the output voltage
    for i in range(len(s21_)):
        b2_.append(s21_[i]*a1_[i])
        # b2_phase_.append((np.angle(s21_[i]) * np.angle(a1_[i])))

    # b2_ = [cmath.rect(mag, phase) for mag, phase in zip(b2_amp_, b2_phase_)]
    
    if plot:
        # Create a figure with two subplots (one row, two columns)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Plot amplitude in the first subplot (ax1)
        ax1.plot(freq_, np.abs(b2_), label='$Out_{2}$', linestyle='-')
        ax1.plot(freq_, np.abs(a1_), linestyle='--', label='$In_{1}$')

        # Customize the amplitude subplot
        ax1.set_xlabel("Frequency")
        ax1.set_ylabel("Amplitude")
        ax1.set_title(f"{title} - Amplitude")
        ax1.legend(loc='upper left')
        ax1.grid()

        # Plot phase in the second subplot (ax2)
        ax2.plot(freq_, np.degrees(np.angle(b2_)), label='$Out_{2}$ Phase', linestyle=':', color='b')
        ax2.plot(freq_, np.degrees(np.angle(a1_)), label='$In_{1}$ Phase', linestyle=':', color='green')

        # Customize the phase subplot
        ax2.set_xlabel("Frequency")
        ax2.set_ylabel("Phase (Degrees)")
        ax2.set_title(f"{title} - Phase")
        ax2.legend(loc='upper right')
        ax2.grid()

        # Adjust layout for clarity
        fig.tight_layout()

        return fig, b2_
    else:
        return b2_

def chain4ports(title, devices_sparam_list, input1, input2, cross_input, freq_, flipinput):
    inputa = input1
    inputb = input2

    for device in devices_sparam_list:
        index = np.where(devices_sparam_list == device)[0][0]
        
        if device.shape[1] == 4:      
            if cross_input[index]:      
                if not flipinput[index]:
                    b2_, b3_ = feeder4port('', device, input2, input1, freq_, False, False)
                else:
                    b2_, b3_ = feeder4port('', device, input2, input1, freq_, False, True)
            else:
                if not flipinput[index]:  # 0
                    b2_, b3_ = feeder4port('', device, input1, input2, freq_, False, False)
                else:                     # 1
                    b2_, b3_ = feeder4port('', device, input1, input2, freq_, False, True)

            input1 = b2_
            input2 = b3_

    # Create a figure with two subplots in one row
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plot amplitude on the left subplot (ax1)
    ax1.plot(freq_, np.abs(b2_), linestyle='-', label='$Out_{2}$')
    ax1.plot(freq_, np.abs(b3_), linestyle='--', label='$Out_{3}$')
    ax1.plot(freq_, np.abs(inputa), linestyle='-', label='$In_{1}$')
    ax1.plot(freq_, np.abs(inputb), linestyle='--', label='$In_{4}$')

    # Customize the left subplot
    ax1.set_xlabel("Frequency")
    ax1.set_ylabel("Amplitude")
    ax1.set_title(f"{title} - Amplitude")
    ax1.legend(loc='best')  # Legend for amplitude on the left
    ax1.grid(True)

    # Plot phase on the right subplot (ax2)
    ax2.plot(freq_, np.angle(b2_, deg=True), color='blue', linestyle='-', label='$Out_{2}$ Phase')
    ax2.plot(freq_, np.angle(b3_, deg=True), color='orange', linestyle='--', label='$Out_{3}$ Phase')
    # ax2.plot(freq_, np.degrees(np.angle(inputa)), color='purple', linestyle='-', label='$In_{1}$ Phase')
    # ax2.plot(freq_, np.degrees(np.angle(inputb)), color='green', linestyle='--', label='$In_{4}$ Phase')

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

    return fig, b2_, b3_


def chain2ports(title, devices_sparam_list, input1, freq_):
    inputa = input1  # Renamed to inputa for clarity in plots
    for device in devices_sparam_list:
        if device.shape[1] == 2:
            b2_ = feeder2port('', device, input1, freq_, False)

        input1 = b2_

    # Create a figure with two subplots in one row
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plot amplitude on the left subplot (ax1)
    ax1.plot(freq_, np.abs(b2_), label='$Out_{2}$', linestyle='-')
    ax1.plot(freq_, np.abs(inputa), linestyle='--', label='$In_{1}$', color='orange')

    # Customize the left subplot
    ax1.set_xlabel("Frequency")
    ax1.set_ylabel("Response")
    ax1.set_title(f"{title} - Amplitude")
    ax1.legend(loc='upper left')  # Legend for amplitude on the left
    ax1.grid(True)

    # Plot phase on the right subplot (ax2)
    ax2.plot(freq_, np.angle(b2_, deg=True), color='b', label='$Out_{2}$ Phase', linestyle='-')
    ax2.plot(freq_, np.angle(inputa, deg=True), color='orange', linestyle='--', label='$In_{1}$ Phase')

    # Customize the right subplot
    ax2.set_xlabel("Frequency")
    ax2.set_ylabel("Phase (Degrees)")
    ax2.set_title(f"{title} - Phase")
    ax2.legend(loc='upper right')  # Legend for phase on the right
    ax2.grid(True)

    # Adjust layout for clarity
    fig.tight_layout()

    return fig, b2_



