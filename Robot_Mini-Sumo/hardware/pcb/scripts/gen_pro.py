"""Genera robot_sumo.kicad_pro: clases de red y reglas de diseño (JLCPCB 2 capas)."""
import json
import os

import design

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', design.PROJECT + '.kicad_pro')


def netclass(name, track, clearance=0.2, via_d=0.6, via_h=0.3, prio=0, color='rgba(0, 0, 0, 0.000)'):
    return {
        'name': name, 'priority': prio, 'clearance': clearance, 'track_width': track,
        'via_diameter': via_d, 'via_drill': via_h, 'microvia_diameter': 0.3, 'microvia_drill': 0.1,
        'diff_pair_width': 0.2, 'diff_pair_gap': 0.25, 'diff_pair_via_gap': 0.25,
        'wire_width': 6, 'bus_width': 12, 'line_style': 0,
        'pcb_color': color, 'schematic_color': color,
    }


pro = {
    'meta': {'filename': os.path.basename(OUT), 'version': 3},
    'board': {
        'design_settings': {
            'rules': {
                'min_clearance': 0.15, 'min_track_width': 0.15, 'min_via_diameter': 0.5,
                'min_through_hole_diameter': 0.3, 'min_via_annular_width': 0.1,
                'min_hole_to_hole': 0.5, 'min_copper_edge_clearance': 0.3,
                'min_silk_clearance': 0.0, 'min_text_height': 0.8, 'min_text_thickness': 0.15,
                'min_hole_clearance': 0.25,
            },
            'track_widths': [0.0, 0.25, 0.4, 0.6, 1.0, 1.5],
            'via_dimensions': [{'diameter': 0.0, 'drill': 0.0}, {'diameter': 0.6, 'drill': 0.3},
                               {'diameter': 0.8, 'drill': 0.4}],
        },
    },
    'net_settings': {
        'meta': {'version': 4},
        'classes': [
            netclass('Default', 0.25),
            # VBAT, salidas de motor y GND de potencia: hasta ~2,5 A por motor (10 A en total por VBAT)
            netclass('Potencia', 1.0, clearance=0.25, via_d=0.8, via_h=0.4, prio=1,
                     color='rgba(194, 0, 0, 1.000)'),
            netclass('Alimentacion', 0.5, prio=2, color='rgba(194, 118, 0, 1.000)'),
            netclass('USB', 0.3, prio=3),
        ],
        'netclass_patterns': [
            {'netclass': 'Potencia', 'pattern': p} for p in
            ['VBAT', 'VBAT_RAW', 'VBAT_REV', 'M*_OUTA', 'M*_OUTB']
        ] + [
            {'netclass': 'Alimentacion', 'pattern': p} for p in
            ['+5V', '+3V3', 'V5_BUCK', 'VUSB', 'BUCK_SW']
        ] + [
            {'netclass': 'USB', 'pattern': p} for p in ['USB_DP', 'USB_DN']
        ],
    },
    'libraries': {'pinned_footprint_libs': [], 'pinned_symbol_libs': []},
    'sheets': [],
    'text_variables': {'EQUIPO': design.COMPANY, 'REV': design.REV},
}

with open(OUT, 'w') as f:
    json.dump(pro, f, indent=2)
print('escrito', os.path.relpath(OUT))
