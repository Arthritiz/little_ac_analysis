from _plot import draw_by_plotly
from circuit import Circuit, VoltageSource, Resistor, Capacitor

rc_ckt = Circuit(
            components = [ 
                VoltageSource(V=1, nodes=[0, 1]),
                Resistor(R=500e3, nodes=[1, 2]),
                Capacitor(C=1e-9, nodes=[2, 0])
            ],
            output_node = 2,
            name = "RC Ckt")

draw_by_plotly(rc_ckt)

