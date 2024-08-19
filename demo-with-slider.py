import numpy as np

from _plot import slider_draw_by_plotly, SliderInfo
from circuit import Circuit, VoltageSource, Potentiometer, Capacitor

rc_ckt = Circuit(
            components = [ 
                VoltageSource(V=1, nodes=[0, 1]),
                Potentiometer(R=500e3, nodes=[1, 2, 2], label='Tone Knob'),
                Capacitor(C=1e-9, nodes=[2, 0])
            ],
            output_node = 2,
            name = "RC Ckt")

slider_draw_by_plotly(
    rc_ckt,
    SliderInfo(
        val_list=np.linspace(5.0, 10.0, 6),
        component_label='Tone Knob'
    )
)
