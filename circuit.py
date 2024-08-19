import numpy as np
from typing import List, Optional

class Component():
    def __init__(self, nodes: List[int], label: Optional[str] = None):
        self.nodes = nodes
        self.label = label

        return
    
    def get_label(self):
        return self.label

class Resistor(Component):
    def __init__(self, R: float, nodes: List[int], label: Optional[str] = None):
        super().__init__(nodes, label)
        self.R = R

        return

    def stamp(self, circuit): # circuit -> Circuit class
        G = 1/self.R
        circuit.stamp_conductance(self.nodes[0], self.nodes[1], G)

        return

    def set_value(self, val: float):
        self.R = val
        return

class Potentiometer(Component):
    def __init__(self, R: float, nodes: List[int], knob_pos: float = 5.0, label: Optional[str] = None):
        super().__init__(nodes, label)
        self.R = R
        self.knob_pos = knob_pos
        self.set_l_r()

        return

    def set_l_r(self):
        self.r_R = self.R*self.knob_pos/10.0

        if self.r_R < 1:
            self.r_R = 1
        elif self.r_R > self.R - 1:
            self.r_R = self.R - 1

        self.l_R = self.R - self.r_R

        return

    def stamp(self, circuit): # circuit -> Circuit class
        if self.nodes[0] != self.nodes[1]:
            l_G = 1/self.l_R
            circuit.stamp_conductance(self.nodes[0], self.nodes[1], l_G)

        if self.nodes[1] != self.nodes[2]:
            r_G = 1/self.r_R
            circuit.stamp_conductance(self.nodes[1], self.nodes[2], r_G)

        return

    def set_value(self, knob_pos: float):
        self.knob_pos = knob_pos
        self.set_l_r()

        return

class Inductor(Component):
    def __init__(self, L: float, nodes: List[int]):
        super().__init__(nodes)
        self.L = L

        return

    def stamp(self, circuit): # circuit -> Circuit class
        cur_freq = circuit.get_current_freq()
        G = complex(0, 1/(-2*np.pi*cur_freq*self.L))
        circuit.stamp_conductance(self.nodes[0], self.nodes[1], G)

        return

class Capacitor(Component):
    def __init__(self, C: float, nodes: List[int]):
        super().__init__(nodes)
        self.C = C

        return

    def stamp(self, circuit): # circuit -> Circuit class
        cur_freq = circuit.get_current_freq()
        G = complex(0, 2*np.pi*cur_freq*self.C)
        circuit.stamp_conductance(self.nodes[0], self.nodes[1], G)

        return

class VoltageSource(Component):
    def __init__(self, V: Optional[float], nodes: List[int]):
        super().__init__(nodes)
        self.vsn = None
        self.V = V

        return

    def stamp(self, circuit): # circuit -> Circuit class
        circuit.stamp_voltage_source(self.nodes[0], self.nodes[1], self.vsn, self.V)
        return

    def set_vs_num(self, vsn: int):
        self.vsn = vsn
        return

    def get_vs_num(self):
        return self.vsn

class OpAmp(VoltageSource):
    def __init__(self, nodes: List[int]):
        super().__init__(None, nodes)
        return

    def stamp(self, circuit): # circuit -> Circuit class
        circuit.stamp_op_amp(self.nodes[0], self.nodes[1], self.nodes[2], self.vsn)
        return

class Circuit():
    def __init__(self, components: List[Component], output_node: int, name: str):
        # .ac dec 10 1 20K
        self.start_freq = 10
        self.end_freq = 2e4
        self.mulStep = np.power(10, 0.1)

        self.components = components
        self.output_node = output_node
        self.name = name

        self.ckt_matrix = None
        self.ckt_rhs = None

        self.component_label_dict = dict() # dict for finding component index according to component label
        node_count = 0
        vs_count = 0 # voltage source count
        for i, comp in enumerate(self.components):
            node_count = max(node_count, max(comp.nodes))
            if isinstance(comp, VoltageSource):
                comp.set_vs_num(vs_count)
                vs_count += 1

            comp_label = comp.get_label()
            if comp_label is not None:
                self.component_label_dict[comp_label] = i

        matrix_size = node_count + vs_count 
        self.ckt_matrix = np.zeros((matrix_size, matrix_size), dtype=complex)
        self.ckt_rhs = np.zeros(matrix_size, dtype=complex)
        self.node_count = node_count

        return

    def set_component_value(self, label: str, val):
        if label not in self.component_label_dict:
            raise Exception("label '{}' not found in circuit".format(label))

        component_index = self.component_label_dict[label]
        self.components[component_index].set_value(val)

        return

    def get_name(self):
        return self.name
    
    def get_current_freq(self):
        return self.cur_freq

    def ac_analysis(self):
        freq_list = []
        response_list = []

        self.cur_freq = self.start_freq
        while self.cur_freq < self.end_freq:
            self.ckt_matrix[:][:] = complex(0, 0)
            self.ckt_rhs[:] = complex(0, 0)

            for comp in self.components:
                comp.stamp(self)

            solution = np.linalg.solve(self.ckt_matrix, self.ckt_rhs)

            freq_list.append(self.cur_freq)
            response_list.append(solution[self.output_node-1])

            self.cur_freq *= self.mulStep

        return freq_list, response_list

    #---Followings are stamp things, based on MNA(Modified Nodal Analysis)---
    def stamp_matrix(self, n1, n2, val):
        if n1 <= 0 or n2 <= 0:
            return
    
        n1 -= 1
        n2 -= 1
        self.ckt_matrix[n1][n2] += val
    
        return

    def stamp_rhs(self, n, val):
        if n <= 0:
            return

        n -= 1
        self.ckt_rhs[n] += val 

        return

    def stamp_conductance(self, n1, n2, G):
        self.stamp_matrix(n1, n1, G)
        self.stamp_matrix(n2, n2, G)
        self.stamp_matrix(n1, n2, -G)
        self.stamp_matrix(n2, n1, -G)
    
        return

    def stamp_voltage_source(self, n1, n2, vsn, voltage):
        vn = self.node_count + vsn + 1
    
        self.stamp_matrix(n1, vn, 1)
        self.stamp_matrix(n2, vn, -1)
        self.stamp_matrix(vn, n1, -1)
        self.stamp_matrix(vn, n2, 1)
    
        self.stamp_rhs(vn, voltage)

        return

    # n1 - inverting input, n2 - non-inverting input, n3 - output 
    def stamp_op_amp(self, n1, n2, n3, vsn):
        GAIN = 1e5;
    
        vn = self.node_count + vsn + 1
    
        self.stamp_matrix(n3, vn, 1)
        self.stamp_matrix(vn, n1, GAIN)
        self.stamp_matrix(vn, n2, -GAIN)
        self.stamp_matrix(vn, n3, 1)
    
        return
