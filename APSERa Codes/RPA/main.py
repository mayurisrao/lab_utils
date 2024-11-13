from imports import *
from sparam import *
from sources import *
from devices import *

#load the rrc s4p file
freq_rrc, sparams_rrc = read_s4p('MS_SL_Transition_v32_taper_v2.s4p')

# Transfer switch data from manual
transferswitch_datasheet = '''1000.0 0.04 0.04 92.45 100.96 1.01 1.01 1.01 1.01 120.0
1500.0 0.05 0.05 98.61 87.38 1.01 1.01 1.01 1.01 120.0
2000.0 0.06 0.06 100.79 97.34 1.01 1.02 1.01 1.01 120.0
2500.0 0.07 0.06 97.51 104.72 1.03 1.03 1.03 1.02 120.0
3000.0 0.07 0.07 93.32 102.92 1.05 1.05 1.04 1.04 120.0
3500.0 0.08 0.08 98.46 99.72 1.06 1.07 1.05 1.05 120.0
4000.0 0.08 0.08 95.89 93.03 1.07 1.09 1.06 1.06 120.0
4500.0 0.09 0.09 92.30 99.42 1.07 1.09 1.07 1.07 120.0
5000.0 0.10 0.09 95.75 90.70 1.08 1.10 1.07 1.07 120.0'''

transferswitch_metadata_on = [[0], [5,1,4,9], [1,6,9,4], [4,9,6,2], [9,4,2,6]]

#load Transfer switch and interpolate to required length
[sparams_switch_on, _] = interpolate_smatrix_datasheet(ds=transferswitch_datasheet, meta=transferswitch_metadata_on, db_true=True, db_negate=True, req_length=1030, port=4, lim=[1e9,5e9])

transferswitch_metadata_off = [[0], [7,3,2,9], [3,8,9,4], [2,9,8,2], [9,2,3,8]]

#load Transfer switch and interpolate to required length
[sparams_switch_off, _] = interpolate_smatrix_datasheet(ds=transferswitch_datasheet, meta=transferswitch_metadata_off, db_true=True, db_negate=True, req_length=1030, port=4, lim=[1e9,5e9])


#load inputs of TA and convert to V_nu (VSD)
V_nu, apsera_freq = TA_to_V(file='residues.txt', R=50)
print('\nLoaded VSD from Antenna temperature file---------')

# Load amplifier s matrix and interpolate it to apsera freq
freq_amp, sparams_amp = read_s2p('PHA-83W+_5.00V_Plus25DegC_TB-PHA-83WE+.s2p')
amp = interpolate_s_matrix_general(sparams_amp, freq_amp, apsera_freq)
print('\nLoaded Amplifier S matrix and interpolated---------')


#T_A and noise 50 ohms
#trim rrc, switch and amp matrices for use with the V_nu
rrc = interpolate_s_matrix_general(sparams_rrc, freq_rrc, apsera_freq)
switch_on = interpolate_s_matrix_general(sparams_switch_on, freq_rrc, apsera_freq)

#get noise at 50 ohms
freq_res = ((max(apsera_freq) - min(apsera_freq))/len(apsera_freq))
noise_input = noise_50(300,freq_res,len(apsera_freq))


# two inputs ---> switch + rrc(splits) + amplifier ---> two separate output
fig_switch_rrc, b2_rrc, b3_rrc = chain4ports(
    title='switch+rrc', 
    devices_sparam_list=[switch_on, rrc], 
    input1=V_nu, 
    input2=noise_input, 
    cross_input=[0,0], 
    freq_=apsera_freq     )

fig_amptop, b2_top = chain2ports(
    title='amp top', 
    devices_sparam_list=[amp], 
    input1=b2_rrc, 
    freq_=apsera_freq    )

fig_ampbottom, b2_bottom = chain2ports(
    title='amp top', 
    devices_sparam_list=[amp], 
    input1=b3_rrc, 
    freq_=apsera_freq    )


#correlate the output
fig_corr, corr_out = correlator(input1=b2_top, input2=b2_bottom, x=apsera_freq)



### IDEAL CASE
switch_ideal = ideal_switch_gen(apsera_freq)
rrc_ideal = ideal_rrc_gen(apsera_freq)
amp_ideal = ideal_amp_gen(apsera_freq)

# two inputs ---> switch + rrc(splits) + amplifier ---> two separate output
_, b2_rrc_ideal, b3_rrc_ideal = chain4ports(
    title='ideal switch+rrc', 
    devices_sparam_list=[switch_ideal, rrc_ideal], 
    input1=V_nu, input2=noise_input, 
    cross_input=[0,0], 
    freq_=apsera_freq     )

_, b2_top_ideal = chain2ports(
    title='ideal amp top', 
    devices_sparam_list=[amp_ideal], 
    input1=b2_rrc_ideal, 
    freq_=apsera_freq    )

_, b2_bottom_ideal = chain2ports(
    title='ideal amp top', 
    devices_sparam_list=[amp_ideal], 
    input1=b3_rrc_ideal, 
    freq_=apsera_freq    )


#correlate the output
fig_corr_ideal, corr_out = correlator(input1=b2_top_ideal, input2=b2_bottom_ideal, x=apsera_freq)




#T_A and noise 50 ohms
#trim rrc, switch and amp matrices for use with the V_nu
rrc = interpolate_s_matrix_general(sparams_rrc, freq_rrc, apsera_freq)
switch_off = interpolate_s_matrix_general(sparams_switch_off, freq_rrc, apsera_freq)

#get noise at 50 ohms
freq_res = ((max(apsera_freq) - min(apsera_freq))/len(apsera_freq))
noise_input = noise_50(300,freq_res,len(apsera_freq))


# two inputs ---> switch + rrc(splits) + amplifier ---> two separate output
fig_switch_rrc_off, b2_rrc_off, b3_rrc_off = chain4ports(
    title='switch+rrc', 
    devices_sparam_list=[switch_off, rrc], 
    input1=V_nu, 
    input2=noise_input, 
    cross_input=[0,0], 
    freq_=apsera_freq     )

fig_amptop_off, b2_top_off = chain2ports(
    title='amp top', 
    devices_sparam_list=[amp], 
    input1=b2_rrc_off, 
    freq_=apsera_freq    )

fig_ampbottom_off, b2_bottom_off = chain2ports(
    title='amp top', 
    devices_sparam_list=[amp], 
    input1=b3_rrc_off, 
    freq_=apsera_freq    )


#correlate the output
fig_corr, corr_out_off = correlator(input1=b2_top_off, input2=b2_bottom_off, x=apsera_freq)


plt.show()






# ### IDEAL CASE
# switch_ideal = ideal_switch_gen(apsera_freq)
# rrc_ideal = ideal_rrc_gen(apsera_freq)
# amp_ideal = ideal_amp_gen(apsera_freq)
# #send input get outputs for switch
# fig_switch_feed_ideal, b2_switch_ideal, b3_switch_ideal = feeder4port('Ideal switch', switch_ideal, V_nu, noise_input, apsera_freq)
# #send input get outputs for rrc
# fig_rrc_feed_ideal, b2_rrc_ideal, b3_rrc_ideal = feeder4port('Ideal rrc', rrc_ideal, b2_switch, b3_switch, apsera_freq)
# #send input get outputs for amp top
# fig_amptop_feed_ideal, b2_amp_top_ideal = feeder2port('Ideal amplifier top', amp_ideal, b2_rrc, apsera_freq)
# #send input get outputs for amp bottom
# fig_ampbottom_feed_ideal, b2_amp_bottom_ideal = feeder2port('Ideal amplifier bottom', amp_ideal, b3_rrc, apsera_freq)
# #correlate the ideal output
# fig_corr_ideal, corr_out_ideal = correlator(b2_amp_top_ideal, b2_amp_bottom_ideal, apsera_freq)