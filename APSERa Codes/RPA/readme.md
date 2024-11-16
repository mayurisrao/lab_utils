# Rf chain Pipeline for APSERa 1.0

This pipeline performs the simulation of the pipeline from Transfer switch till the correlator out. 
The blocks defined in the pipeline are Switch, Rat Race coupler and amplifier.
There is a ideal block generater which generates the ideal s-matrix equations or we can also load the measures s-matrices from the s4p files or datasheets.
We can feed inputs into the rf chain to get the final outputs.

RPA 1.0 features include:
- No perturbation to the idealities of RRC or system.
- No reflections considered in the system, and only contributions from the s-matrix accounted for.

### Installation
Install the whole dir of RPA. Create a venv with python 3.10.12 and install the required packages with the requirements.txt.
We are ready to run RPA now.

## Description of Pipeline

The pipeline is split into _main.ipynb_, and a bunch of _py files_ that are imported into the main.ipynb and used in the computation.
We will explore each one of them and describe their functionalities. 

- import.py - Has all the imports
- sparam.py - Contains all functions for s parameter related algebra, manipulation, reading and saving as s4p/s2p files.
- devices.py - Has all the devices used in the rf chain which include ideal amplifier, ideal rat race coupler, ideal switch (on/off configurations),
  correlator, chaining, feeder.
- sources.py - Contains source signal generators with and signal manipulators to convert temperature signal to voltage.
- main.ipynb - Main driver. Contains the pipeline call as apsera_pipeline.

```
            |                          |
            |                          |
    +---------------------------------------------+
    |                  Transfer Switch            |
    +-------+-----------+--------------+----------+
            |                          |
            |                          |
    +-------+--------------------------+----------+
    |                  Rat Race Coupler           |
    +-------+--------------------------+----------+
            |                          |
            |                          |                 
    +-------+-----+             +------+------+            
    | Amplifier 1 |             | Amplifier 2 |          
    +-------------+             +-------------+          
            |                          |
            |     +-------v-------+    |
            +-----|  Correlator   |----+                                      
                  +-------+-------+                
                          |                         
                        Output              
```                                
                                    
## Decription of functions:
### <u>sparam.py</u>


- **dict_db_to_linear**

  Converts a dictionary (with first key as frequency and remaining as s parameters) from db scale to linear scale.
  ```python
    Example:
    --------
    >>> db_dict = {'freq': [1, 2, 3], 's11': [-20, 0, 20], , 's12': [-20, 0, 20], , 's21': [-20, 0, 20], , 's22': [-20, 0, 20]}
    >>> dict_db_to_linear(db_dict)
    {'freq': [1, 2, 3], 'gain': [0.1, 1.0, 10.0]}
  ```
  
- **list_db_to_linear**

  Convert a list from db to linear units.
  ```python
    Example:
    --------
    >>> db_list = [20, 0, -20]
    >>> list_db_to_linear(db_list, negate=True)
    [0.1, 1.0, 10.0]
  ```
- **s_plotter(title, which_s, plot_db, freq_, freq_unit, s_matrix_, port, bw_cutline)**
  
  provide title, which S params to plot, if to plot as db type True, frequency values, frequency unit, s_matrix, no.of port, draw a horizontal line.
  Plots specified S-parameters (e.g., S11, S21) from a given S-matrix in either dB or linear scale as subplots.

  ```python
    Example:
    -------
    _ = s_plotter('switch ideal off', 'all', True, apsera_freq, 'GHz', switch_ideal_off, 4, None)
  ```
- **matrix_cascader_manual(mat1, mat2)**

  Cascades two S-parameter matrices manually using conversion between S and T parameters.
    This function takes two S-parameter matrices, converts them to T-parameters, 
    performs matrix multiplication, and then converts the result back to S-parameters.
  
- **trim_smatrix(freq_, smatrix_, lim)**

  Trims the S-parameter matrix to a specified frequency range.
    This function takes a frequency array and an S-parameter matrix and returns a 
    new S-parameter matrix containing only the data within the specified frequency limits.
  
- **interpolate_smatrix_datasheet(ds, meta, db_true, db_negate, req_length, port, lim)**

    Interpolates S-parameter data from a datasheet to a specified frequency length.
    This function reads S-parameter data from a string input, performs conversions 
    from dB to linear if required, and interpolates the S-parameters over a specified 
    frequency range.
  ```python
    Example:
    -------
    #load Transfer switch and interpolate to required length
    [sparams_switch_on, _] = interpolate_smatrix_datasheet(ds=transferswitch_datasheet, meta=transferswitch_metadata_on, db_true=True, db_negate=True, req_length=1030, port=4, lim=[1e9,5e9])
  ```
- **s_extract(which_s, s_matrix_)**

  Extracts specified S-parameters from an S-parameter matrix.
    This function allows users to extract any of the S-parameters 
    (such as S11, S21, S12, S44) from a provided S-parameter matrix 
    that is expected to be in complex (real-imaginary) format.
  ```python
    Example
    -------
    >>> extracted_s = s_extract(['s11', 's21'], s_matrix)
  ```

- **save_s4p(filename, S_matrix, frequencies)**

    Saves a 4-port S-parameter network to an S4P file with interpolated frequencies.    
    This function writes the provided S-parameter data along with corresponding 
    frequency points into a file in the S4P format, which is commonly used for 
    storing S-parameter data of multi-port networks.
  ```python
    Example
    -------
    >>> save_s4p('output.s4p', S_matrix, frequencies)
  ```

- **read_s4p(file_path)**
    Reads an S4P file and extracts frequency and S-parameter data.
    This function opens an S4P file, verifies its format, and reads the frequency 
    and S-parameter data into appropriate arrays. The S-parameters are stored in 
    complex format, and frequencies are converted to Hz.
  ```python
    Example
    -------
    >>> frequencies, s_matrix = read_s4p('example.s4p')
  ```

- **read_s2p(file_path)**
  
    Reads an S2P file and extracts frequency and S-parameter data.
    This function opens an S2P file, verifies its format, and reads the frequency 
    and S-parameter data into appropriate arrays. The S-parameters are stored in 
    complex format, and frequencies are converted to Hz.
  ```python
    Example
    -------
    >>> frequencies, s_matrix = read_s4p('example.s2p')
  ```

- **interpolate_s_matrix_general(s_matrix, current_freq, new_freq)**

  Interpolates an S-matrix from current frequency points to new frequency points.    
    This function takes an S-parameter matrix and interpolates its values from existing
    frequency points to a new set of frequency points provided as new_freq using linear interpolation. 

  ```python
    Example
    -------
    >>> amp = interpolate_s_matrix_general(sparams_amp, freq_amp, apsera_freq)
  ```

- **general_line_interpolate(x, xp, yp)**

  Uses general numpy interolater np.interp to get new data points x.

- interpolate_smatrices(devices, current_f_list, new_f)

  Runs the interpolate_s_matrix_general for mulitple devices. 

  ```python
    Example
    -------
    >>> rrc, switch_on, switch_off = interpolate_smatrices(devices=[sparams_rrc, sparams_switch_on, sparams_switch_off], current_f_list=[freq_rrc]*3, new_f=apsera_freq)
  ```


### <u>devices.py</u>

  
  
- **ideal_switch_gen(freq, switchon)**

  Generates an ideal transfer switch S-parameter matrix in complex form. This function creates an S-parameter matrix for a 4-port ideal switch 
    based on given frequency points. The S-parameters are expressed in dB.
  ```python
    Example
    -------
    >>>   s_matrix = ideal_switch_gen(freq_points)
  ```

- **ideal_rrc_gen(freq_)**

  Generates an ideal rat race coupler (RRC) S-parameter matrix in complex form.
    This function creates an S-parameter matrix for a 4-port ideal rat race coupler
    filter based on given frequency points. The S-parameters are expressed in complex 
    values representing the filter characteristics.

   ```python
    Example
    -------
    >>>   s_matrix = ideal_rrc_gen(freq_points)
    ```

- **ideal_amp_gen(freq_, gain)**

  Generates an ideal amplifier (no phase lag) S-parameter matrix in complex form for a gain.
    This function creates an S-parameter matrix for a 2-port ideal amplifier based on
    given frequency points. The S-parameters represent the reflection and transmission 
    characteristics of the amplifier.
  
   ```python
    Example
    -------
    >>>   s_matrix = ideal_amp_gen(freq_points, 3)
    ```

- **correlator(input1, input2, x)**

  Correlate two inputs for a given frequency range x

   ```python
    Example
    -------
    >>>   fig_corr_ideal, t_obs01 = correlator(input1=b2_top_ideal_on[1], input2=b2_bottom_ideal_on[1], x=apsera_freq)
   ```

- **feeder2port(block_smatrix, input, freq_)**

  Feed input (a, voltage signal) to a two port device and get its output (b, voltage signals) using the S matrix of the device.
  Only transmission effects are considered from all ports. No reflections are considered. 

  ```python
    Example
    -------
    >>>   b_ = feeder2port(device, input, freq_)
  ```

- **feeder4port(block_smatrix, input, freq_)**
  
  Feed input (a, voltage signal) to a four port device and get its output (b, voltage signals) using the S matrix of the device.
  Only transmission effects are considered from all ports. No reflections are considered. 
  
  ```python
    Example
    -------
    >>>   b_ = feeder2port(device, input, freq_)
  ```

- **chain4ports(title, devices_sparam_list, input, freq_)**
  
  Chain four port devices and feed input (a, voltage signal) to ports of first four port device. And get the output (b, voltage signals) from the output of the last device.
  Since it is chained give inputs to port 1 and 4 of first device and take outputs from port 2 and 3 of last device. Uses feeder4port in backend.
  Only transmission effects are considered from all ports. No reflections are considered. 
  
  ```python
    Example
    -------
    >>>   _, b_rrc_ideal = chain4ports(
                              title='ideal switch+rrc', 
                              devices_sparam_list=[switch_ideal_on, rrc_ideal], 
                              input=[noisy_V_nu_amp, [0]*len(apsera_freq), [0]*len(apsera_freq), noise_300],  
                              freq_=apsera_freq     )
  ```
  
- **chain2ports(title, devices_sparam_list, input, freq_)**
  
   Chain two port devices and feed input (a, voltage signal) to ports of first two port device. And get the output (b, voltage signals) from the output of the last device.
    Since it is chained give inputs to port 1 of first device and take outputs from port 2 last device. Uses feeder2port in backend.
    Only transmission effects are considered from all ports. No reflections are considered. 
    
    ```python
      Example
      -------
      >>>   _, V_nu_amp = chain2ports(
                            title='amp antenna', 
                            devices_sparam_list=[amp_ideal_40], 
                            input=[V_nu, [0]*len(apsera_freq)], 
                            freq_=apsera_freq    )
    ```

### <u>sources.py</u>
- **gen_VSD_50(temp, b, length)**
  
    Generates an Voltage Spectral Density based on Additive White Gaussian Noise (AWGN) source for given temperature 
    and bandwidth parameters.
    This function computes the noise voltage for a given temperature (in Kelvin), 
    bandwidth (in Hertz), and the length of the noise signal frequency points.
  
  ```python
    Example
    -------
    >>>   noise_samples = noise_50(300, 1e6, 1000)
  ```

- **TA_to_V(file, R)**

  Read residuals from a computed residual file, load the temperature (K) and convert it into voltage values.

  ```python
    Example
    -------
    >>>   V_nu, apsera_freq = TA_to_V(file='residues.txt', R=50)
  ```
### <u>main.ipynb</u>

- rf_chain_simulate(switch_on_, switch_off_, rrc_, amp_, input): This functions contains the RF Chain from Transfer switch to correlator output as in version 2 of APSERa schematic.
  Supply the switch on and off, rrc and amplifier s matrices and the input a matrix. Output will be:

  `Tobs_ideal = t_obs00 - t_obs01  # crossed (on) - through (off)`

  Output will be the Voltage corresponding to Tobs_ideal. Since it is chained the input to port 1 and 4 of a matrix.
  
  ```python
    Example
    -------
    >>>   Tobs_ideal = rf_chain_simulate(switch_on, switch_off, rrc, amp, [input_, noise_300_])
  ```

- **apsera_pipeline(input_, switch_on, switch_off, rrc, amp)**

  Takes all input devices and performs the entire extraction of the input antenna signal. Uses rd_chain_simulate in backend. It performs three cases: Antenna temperature and 300K noise,
  Coldload and 300K noise, Hotload and 300K noise. And extracts the antenna temperature after it flows through the chain. Using the following equations below.
 
  ```python
    # Ideal Observation Time
    Tobs_ideal = rf_chain_simulate(switch_on, switch_off, rrc, amp, [input_, noise_300_])
    
    ### COLD LOAD
    Tcold = rf_chain_simulate(switch_on, switch_off, rrc, amp, [cold_, noise_300_])
    
    ### HOT LOAD
    Thot = rf_chain_simulate(switch_on, switch_off, rrc, amp, [hot_, noise_300_])
    
    # Extract antenna temperature
    T_a_reflected = ((Tobs_ideal - Tcold) * (hotload_vsd - coldload_vsd)) / (Thot - Tcold) + coldload_vsd
  ```
