# Plotting waterfall plot
        f_start = Start_frequency
        f_stop = Stop_frequency
        f_sweep=Sweep_points
        f_sweep_time = Sweep_time


        rfi_data = np.array(current_dataset)

        heatmap_trace = go.Heatmap(z=rfi_data,
                                   colorscale='Inferno',
                                   zmin=-90,
                                   zmax=-60,
                                   x=np.linspace(f_start,f_stop, rfi_data.shape[1]),  # Adjust x-values here
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