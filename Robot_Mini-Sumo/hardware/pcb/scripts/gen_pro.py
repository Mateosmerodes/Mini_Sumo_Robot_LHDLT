"""Genera robot_sumo.kicad_pro: clases de red y reglas de diseño (2 capas, reglas holgadas: pistas ≥ 0,4 mm y holguras ≥ 0,3 mm)."""
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
                'min_clearance': 0.2, 'min_track_width': 0.25, 'min_via_diameter': 0.6,
                'min_through_hole_diameter': 0.3, 'min_via_annular_width': 0.1,
                'min_hole_to_hole': 0.5, 'min_copper_edge_clearance': 0.3,
                'min_silk_clearance': 0.0, 'min_text_height': 0.8, 'min_text_thickness': 0.15,
                'min_hole_clearance': 0.25,
            },
            'track_widths': [0.0, 0.4, 0.8, 1.5, 2.0],
            'via_dimensions': [{'diameter': 0.0, 'drill': 0.0}, {'diameter': 0.9, 'drill': 0.45},
                               {'diameter': 1.2, 'drill': 0.6}],
        },
    },
    'net_settings': {
        'meta': {'version': 4},
        'classes': [
            netclass('Default', 0.4, clearance=0.3, via_d=0.9, via_h=0.45),
            # Batería y motores: hasta ~2,3 A por motor y ~5 A en total por VBAT/GND
            netclass('Potencia', 1.5, clearance=0.4, via_d=1.2, via_h=0.6, prio=1,
                     color='rgba(194, 0, 0, 1.000)'),
            netclass('Alimentacion', 0.8, clearance=0.3, via_d=1.0, via_h=0.5, prio=2,
                     color='rgba(194, 118, 0, 1.000)'),
        ],
        'netclass_patterns': [
            {'netclass': 'Potencia', 'pattern': p} for p in ['VBAT', 'VBAT_RAW', 'MI_A', 'MI_B', 'MD_A', 'MD_B']
        ] + [
            {'netclass': 'Alimentacion', 'pattern': p} for p in ['+5V', 'V5_ESP']
        ],
    },
    'libraries': {'pinned_footprint_libs': [], 'pinned_symbol_libs': []},
    'sheets': [],
    'text_variables': {'EQUIPO': design.COMPANY, 'REV': design.REV},
}

with open(OUT, 'w') as f:
    json.dump(pro, f, indent=2)
print('escrito', os.path.relpath(OUT))
