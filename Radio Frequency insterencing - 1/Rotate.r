try:
rfi_data = np.array(current_dataset)

heatmap_trace = go.Heatmap(z=rfi_data,
                           colorscale='Inferno',
                           zmin=-90,
                           zmax=-60,
                           x=np.linspace(0.5, 4.0, rfi_data.shape[1]),  # Adjust x-values here
                           y=[i * 1  for i in range(rfi_data.shape[0])],
                           )

heatmap_layout = go.Layout(
                           
                           xaxis=dict(title='Frequency [GHz]'),
                           yaxis=dict(title='Time [seconds]'),
                           width=680,
                           height=600
                           )

heatmap_fig = go.Figure(data=[heatmap_trace], layout=heatmap_layout)

heatmap_graphJSON = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

data_median = np.median(rfi_data[:, 2:], axis=0)

median_trace = go.Scatter(y=data_median, x=np.linspace(0.5, 4.0, len(data_median)), mode='lines', hoverinfo='x+y')

median_layout = go.Layout(
                          
                          xaxis_title='Frequency[GHz]',
                          yaxis_title='Median Intensity [dBm]',
                          xaxis=dict(autorange="reversed", type="linear"),
                          yaxis=dict(autorange="reversed", type="linear"),
                          hovermode='closest',
                          margin=dict(t=2),
                          width=720,
                          height=600
                          )

median_fig = go.Figure(data=[median_trace], layout=median_layout)

median_graphJSON = json.dumps(median_fig, cls=plotly.utils.PlotlyJSONEncoder)

time_index = np.arange(np.shape(rfi_data)[0])
time_median = np.median(rfi_data[:,:], axis=1)

time_median_trace = go.Scatter(x=time_median, y=time_index, mode='lines', name='Median Line')

time_median_layout = go.Layout(
    
    xaxis_title='Intensity [dBm]',
    yaxis_title='Time [s]',
    hovermode='closest',
    showlegend=True,
    width=700,
    height=600
)

time_median_fig = go.Figure(data=[time_median_trace], layout=time_median_layout)
time_median_graphJSON = json.dumps(time_median_fig, cls=plotly.utils.PlotlyJSONEncoder)

return jsonify({'success': True, 'heatmap_graphJSON': heatmap_graphJSON, 'median_graphJSON': median_graphJSON, 'time_median_graphJSON': time_median_graphJSON, 'image_path': uploaded_image_path})

except Exception as e:
return jsonify({'error': str(e)})