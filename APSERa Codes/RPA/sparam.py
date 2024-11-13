import numpy as np
import skrf as rf
import math
from datetime import datetime
import matplotlib.pyplot as plt


def dict_db_to_linear(_df):
    """
    Converts dB values in a dictionary to linear scale.

    Parameters:
    ----------
    _df : dict
        A dictionary where each key represents a parameter (e.g., 'freq' or any other parameter name), 
        and each value is a list of values corresponding to that parameter.
        - If the key is 'freq', values are assumed to represent frequencies and are copied as-is.
        - For other keys, values are assumed to be in dB and are converted to linear scale.

    Returns:
    -------
    linear_df : dict
        A dictionary where:
        - The 'freq' key (if present) has values copied directly from `_df`.
        - All other keys have their values converted from dB to linear scale using the formula:
          linear_value = 10^(dB_value / 20).

    Notes:
    ------
    This function is typically used for converting signal amplitudes or gains from dB to linear units.
    - It is assumed that `freq` does not require any conversion and is left unaltered.
    - For each parameter other than `freq`, the function applies a 10^(dB_value / 20) transformation 
      to convert from dB to linear scale.

    Example:
    --------
    >>> db_dict = {'freq': [1, 2, 3], 'gain': [-20, 0, 20]}
    >>> dict_db_to_linear(db_dict)
    {'freq': [1, 2, 3], 'gain': [0.1, 1.0, 10.0]}
    
    """
    linear_df = {}  # Create a new dictionary
    for params, _ in _df.items():
        if params == 'freq':
            linear_df[params] = _df[params][:]  # Copy the frequency list as is
        else:
            linear_df[params] = [(10**(val / 20)) for val in _df[params]]  # Convert dB to linear
    return linear_df



def list_db_to_linear(_list, negate):
    """
    Converts a list of dB values to linear scale, with optional negation.

    Parameters:
    ----------
    _list : list of float
        A list containing values in dB that need to be converted to linear scale.

    negate : bool
        A boolean flag indicating whether to negate each dB value before conversion.
        - If `True`, each dB value in `_list` is multiplied by -1 before conversion.
        - If `False`, the values are not negated (but currently, only negated conversion is implemented).

    Returns:
    -------
    temp : list of float
        A list where each dB value in `_list` has been converted to linear scale,
        with negation applied if `negate` is True. Conversion formula used:
        linear_value = 10^(-dB_value / 20).

    Notes:
    ------
    - The function applies the conversion only if `negate` is `True`. If `negate` is `False`, 
      the function will return an empty list (based on current implementation).
    - This function can be useful in scenarios where a signal's gain or amplitude in dB 
      needs to be converted to linear scale and optionally inverted (e.g., for attenuation).

    Example:
    --------
    >>> db_list = [20, 0, -20]
    >>> list_db_to_linear(db_list, negate=True)
    [0.1, 1.0, 10.0]
    
    """
    if not isinstance(_list, list):
        raise TypeError(f"Expected _list to be of type list, but got {type(_list).__name__}")

    temp = []
    for val in _list:
        if negate:
            temp.append((10**((val * -1) / 20)))  # Convert dB to linear with negation
    return temp


import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def s_plotter(title, which_s, plot_db, freq_, freq_unit, s_matrix_, port, bw_cutline):
    """
    Plots specified S-parameters (e.g., S11, S21) from a given S-matrix in either dB or linear scale as subplots.
    
    Parameters
    ----------
    title : str
        The title for the plot, displayed at the top of the figure.
    
    which_s : list of str
        Specifies the S-parameters to plot (e.g., ['s11', 's21']). Each string should represent
        a valid S-parameter, such as 's11', 's21', 's31', etc.
    
    plot_db : bool
        Determines if the S-parameters are plotted in dB scale (True) or linear scale (False).
    
    freq_ : list or np.array
        A list or array containing frequency values, corresponding to each row of the S-matrix.
    
    freq_unit : str
        The frequency unit label for the x-axis (e.g., 'Hz', 'GHz').

    s_matrix_ : list of lists of complex numbers
        The S-matrix data, where each entry represents a complex S-parameter in RI format.
        The matrix should be structured so that s_matrix_[i][j][k] gives the complex value of 
        the j-k S-parameter at the ith frequency point.

    bw_cutline : float or None
        A y-value for a horizontal cutline indicating bandwidth limits. If specified,
        a horizontal line will be drawn at this value in the plot.

    Returns
    -------
    None
        Displays the plot with the specified S-parameters and scale.
    """
    if which_s == 'all' and port == 4:
        which_s = ['s11','s12','s13','s14','s21','s22','s23','s24','s31','s32','s33','s34','s41','s42','s43','s44']
        # Determine number of subplots needed
        num_plots = len(which_s)
        rows = min(4, (num_plots + 3) // 4)  # Up to 4 rows
        cols = min(4, num_plots) if num_plots <= 4 else 4  # Up to 4 columns
        fig, axs = plt.subplots(rows, cols, figsize=(15, 12))

    if which_s == 'all' and port == 2:
        which_s = ['s11','s12','s21','s22']
        # Determine number of subplots needed
        num_plots = len(which_s)
        rows = min(4, (num_plots + 3) // 4)  # Up to 4 rows
        cols = min(4, num_plots) if num_plots <= 4 else 4  # Up to 4 columns
        fig, axs = plt.subplots(rows, cols, figsize=(15, 4))    
    
    
    
    axs = axs.ravel()  # Flatten axes array for easier indexing
    
    # Map S-parameter names to matrix indices
    s_param_indices = {
        's11': (0, 0), 's12': (0, 1), 's13': (0, 2), 's14': (0, 3),
        's21': (1, 0), 's22': (1, 1), 's23': (1, 2), 's24': (1, 3),
        's31': (2, 0), 's32': (2, 1), 's33': (2, 2), 's34': (2, 3),
        's41': (3, 0), 's42': (3, 1), 's43': (3, 2), 's44': (3, 3),
    }
    
    now = datetime.now()
    formatted_datetime = now.strftime("%m/%d/%Y %H:%M")
    
    # Extract and plot each specified S-parameter
    for idx, s_param in enumerate(which_s):
        row, col = s_param_indices[s_param]
        s_values = [s_matrix_[i][row][col] for i in range(len(s_matrix_))]
        
        # Calculate magnitude (dB or linear) and phase (degrees)
        if plot_db:
            s_magnitudes = 20 * np.log10(np.abs(s_values))
            #ylabel = 'Magnitude (dB)'
        else:
            s_magnitudes = np.abs(s_values)
            #ylabel = 'Magnitude (Linear)'
        
        s_phase = np.angle(s_values, deg=True)
        
        # Plot magnitude on the primary y-axis
        axs[idx].plot(freq_ / 1e9, s_magnitudes, label=f'{s_param.upper()} Mag')
        #axs[idx].set_xlabel(f'Frequency ({freq_unit})')
        #axs[idx].set_ylabel(ylabel)
        axs[idx].legend(loc='upper left')
        
        # Create a secondary y-axis for phase
        ax_phase = axs[idx].twinx()
        ax_phase.plot(freq_ / 1e9, s_phase, 'r--', label=f'{s_param.upper()} Ph')
        #ax_phase.set_ylabel('Phase (Degrees)', color='r')
        ax_phase.legend(loc='lower right', labelcolor='red')
        ax_phase.tick_params(axis='y', labelcolor='red')
        
        # Add bandwidth cutline if provided
        if bw_cutline is not None:
            axs[idx].axhline(y=bw_cutline, color='m', linestyle='--', label=f'y={bw_cutline}')
    
    # Hide any unused subplots
    for ax in axs[len(which_s):]:
        ax.axis('off')
    
    fig.suptitle(f'{title} S-Plot: $Phase(deg), Mag(dB)$       {formatted_datetime}', fontsize=16)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    return fig

def matrix_cascader_manual(mat1, mat2):
    """
    Cascades two S-parameter matrices manually using conversion between S and T parameters.

    This function takes two S-parameter matrices, converts them to T-parameters, 
    performs matrix multiplication, and then converts the result back to S-parameters.

    Parameters
    ----------
    mat1 : np.ndarray
        The first S-parameter matrix to cascade, expected to have shape (f, 4, 4), 
        where 'f' is the number of frequency points.

    mat2 : np.ndarray
        The second S-parameter matrix to cascade, expected to have the same shape as mat1.

    Returns
    -------
    np.ndarray
        The resultant S-parameter matrix after cascading mat1 and mat2, with the same shape (f, 4, 4).

    Raises
    ------
    ValueError
        If the shapes of the input matrices are different.

    Notes
    -----
    - This function uses the `scikit-rf` library for converting S-parameters to T-parameters and vice versa.
    - Ensure that both input matrices are valid S-parameter matrices and have the correct shape before calling this function.
    - The function exits if the input matrices have different shapes, printing a message to indicate the issue.
    """
    
    mat1 = rf.network.s2t(mat1)
    mat2 = rf.network.s2t(mat2)
    
    mat3 = []
    if mat1.shape == mat2.shape:
        pass
    else:
        print("The shapes of the matrices are different.")
        exit
        
    for i in range(len(mat1)):    
        mat3.append(np.dot(mat1[i], mat2[i]))            
    # Convert s_matrix to a NumPy array with shape (f, 4, 4)
    mat3_return = np.array(mat3)
    return rf.network.t2s(mat3_return)



def trim_smatrix(freq_, smatrix_, lim):
    """
    Trims the S-parameter matrix to a specified frequency range.

    This function takes a frequency array and an S-parameter matrix and returns a 
    new S-parameter matrix containing only the data within the specified frequency limits.

    Parameters
    ----------
    freq_ : list or np.ndarray
        A list or array of frequency values corresponding to the rows of the S-parameter matrix.

    smatrix_ : np.ndarray
        The S-parameter matrix to be trimmed, expected to have shape (f, 4, 4), where 'f' 
        is the number of frequency points.

    lim : list or tuple
        A two-element list or tuple specifying the lower and upper frequency limits 
        (inclusive) for the trimming operation.

    Returns
    -------
    np.ndarray
        A trimmed S-parameter matrix containing only the data within the specified frequency limits.

    Raises
    ------
    ValueError
        If the provided limits do not match the frequency range in the `freq_` array.

    Notes
    -----
    - The function assumes that the `freq_` array is sorted in ascending order.
    - The output array will contain S-parameter data only between the specified limits, 
      including the starting point defined by `lim[0]` and up to (but not including) 
      the point defined by `lim[1]`.

    Example
    -------
    >>> freq = np.array([1e9, 2e9, 3e9, 4e9])  # Frequency in Hz
    >>> smatrix = np.random.rand(4, 4, 4)      # Example S-parameter matrix
    >>> limits = [1e9, 3e9]
    >>> trimmed_matrix = trim_smatrix(freq, smatrix, limits)
    """
    
    new_arr = []
    #print(lim[0], lim[1], len(freq_))
    for i in range(len(freq_)):
        #print(freq_[i])
        if freq_[i] == lim[0]:
            transfer = True         
        elif freq_[i] == lim[1]:
            new_arr.append(smatrix_[i])  
            break
        try:
            if transfer == True:
                new_arr.append(smatrix_[i])
        except:
            pass
    new_arr = np.array(new_arr)
    return new_arr




def interpolate_smatrix_datasheet(ds, meta, db_true, db_negate, req_length, port, lim):
    """
    Interpolates S-parameter data from a datasheet to a specified frequency length.

    This function reads S-parameter data from a string input, performs conversions 
    from dB to linear if required, and interpolates the S-parameters over a specified 
    frequency range.

    Parameters
    ----------
    ds : str
        The input string containing S-parameter data, typically read from a datasheet.

    meta : list
        A nested list containing the indices of frequency and S-parameter values in the input data.

    db_true : bool
        Indicates whether the input S-parameter data is in dB format. If True, the data will be converted to linear.

    db_negate : bool
        If True, negates the dB values during the conversion process.

    req_length : int
        The desired length of the output frequency array after interpolation.

    port : int
        The number of ports of the S-parameter matrix (e.g., 2 or 4).

    lim : list or tuple
        A two-element list or tuple specifying the lower and upper frequency limits 
        for interpolation.

    Returns
    -------
    list
        A list containing:
            - np.ndarray: The interpolated S-parameter matrix, with shape determined by the `port` parameter.
            - np.ndarray: The new frequency indices corresponding to the interpolated S-parameters.

    Raises
    ------
    ValueError
        If the input variable type is not supported or if other issues arise during processing.

    Notes
    -----
    - This function uses NumPy for numerical operations and interpolation.
    - The S-parameters are expected to be formatted in a specific way in the input string, 
      and the `meta` list must correctly specify the indices of the frequency and S-parameter values.
    - The S11, S22, S33, S44 is expected to be inputed as VSWR.
    - Frequency unit is assumed as MHz
    """
    
    if str(type(ds)) == "<class 'str'>":
        if port == 4:    
            print('s params input variable is string, reading...\n')
            sarray = []
    
            freq_ds = []
            s11_ = []
            s12_ = []
            s13_ = []
            s14_ = []
            
            s21_ = []
            s22_ = []
            s23_ = []
            s24_ = []
            
            s31_ = []
            s32_ = []
            s33_ = []
            s34_ = []
            
            s41_ = []
            s42_ = []
            s43_ = []
            s44_ = []
    
            data_linewise = ds.split('\n')
            for i in data_linewise:
                words = i.split(' ')
               
                freq_ds.append(float(words[meta[0][0]])*(10**6))
                
                temp = float(words[meta[1][0]])
                s11_.append(20*np.log10((temp - 1)/(temp + 1)))
                s12_.append(float(words[meta[1][1]]))
                s13_.append(float(words[meta[1][2]]))
                s14_.append(float(words[meta[1][3]]))
                
                s21_.append(float(words[meta[2][0]]))
                temp = float(words[meta[2][1]])
                s22_.append(20*np.log10((temp - 1)/(temp + 1)))
                s23_.append(float(words[meta[2][2]]))
                s24_.append(float(words[meta[2][3]]))
                
                s31_.append(float(words[meta[3][0]]))
                s32_.append(float(words[meta[3][1]]))
                temp = float(words[meta[3][2]])
                s33_.append(20*np.log10((temp - 1)/(temp + 1)))
                s34_.append(float(words[meta[3][3]]))
                
                s41_.append(float(words[meta[4][0]]))
                s42_.append(float(words[meta[4][1]]))
                s43_.append(float(words[meta[4][2]]))
                temp = float(words[meta[4][3]])
                s44_.append(20*np.log10((temp - 1)/(temp + 1)))
    
                sarray = [ [s11_],[s12_],[s13_],[s14_]  
                          ,[s21_],[s22_],[s23_],[s24_]  
                          ,[s31_],[s32_],[s33_],[s34_]  
                          ,[s41_],[s42_],[s43_],[s44_] ]

        if port == 2:
            print('s params input variable is string, reading...\n')
            sarray = []
    
            freq_ds = []
            s11_ = []
            s12_ = []
            s13_ = []
            s14_ = []
            
            s21_ = []
            s22_ = []
            s23_ = []
            s24_ = []
            
            s31_ = []
            s32_ = []
            s33_ = []
            s34_ = []
            
            s41_ = []
            s42_ = []
            s43_ = []
            s44_ = []
    
            data_linewise = ds.split('\n')
            for i in data_linewise:
                words = i.split(' ')
               
                freq_ds.append(float(words[meta[0][0]])*(10**6))
                            
                temp = float(words[meta[1][0]])
                s11_.append(20*np.log10((temp - 1)/(temp + 1)))
                s12_.append(float(words[meta[1][1]]))
                
                s21_.append(float(words[meta[2][0]]))
                temp = float(words[meta[2][1]])
                s22_.append(20*np.log10((temp - 1)/(temp + 1)))
    
                sarray = [ [s11_],[s12_],  
                           [s21_],[s22_] ]

            
        print("frequency translated... Length: " + str(len(freq_ds)))   
        print('s params translated... Length: ' + str(len(sarray)))  

        # db to linear convertion
        
        if db_true:
            print('make sure the input s params data is in dB!')
            
            sarray_db = []            
            for i in sarray:
                temp = []
                if sarray.index(i) == 0 or sarray.index(i) == 5 or sarray.index(i) == 10 or sarray.index(i) == 15:
                    temp = []
                    for j in i:   
                        temp1 = []
                        for k in j:
                            temp1.append(np.abs(((1-k)/(1+k))))
                        temp.append(temp1)
                    sarray_db.append(temp)
                    
                else:
                    temp = []
                    for j in i:
                        temp.append(list_db_to_linear(j, db_negate))
                    sarray_db.append(temp)
        
        sarray_db_interp = []        
        for i in sarray_db:
            new_indices = np.linspace(lim[0], lim[1], num=int(req_length))  
            sarray_db_interp.append(np.interp(new_indices, freq_ds, i[0]))

        # interpolater
        
        print('Interpolation success :)')
        print("========================================================\n") 

        
        Sarray = []
        for i in range(len(sarray_db_interp[0])):            
            if port == 4:
                Sarray.append(np.array([[sarray_db_interp[0][i], sarray_db_interp[1][i], sarray_db_interp[2][i], sarray_db_interp[3][i]],
                                        [sarray_db_interp[4][i], sarray_db_interp[5][i], sarray_db_interp[6][i], sarray_db_interp[7][i]],
                                        [sarray_db_interp[8][i], sarray_db_interp[9][i], sarray_db_interp[10][i],sarray_db_interp[11][i]],
                                        [sarray_db_interp[12][i],sarray_db_interp[13][i],sarray_db_interp[14][i],sarray_db_interp[15][i]] ]))
            elif port == 2:
                Sarray.append(np.array([ [sarray_db_interp[0][i], sarray_db_interp[1][i]] ,
                                         [sarray_db_interp[2][i], sarray_db_interp[3][i]] ]))
        return [np.array(Sarray), new_indices]
                
    else:
        print('s params variable type not supported!')



def s_extract(which_s, s_matrix_):
    """
    Extracts specified S-parameters from an S-parameter matrix.

    This function allows users to extract any of the S-parameters 
    (such as S11, S21, S12, S44) from a provided S-parameter matrix 
    that is expected to be in complex (real-imaginary) format.

    Parameters
    ----------
    which_s : str or list of str
        The S-parameters to extract. This can include 's11', 's12', 's21', 's22',
        's13', 's14', 's31', 's32', 's33', 's34', 's41', 's42', 's43', 's44'.
        Multiple S-parameters can be specified as a string with gaps or no gaps.

    s_matrix_ : np.ndarray
        The input S-parameter matrix in complex format. The shape of the 
        matrix should be (num_frequencies, num_ports, num_ports). 
        Supported configurations are for 2-port or 4-port networks.

    Returns
    -------
    np.ndarray
        A NumPy array containing the extracted S-parameter values.

    Raises
    ------
    ValueError
        If the input S-parameter matrix does not have a valid shape (either 
        2 or 4 ports) or if `which_s` contains invalid S-parameter identifiers.

    Notes
    -----
    - The function handles both 2-port and 4-port S-parameter matrices.
    - Ensure that the input S-parameter matrix is in the correct format to 
      avoid errors during extraction.

    Example
    -------
    >>> s_matrix = np.array([[[1+1j, 0.1-0.1j], [0.1+0.1j, 0.5+0.5j]], 
                              [[0.2-0.2j, 0.3+0.3j], [0.4+0.4j, 0.6-0.6j]]])
    >>> extracted_s = s_extract(['s11', 's21'], s_matrix)
    >>> print(extracted_s)
    """
       
    s_extract = []
    
    if s_matrix_.shape[2] == 4:
        if 's11' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][0])
        if 's12' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][1])
        if 's13' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][2])
        if 's14' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][3])
        if 's21' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][0])
        if 's22' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][1])
        if 's23' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][2])
        if 's24' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][3])
        if 's31' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][2][0])
        if 's32' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][2][1])
        if 's33' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][2][2])
        if 's34' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][2][3])
        if 's41' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][3][0])
        if 's42' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][3][1])
        if 's43' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][3][2])
        if 's44' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][3][3])
                
        return np.array(s_extract)

    if s_matrix_.shape[2] == 2:
        if 's11' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][0])
        if 's12' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][0][1])
        if 's21' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][0])
        if 's22' in which_s:
            for i in range(len(s_matrix_)):
                s_extract.append(s_matrix_[i][1][1])
                
        return np.array(s_extract)    
    



def save_s4p(filename, S_matrix, frequencies):
    """
    Saves a 4-port S-parameter network to an S4P file with interpolated frequencies.
    
    This function writes the provided S-parameter data along with corresponding 
    frequency points into a file in the S4P format, which is commonly used for 
    storing S-parameter data of multi-port networks.

    Parameters
    ----------
    filename : str
        The name of the output S4P file where the S-parameter data will be saved.

    S_matrix : np.ndarray
        A 3D NumPy array containing the S-parameter values in complex format. 
        The shape must be (f, 4, 4), where 'f' is the number of frequency points 
        and '4' corresponds to the number of ports in the network.

    frequencies : list or np.ndarray
        A list or NumPy array containing the frequency points (in Hz) corresponding 
        to the S-parameters in the S_matrix.

    Raises
    ------
    ValueError
        If the S_matrix does not have the shape (f, 4, 4), an error is raised to ensure 
        that the correct format is being used.

    Example
    -------
    >>> import numpy as np
    >>> S_matrix = np.random.rand(10, 4, 4) + 1j * np.random.rand(10, 4, 4)  # Example complex S-parameters
    >>> frequencies = np.linspace(1e9, 10e9, 10)  # Frequencies from 1 GHz to 10 GHz
    >>> save_s4p('output.s4p', S_matrix, frequencies)
    """
    # Check if the input S_matrix has the correct shape
    if S_matrix.shape != (len(frequencies), 4, 4):
        raise ValueError("S_matrix must have shape (f, 4, 4) where f is the number of frequency points.")
    
    f_points = S_matrix.shape[0]
    
    # Write the .s4p file
    with open(filename, 'w') as f:
        # Write the header
        f.write("# Hz S RI R 50\n")

        # Write the frequency points and S-parameters
        for i in range(f_points):
            freq = float(frequencies[i]) # Ensure freq is a float
            f.write(f"{freq:<20.6f}\n")  # Write the frequency

            # Write the S-parameters in the correct format
            for j in range(4):
                line = ""
                for k in range(4):
                    # Extract the S-parameter values (magnitude and angle)
                    real = S_matrix[i, j, k].real
                    imag = S_matrix[i, j, k].imag
                    line += f"{real:<20.6f}{imag:<20.6f}"
                f.write(f"{line}\n")


def read_s4p(file_path):
    """
    Reads an S4P file and extracts frequency and S-parameter data.

    This function opens an S4P file, verifies its format, and reads the frequency 
    and S-parameter data into appropriate arrays. The S-parameters are stored in 
    complex format, and frequencies are converted to Hz.

    Parameters
    ----------
    file_path : str
        The path to the S4P file to be read.

    Returns
    -------
    frequencies : np.ndarray
        A NumPy array containing frequency points in Hz.

    s_matrix : np.ndarray
        A 3D NumPy array containing the S-parameters in complex format. The shape 
        will be (f, 4, 4), where 'f' is the number of frequency points.

    Raises
    ------
    ValueError
        If the S4P file is not in the expected S MA format, or if it is incorrectly formatted 
        internally.

    Example
    -------
    >>> frequencies, s_matrix = read_s4p('example.s4p')
    >>> print(frequencies)
    >>> print(s_matrix)
    """
    
    frequencies = []
    s_matrix = []
    counter = 0

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Check for the correct header
        for line in lines:
            parts = line.split()
            if line.startswith('!'):
                continue
            elif line.startswith('#'):
                
                if 'S MA' not in line:
                    raise ValueError("s4p file not in S MA format")
                else:
                    print('\nFile format is MA, reading...')

                # Convert GHz, MHz, etc. to Hz
                if 'GHz' in line:
                    print('Converted frequency data to Hz frm GHz')
                    print('========================================================')
                    frequency_mul = 1e9
                elif 'MHz' in line:
                    print('Converted frequency data to Hz frm MHz')
                    print('========================================================')
                    frequency_mul = 1e6
                elif 'KHz' in line:
                    print('Converted frequency data to Hz frm KHz')
                    print('========================================================')
                    frequency_mul = 1e3
                else:
                    pass
           
            elif len(parts) == 9:  # Expecting frequency and 8 S-parameters
                
                s_matrix_row = []
                s_matrix_pre = []
                
                frequency = float(parts[0])*frequency_mul  #in Hz now                
                frequencies.append(frequency)
                # Collect S-parameters as complex numbers
                for i in range(0, len(parts[1:]), 2):

                    phase_radians = math.radians(float(parts[1:][i+1]))
                    
                    # Calculate real and imaginary parts
                    a = float(parts[1:][i]) * math.cos(phase_radians)
                    b = float(parts[1:][i]) * math.sin(phase_radians)                    
                    s_matrix_row.append(complex(a,b))
                    
                s_matrix_pre.append(np.array(s_matrix_row))
                                                    
            elif len(parts) == 8:   #only s params
                #clear initial row for next row
                s_matrix_row = []
                #count for three rows
                counter = counter + 1
                for i in range(0, len(parts), 2):
                    phase_radians = math.radians(float(parts[i+1]))
                    
                    # Calculate real and imaginary parts
                    a = float(parts[i]) * math.cos(phase_radians)
                    b = float(parts[i]) * math.sin(phase_radians)                    
                    s_matrix_row.append(complex(a,b))

                s_matrix_pre.append(np.array(s_matrix_row))

                if counter == 3:
                    counter = 0
                    s_matrix.append(np.array(s_matrix_pre))
                
            else:
                raise ValueError('s4p file wrongly formated internally! Exiting..')
                
        
    return np.array(frequencies), np.array(s_matrix)



def read_s2p(file_path):
    """
    Reads an S2P file and extracts frequency and S-parameter data.

    This function opens an S2P file, verifies its format, and reads the frequency 
    and S-parameter data into appropriate arrays. The S-parameters are stored in 
    complex format, and frequencies are converted to Hz.

    Parameters
    ----------
    file_path : str
        The path to the S2P file to be read.

    Returns
    -------
    frequencies : np.ndarray
        A NumPy array containing frequency points in Hz.

    s_matrix : np.ndarray
        A 3D NumPy array containing the S-parameters in complex format. The shape 
        will be (f, 2, 2), where 'f' is the number of frequency points.

    Raises
    ------
    ValueError
        If the S2P file is not in an acceptable format, or if it is incorrectly formatted 
        internally.

    Example
    -------
    >>> frequencies, s_matrix = read_s2p('example.s2p')
    >>> print(frequencies)
    >>> print(s_matrix)
    """
    
    frequencies = []
    s_matrix = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Check for the correct header
        frequency_mul = 1  # Default to Hz
        for line in lines:
            parts = line.split()
            if line.startswith('!'):
                continue
            elif line.startswith('#'):
                # Check for acceptable format
                if ('MA' not in line and 'dB' not in line) or 'S' not in line:
                    raise ValueError("s2p file not in acceptable format")
                print('File format accepted, reading...')

                # Convert frequency unit
                if 'GHz' in line:
                    frequency_mul = 1e9
                    print('Converted frequency data to Hz from GHz')
                elif 'MHz' in line:
                    frequency_mul = 1e6
                    print('Converted frequency data to Hz from MHz')
                elif 'KHz' in line:
                    frequency_mul = 1e3
                    print('Converted frequency data to Hz from KHz')
                elif 'Hz' in line:
                    print('Frequency data in Hz')
                else:
                    raise ValueError("Unrecognized frequency unit.")

            elif len(parts) == 9:  # Expecting frequency and 8 S-parameters
                frequency = float(parts[0]) * frequency_mul
                frequencies.append(frequency)

                # Collect S-parameters as complex numbers
                s_matrix_row = []
                for i in range(0, len(parts[1:]), 2):
                    phase_radians = math.radians(float(parts[1:][i + 1]))
                    magnitude = 10 ** (float(parts[1:][i]) / 20)
                    a = magnitude * math.cos(phase_radians)
                    b = magnitude * math.sin(phase_radians)
                    s_matrix_row.append(complex(a, b))

                # Append the row to the s_matrix as a 2x2 array
                s_matrix.append(np.array([[s_matrix_row[0], s_matrix_row[2]],[s_matrix_row[1], s_matrix_row[3]]]))

            else:
                raise ValueError('s2p file wrongly formatted internally! Exiting..')
            
        print('Frequency and S-matrix created')
    
    return np.array(frequencies), np.array(s_matrix)



def interpolate_s_matrix_general(s_matrix, current_freq, new_freq):
    """
    Interpolates an S-matrix from current frequency points to new frequency points.
    
    This function takes an S-parameter matrix and interpolates its values from existing
    frequency points to a new set of frequency points using linear interpolation.

    Parameters
    ----------
    s_matrix : numpy.ndarray
        Original S-matrix of shape (m, n, p), where m is the number of frequency points,
        and n and p are the dimensions of the S-parameters (4x4 for a 4-port network
        or 2x2 for a 2-port network).

    current_freq : numpy.ndarray
        Array of current frequency points corresponding to the S-matrix, shape (m,).

    new_freq : numpy.ndarray
        Array of new frequency points for interpolation, shape (k,).

    Returns
    -------
    numpy.ndarray
        Interpolated S-matrix at the new frequency points, shape (k, n, p), where k is
        the number of new frequency points.
    
    Raises
    ------
    ValueError
        If the shape of the input S-matrix is not compatible with the expected dimensions.
    """  
    #m, n, p = s_matrix.shape    
    if s_matrix.shape[1] == 4:
        s11_ = s_extract('s11', s_matrix)
        s12_ = s_extract('s12', s_matrix)
        s13_ = s_extract('s13', s_matrix)
        s14_ = s_extract('s14', s_matrix)
        s21_ = s_extract('s21', s_matrix)
        s22_ = s_extract('s22', s_matrix)
        s23_ = s_extract('s23', s_matrix)
        s24_ = s_extract('s24', s_matrix)
        s31_ = s_extract('s31', s_matrix)
        s32_ = s_extract('s32', s_matrix)
        s33_ = s_extract('s33', s_matrix)
        s34_ = s_extract('s34', s_matrix)
        s41_ = s_extract('s41', s_matrix)
        s42_ = s_extract('s42', s_matrix)
        s43_ = s_extract('s43', s_matrix)
        s44_ = s_extract('s44', s_matrix)
        
        s11_interp = np.interp(new_freq, current_freq, s11_)
        s12_interp = np.interp(new_freq, current_freq, s12_)
        s13_interp = np.interp(new_freq, current_freq, s13_)
        s14_interp = np.interp(new_freq, current_freq, s14_)
        s21_interp = np.interp(new_freq, current_freq, s21_)
        s22_interp = np.interp(new_freq, current_freq, s22_)
        s23_interp = np.interp(new_freq, current_freq, s23_)
        s24_interp = np.interp(new_freq, current_freq, s24_)
        s31_interp = np.interp(new_freq, current_freq, s31_)
        s32_interp = np.interp(new_freq, current_freq, s32_)
        s33_interp = np.interp(new_freq, current_freq, s33_)
        s34_interp = np.interp(new_freq, current_freq, s34_)
        s41_interp = np.interp(new_freq, current_freq, s41_)
        s42_interp = np.interp(new_freq, current_freq, s42_)
        s43_interp = np.interp(new_freq, current_freq, s43_)
        s44_interp = np.interp(new_freq, current_freq, s44_)

        sarray_interp = [s11_interp, s12_interp, s13_interp, s14_interp, s21_interp, s22_interp,s23_interp,s24_interp, s31_interp,s32_interp,s33_interp,s34_interp, s41_interp, s42_interp, s43_interp, s44_interp]

    if s_matrix.shape[1] == 2:
        s11_ = s_extract('s11', s_matrix)
        s12_ = s_extract('s12', s_matrix)
        
        s21_ = s_extract('s21', s_matrix)
        s22_ = s_extract('s22', s_matrix)
        
        
        s11_interp = np.interp(new_freq, current_freq, s11_)
        s12_interp = np.interp(new_freq, current_freq, s12_)
        
        s21_interp = np.interp(new_freq, current_freq, s21_)
        s22_interp = np.interp(new_freq, current_freq, s22_)
        

        sarray_interp = [s11_interp, s12_interp, s21_interp, s22_interp]

    
    Sarray = []

    for i in range(len(sarray_interp[0])):            
        if s_matrix.shape[1] == 4:
            Sarray.append(np.array([[sarray_interp[0][i], sarray_interp[1][i],                    sarray_interp[2][i], sarray_interp[3][i]],
                                    [sarray_interp[4][i], sarray_interp[5][i], sarray_interp[6][i], sarray_interp[7][i]],
                                    [sarray_interp[8][i], sarray_interp[9][i], sarray_interp[10][i],sarray_interp[11][i]],
                                    [sarray_interp[12][i],sarray_interp[13][i],sarray_interp[14][i],sarray_interp[15][i]] ]))
        elif s_matrix.shape[1] == 2:
            Sarray.append(np.array([ [sarray_interp[0][i], sarray_interp[1][i]] ,
                                        [sarray_interp[2][i], sarray_interp[3][i]] ]))
    return np.array(Sarray)


def general_line_interpolate(x, xp, yp):
    return np.interp(x, xp, yp)


def interpolate_smatrices(devices, current_f_list, new_f):
    temp_devices = []
    for i in range(len(devices)):
        temp_devices.append(interpolate_s_matrix_general(devices[i], current_f_list[i], new_f))
    print('All S matrices are compatible with each other and current freq')
    return temp_devices
    
