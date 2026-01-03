import math
import sqlite3
import sys
import webbrowser
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Tuple, Optional

from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QDialog
)

from db import init_db, insert_registry, list_registry, get_registry, update_registry
from export_utils import export_rows_to_csv
from update_check import check_update_and_download
from version import __version__

YES_NO_NS = ["-", "Sì", "No", "Non so"]
YES_NO = ["-", 'Sì', 'No']
VILLAGGI = ["-", "Befandefa", "Andavadoaka"]
SESSI = ["-", "Maschio", "Femmina"]

REPO_URL = "https://github.com/lcarotenuto/questionario-ampasilava"

lms_f_0_2 = {
    45.0:   [-0.3833,  2.4607, 0.09029],
    45.5:   [-0.3833,  2.5457, 0.09033],
    46.0:   [-0.3833,  2.6306, 0.09037],
    46.5:   [-0.3833,  2.7155, 0.09040],
    47.0:   [-0.3833,  2.8007, 0.09044],
    47.5:   [-0.3833,  2.8867, 0.09048],
    48.0:   [-0.3833,  2.9741, 0.09052],
    48.5:   [-0.3833,  3.0636, 0.09056],
    49.0:   [-0.3833,  3.1560, 0.09060],
    49.5:   [-0.3833,  3.2520, 0.09064],
    50.0:   [-0.3833,  3.3518, 0.09068],
    50.5:   [-0.3833,  3.4557, 0.09072],
    51.0:   [-0.3833,  3.5636, 0.09076],
    51.5:   [-0.3833,  3.6754, 0.09080],
    52.0:   [-0.3833,  3.7911, 0.09085],
    52.5:   [-0.3833,  3.9105, 0.09089],
    53.0:   [-0.3833,  4.0332, 0.09093],
    53.5:   [-0.3833,  4.1591, 0.09098],
    54.0:   [-0.3833,  4.2875, 0.09102],
    54.5:   [-0.3833,  4.4179, 0.09106],
    55.0:   [-0.3833,  4.5498, 0.09110],
    55.5:   [-0.3833,  4.6827, 0.09114],
    56.0:   [-0.3833,  4.8162, 0.09118],
    56.5:   [-0.3833,  4.9500, 0.09121],
    57.0:   [-0.3833,  5.0837, 0.09125],
    57.5:   [-0.3833,  5.2173, 0.09128],
    58.0:   [-0.3833,  5.3507, 0.09130],
    58.5:   [-0.3833,  5.4834, 0.09132],
    59.0:   [-0.3833,  5.6151, 0.09134],
    59.5:   [-0.3833,  5.7454, 0.09135],
    60.0:   [-0.3833,  5.8742, 0.09136],
    60.5:   [-0.3833,  6.0014, 0.09137],
    61.0:   [-0.3833,  6.1270, 0.09137],
    61.5:   [-0.3833,  6.2511, 0.09136],
    62.0:   [-0.3833,  6.3738, 0.09135],
    62.5:   [-0.3833,  6.4948, 0.09133],
    63.0:   [-0.3833,  6.6144, 0.09131],
    63.5:   [-0.3833,  6.7328, 0.09129],
    64.0:   [-0.3833,  6.8501, 0.09126],
    64.5:   [-0.3833,  6.9662, 0.09123],
    65.0:   [-0.3833,  7.0812, 0.09119],
    65.5:   [-0.3833,  7.1950, 0.09115],
    66.0:   [-0.3833,  7.3076, 0.09110],
    66.5:   [-0.3833,  7.4189, 0.09106],
    67.0:   [-0.3833,  7.5288, 0.09101],
    67.5:   [-0.3833,  7.6375, 0.09096],
    68.0:   [-0.3833,  7.7448, 0.09090],
    68.5:   [-0.3833,  7.8509, 0.09085],
    69.0:   [-0.3833,  7.9559, 0.09079],
    69.5:   [-0.3833,  8.0599, 0.09074],
    70.0:   [-0.3833,  8.1630, 0.09068],
    70.5:   [-0.3833,  8.2651, 0.09062],
    71.0:   [-0.3833,  8.3666, 0.09056],
    71.5:   [-0.3833,  8.4676, 0.09050],
    72.0:   [-0.3833,  8.5679, 0.09043],
    72.5:   [-0.3833,  8.6674, 0.09037],
    73.0:   [-0.3833,  8.7661, 0.09031],
    73.5:   [-0.3833,  8.8638, 0.09025],
    74.0:   [-0.3833,  8.9601, 0.09018],
    74.5:   [-0.3833,  9.0552, 0.09012],
    75.0:   [-0.3833,  9.1490, 0.09005],
    75.5:   [-0.3833,  9.2418, 0.08999],
    76.0:   [-0.3833,  9.3337, 0.08992],
    76.5:   [-0.3833,  9.4252, 0.08985],
    77.0:   [-0.3833,  9.5166, 0.08979],
    77.5:   [-0.3833,  9.6086, 0.08972],
    78.0:   [-0.3833,  9.7015, 0.08965],
    78.5:   [-0.3833,  9.7957, 0.08959],
    79.0:   [-0.3833,  9.8915, 0.08952],
    79.5:   [-0.3833,  9.9892, 0.08946],
    80.0:   [-0.3833, 10.0891, 0.08940],
    80.5:   [-0.3833, 10.1916, 0.08934],
    81.0:   [-0.3833, 10.2965, 0.08928],
    81.5:   [-0.3833, 10.4041, 0.08923],
    82.0:   [-0.3833, 10.5140, 0.08918],
    82.5:   [-0.3833, 10.6263, 0.08914],
    83.0:   [-0.3833, 10.7410, 0.08910],
    83.5:   [-0.3833, 10.8578, 0.08906],
    84.0:   [-0.3833, 10.9767, 0.08903],
    84.5:   [-0.3833, 11.0974, 0.08900],
    85.0:   [-0.3833, 11.2198, 0.08898],
    85.5:   [-0.3833, 11.3435, 0.08897],
    86.0:   [-0.3833, 11.4684, 0.08895],
    86.5:   [-0.3833, 11.5940, 0.08895],
    87.0:   [-0.3833, 11.7201, 0.08895],
    87.5:   [-0.3833, 11.8461, 0.08895],
    88.0:   [-0.3833, 11.9720, 0.08896],
    88.5:   [-0.3833, 12.0976, 0.08898],
    89.0:   [-0.3833, 12.2229, 0.08900],
    89.5:   [-0.3833, 12.3477, 0.08903],
    90.0:   [-0.3833, 12.4723, 0.08906],
    90.5:   [-0.3833, 12.5965, 0.08909],
    91.0:   [-0.3833, 12.7205, 0.08913],
    91.5:   [-0.3833, 12.8443, 0.08918],
    92.0:   [-0.3833, 12.9681, 0.08923],
    92.5:   [-0.3833, 13.0920, 0.08928],
    93.0:   [-0.3833, 13.2158, 0.08934],
    93.5:   [-0.3833, 13.3399, 0.08941],
    94.0:   [-0.3833, 13.4643, 0.08948],
    94.5:   [-0.3833, 13.5892, 0.08955],
    95.0:   [-0.3833, 13.7146, 0.08963],
    95.5:   [-0.3833, 13.8408, 0.08972],
    96.0:   [-0.3833, 13.9676, 0.08981],
    96.5:   [-0.3833, 14.0953, 0.08990],
    97.0:   [-0.3833, 14.2239, 0.09000],
    97.5:   [-0.3833, 14.3537, 0.09010],
    98.0:   [-0.3833, 14.4848, 0.09021],
    98.5:   [-0.3833, 14.6174, 0.09033],
    99.0:   [-0.3833, 14.7519, 0.09044],
    99.5:   [-0.3833, 14.8882, 0.09057],
    100.0:  [-0.3833, 15.0267, 0.09069],
    100.5:  [-0.3833, 15.1676, 0.09083],
    101.0:  [-0.3833, 15.3108, 0.09096],
    101.5:  [-0.3833, 15.4564, 0.09110],
    102.0:  [-0.3833, 15.6046, 0.09125],
    102.5:  [-0.3833, 15.7553, 0.09139],
    103.0:  [-0.3833, 15.9087, 0.09155],
    103.5:  [-0.3833, 16.0645, 0.09170],
    104.0:  [-0.3833, 16.2229, 0.09186],
    104.5:  [-0.3833, 16.3837, 0.09203],
    105.0:  [-0.3833, 16.5470, 0.09219],
    105.5:  [-0.3833, 16.7129, 0.09236],
    106.0:  [-0.3833, 16.8814, 0.09254],
    106.5:  [-0.3833, 17.0527, 0.09271],
    107.0:  [-0.3833, 17.2269, 0.09289],
    107.5:  [-0.3833, 17.4039, 0.09307],
    108.0:  [-0.3833, 17.5839, 0.09326],
    108.5:  [-0.3833, 17.7668, 0.09344],
    109.0:  [-0.3833, 17.9526, 0.09363],
    109.5:  [-0.3833, 18.1412, 0.09382],
    110.0:  [-0.3833, 18.3324, 0.09401],
}

lms_f_2_5 = {
    65.0:   [-0.3833,  7.2402, 0.09113],
    65.5:   [-0.3833,  7.3523, 0.09109],
    66.0:   [-0.3833,  7.4630, 0.09104],
    66.5:   [-0.3833,  7.5724, 0.09099],
    67.0:   [-0.3833,  7.6806, 0.09094],
    67.5:   [-0.3833,  7.7874, 0.09088],
    68.0:   [-0.3833,  7.8930, 0.09083],
    68.5:   [-0.3833,  7.9976, 0.09077],
    69.0:   [-0.3833,  8.1012, 0.09071],
    69.5:   [-0.3833,  8.2039, 0.09065],
    70.0:   [-0.3833,  8.3058, 0.09059],
    70.5:   [-0.3833,  8.4071, 0.09053],
    71.0:   [-0.3833,  8.5078, 0.09047],
    71.5:   [-0.3833,  8.6078, 0.09041],
    72.0:   [-0.3833,  8.7070, 0.09035],
    72.5:   [-0.3833,  8.8053, 0.09028],
    73.0:   [-0.3833,  8.9025, 0.09022],
    73.5:   [-0.3833,  8.9983, 0.09016],
    74.0:   [-0.3833,  9.0928, 0.09009],
    74.5:   [-0.3833,  9.1862, 0.09003],
    75.0:   [-0.3833,  9.2786, 0.08996],
    75.5:   [-0.3833,  9.3703, 0.08989],
    76.0:   [-0.3833,  9.4617, 0.08983],
    76.5:   [-0.3833,  9.5533, 0.08976],
    77.0:   [-0.3833,  9.6456, 0.08969],
    77.5:   [-0.3833,  9.7390, 0.08963],
    78.0:   [-0.3833,  9.8338, 0.08956],
    78.5:   [-0.3833,  9.9303, 0.08950],
    79.0:   [-0.3833, 10.0289, 0.08943],
    79.5:   [-0.3833, 10.1298, 0.08937],
    80.0:   [-0.3833, 10.2332, 0.08932],
    80.5:   [-0.3833, 10.3393, 0.08926],
    81.0:   [-0.3833, 10.4477, 0.08921],
    81.5:   [-0.3833, 10.5586, 0.08916],
    82.0:   [-0.3833, 10.6719, 0.08912],
    82.5:   [-0.3833, 10.7874, 0.08908],
    83.0:   [-0.3833, 10.9051, 0.08905],
    83.5:   [-0.3833, 11.0248, 0.08902],
    84.0:   [-0.3833, 11.1462, 0.08899],
    84.5:   [-0.3833, 11.2691, 0.08897],
    85.0:   [-0.3833, 11.3934, 0.08896],
    85.5:   [-0.3833, 11.5186, 0.08895],
    86.0:   [-0.3833, 11.6444, 0.08895],
    86.5:   [-0.3833, 11.7705, 0.08895],
    87.0:   [-0.3833, 11.8965, 0.08896],
    87.5:   [-0.3833, 12.0223, 0.08897],
    88.0:   [-0.3833, 12.1478, 0.08899],
    88.5:   [-0.3833, 12.2729, 0.08901],
    89.0:   [-0.3833, 12.3976, 0.08904],
    89.5:   [-0.3833, 12.5220, 0.08907],
    90.0:   [-0.3833, 12.6461, 0.08911],
    90.5:   [-0.3833, 12.7700, 0.08915],
    91.0:   [-0.3833, 12.8939, 0.08920],
    91.5:   [-0.3833, 13.0177, 0.08925],
    92.0:   [-0.3833, 13.1415, 0.08931],
    92.5:   [-0.3833, 13.2654, 0.08937],
    93.0:   [-0.3833, 13.3896, 0.08944],
    93.5:   [-0.3833, 13.5142, 0.08951],
    94.0:   [-0.3833, 13.6393, 0.08959],
    94.5:   [-0.3833, 13.7650, 0.08967],
    95.0:   [-0.3833, 13.8914, 0.08975],
    95.5:   [-0.3833, 14.0186, 0.08984],
    96.0:   [-0.3833, 14.1466, 0.08994],
    96.5:   [-0.3833, 14.2757, 0.09004],
    97.0:   [-0.3833, 14.4059, 0.09015],
    97.5:   [-0.3833, 14.5376, 0.09026],
    98.0:   [-0.3833, 14.6710, 0.09037],
    98.5:   [-0.3833, 14.8062, 0.09049],
    99.0:   [-0.3833, 14.9434, 0.09062],
    99.5:   [-0.3833, 15.0828, 0.09075],
    100.0:  [-0.3833, 15.2246, 0.09088],
    100.5:  [-0.3833, 15.3687, 0.09102],
    101.0:  [-0.3833, 15.5154, 0.09116],
    101.5:  [-0.3833, 15.6646, 0.09131],
    102.0:  [-0.3833, 15.8164, 0.09146],
    102.5:  [-0.3833, 15.9707, 0.09161],
    103.0:  [-0.3833, 16.1276, 0.09177],
    103.5:  [-0.3833, 16.2870, 0.09193],
    104.0:  [-0.3833, 16.4488, 0.09209],
    104.5:  [-0.3833, 16.6131, 0.09226],
    105.0:  [-0.3833, 16.7800, 0.09243],
    105.5:  [-0.3833, 16.9496, 0.09261],
    106.0:  [-0.3833, 17.1220, 0.09278],
    106.5:  [-0.3833, 17.2973, 0.09296],
    107.0:  [-0.3833, 17.4755, 0.09315],
    107.5:  [-0.3833, 17.6567, 0.09333],
    108.0:  [-0.3833, 17.8407, 0.09352],
    108.5:  [-0.3833, 18.0277, 0.09371],
    109.0:  [-0.3833, 18.2174, 0.09390],
    109.5:  [-0.3833, 18.4096, 0.09409],
    110.0:  [-0.3833, 18.6043, 0.09428],
    110.5:  [-0.3833, 18.8015, 0.09448],
    111.0:  [-0.3833, 19.0009, 0.09467],
    111.5:  [-0.3833, 19.2024, 0.09487],
    112.0:  [-0.3833, 19.4060, 0.09507],
    112.5:  [-0.3833, 19.6116, 0.09527],
    113.0:  [-0.3833, 19.8190, 0.09546],
    113.5:  [-0.3833, 20.0280, 0.09566],
    114.0:  [-0.3833, 20.2385, 0.09586],
    114.5:  [-0.3833, 20.4502, 0.09606],
    115.0:  [-0.3833, 20.6629, 0.09626],
    115.5:  [-0.3833, 20.8766, 0.09646],
    116.0:  [-0.3833, 21.0909, 0.09666],
    116.5:  [-0.3833, 21.3059, 0.09686],
    117.0:  [-0.3833, 21.5213, 0.09707],
    117.5:  [-0.3833, 21.7370, 0.09727],
    118.0:  [-0.3833, 21.9529, 0.09747],
    118.5:  [-0.3833, 22.1690, 0.09767],
    119.0:  [-0.3833, 22.3851, 0.09788],
    119.5:  [-0.3833, 22.6012, 0.09808],
    120.0:  [-0.3833, 22.8173, 0.09828],
}

lms_m_0_2 = {
    45.0:   [-0.3521,  2.4410, 0.09182],
    45.5:   [-0.3521,  2.5244, 0.09153],
    46.0:   [-0.3521,  2.6077, 0.09124],
    46.5:   [-0.3521,  2.6913, 0.09094],
    47.0:   [-0.3521,  2.7755, 0.09065],
    47.5:   [-0.3521,  2.8609, 0.09036],
    48.0:   [-0.3521,  2.9480, 0.09007],
    48.5:   [-0.3521,  3.0377, 0.08977],
    49.0:   [-0.3521,  3.1308, 0.08948],
    49.5:   [-0.3521,  3.2276, 0.08919],
    50.0:   [-0.3521,  3.3278, 0.08890],
    50.5:   [-0.3521,  3.4311, 0.08861],
    51.0:   [-0.3521,  3.5376, 0.08831],
    51.5:   [-0.3521,  3.6477, 0.08801],
    52.0:   [-0.3521,  3.7620, 0.08771],
    52.5:   [-0.3521,  3.8814, 0.08741],
    53.0:   [-0.3521,  4.0060, 0.08711],
    53.5:   [-0.3521,  4.1354, 0.08681],
    54.0:   [-0.3521,  4.2693, 0.08651],
    54.5:   [-0.3521,  4.4066, 0.08621],
    55.0:   [-0.3521,  4.5467, 0.08592],
    55.5:   [-0.3521,  4.6892, 0.08563],
    56.0:   [-0.3521,  4.8338, 0.08535],
    56.5:   [-0.3521,  4.9796, 0.08507],
    57.0:   [-0.3521,  5.1259, 0.08481],
    57.5:   [-0.3521,  5.2721, 0.08455],
    58.0:   [-0.3521,  5.4180, 0.08430],
    58.5:   [-0.3521,  5.5632, 0.08406],
    59.0:   [-0.3521,  5.7074, 0.08383],
    59.5:   [-0.3521,  5.8501, 0.08362],
    60.0:   [-0.3521,  5.9907, 0.08342],
    60.5:   [-0.3521,  6.1284, 0.08324],
    61.0:   [-0.3521,  6.2632, 0.08308],
    61.5:   [-0.3521,  6.3954, 0.08292],
    62.0:   [-0.3521,  6.5251, 0.08279],
    62.5:   [-0.3521,  6.6527, 0.08266],
    63.0:   [-0.3521,  6.7786, 0.08255],
    63.5:   [-0.3521,  6.9028, 0.08245],
    64.0:   [-0.3521,  7.0255, 0.08236],
    64.5:   [-0.3521,  7.1467, 0.08229],
    65.0:   [-0.3521,  7.2666, 0.08223],
    65.5:   [-0.3521,  7.3854, 0.08218],
    66.0:   [-0.3521,  7.5034, 0.08215],
    66.5:   [-0.3521,  7.6206, 0.08213],
    67.0:   [-0.3521,  7.7370, 0.08212],
    67.5:   [-0.3521,  7.8526, 0.08212],
    68.0:   [-0.3521,  7.9674, 0.08214],
    68.5:   [-0.3521,  8.0816, 0.08216],
    69.0:   [-0.3521,  8.1955, 0.08219],
    69.5:   [-0.3521,  8.3092, 0.08224],
    70.0:   [-0.3521,  8.4227, 0.08229],
    70.5:   [-0.3521,  8.5358, 0.08235],
    71.0:   [-0.3521,  8.6480, 0.08241],
    71.5:   [-0.3521,  8.7594, 0.08248],
    72.0:   [-0.3521,  8.8697, 0.08254],
    72.5:   [-0.3521,  8.9788, 0.08262],
    73.0:   [-0.3521,  9.0865, 0.08269],
    73.5:   [-0.3521,  9.1927, 0.08276],
    74.0:   [-0.3521,  9.2974, 0.08283],
    74.5:   [-0.3521,  9.4010, 0.08289],
    75.0:   [-0.3521,  9.5032, 0.08295],
    75.5:   [-0.3521,  9.6041, 0.08301],
    76.0:   [-0.3521,  9.7033, 0.08307],
    76.5:   [-0.3521,  9.8007, 0.08311],
    77.0:   [-0.3521,  9.8963, 0.08314],
    77.5:   [-0.3521,  9.9902, 0.08317],
    78.0:   [-0.3521, 10.0827, 0.08318],
    78.5:   [-0.3521, 10.1741, 0.08318],
    79.0:   [-0.3521, 10.2649, 0.08316],
    79.5:   [-0.3521, 10.3558, 0.08313],
    80.0:   [-0.3521, 10.4475, 0.08308],
    80.5:   [-0.3521, 10.5405, 0.08301],
    81.0:   [-0.3521, 10.6352, 0.08293],
    81.5:   [-0.3521, 10.7322, 0.08284],
    82.0:   [-0.3521, 10.8321, 0.08273],
    82.5:   [-0.3521, 10.9350, 0.08260],
    83.0:   [-0.3521, 11.0415, 0.08246],
    83.5:   [-0.3521, 11.1516, 0.08231],
    84.0:   [-0.3521, 11.2651, 0.08215],
    84.5:   [-0.3521, 11.3817, 0.08198],
    85.0:   [-0.3521, 11.5007, 0.08181],
    85.5:   [-0.3521, 11.6218, 0.08163],
    86.0:   [-0.3521, 11.7444, 0.08145],
    86.5:   [-0.3521, 11.8678, 0.08128],
    87.0:   [-0.3521, 11.9916, 0.08111],
    87.5:   [-0.3521, 12.1152, 0.08096],
    88.0:   [-0.3521, 12.2382, 0.08082],
    88.5:   [-0.3521, 12.3603, 0.08069],
    89.0:   [-0.3521, 12.4815, 0.08058],
    89.5:   [-0.3521, 12.6017, 0.08048],
    90.0:   [-0.3521, 12.7209, 0.08041],
    90.5:   [-0.3521, 12.8392, 0.08034],
    91.0:   [-0.3521, 12.9569, 0.08030],
    91.5:   [-0.3521, 13.0742, 0.08026],
    92.0:   [-0.3521, 13.1910, 0.08025],
    92.5:   [-0.3521, 13.3075, 0.08025],
    93.0:   [-0.3521, 13.4239, 0.08026],
    93.5:   [-0.3521, 13.5404, 0.08029],
    94.0:   [-0.3521, 13.6572, 0.08034],
    94.5:   [-0.3521, 13.7746, 0.08040],
    95.0:   [-0.3521, 13.8928, 0.08047],
    95.5:   [-0.3521, 14.0120, 0.08056],
    96.0:   [-0.3521, 14.1325, 0.08067],
    96.5:   [-0.3521, 14.2544, 0.08078],
    97.0:   [-0.3521, 14.3782, 0.08092],
    97.5:   [-0.3521, 14.5038, 0.08106],
    98.0:   [-0.3521, 14.6316, 0.08122],
    98.5:   [-0.3521, 14.7614, 0.08139],
    99.0:   [-0.3521, 14.8934, 0.08157],
    99.5:   [-0.3521, 15.0275, 0.08177],
    100.0:  [-0.3521, 15.1637, 0.08198],
    100.5:  [-0.3521, 15.3018, 0.08220],
    101.0:  [-0.3521, 15.4419, 0.08243],
    101.5:  [-0.3521, 15.5838, 0.08267],
    102.0:  [-0.3521, 15.7276, 0.08292],
    102.5:  [-0.3521, 15.8732, 0.08317],
    103.0:  [-0.3521, 16.0206, 0.08343],
    103.5:  [-0.3521, 16.1697, 0.08370],
    104.0:  [-0.3521, 16.3204, 0.08397],
    104.5:  [-0.3521, 16.4728, 0.08425],
    105.0:  [-0.3521, 16.6268, 0.08453],
    105.5:  [-0.3521, 16.7826, 0.08481],
    106.0:  [-0.3521, 16.9401, 0.08510],
    106.5:  [-0.3521, 17.0995, 0.08539],
    107.0:  [-0.3521, 17.2607, 0.08568],
    107.5:  [-0.3521, 17.4237, 0.08599],
    108.0:  [-0.3521, 17.5885, 0.08629],
    108.5:  [-0.3521, 17.7553, 0.08660],
    109.0:  [-0.3521, 17.9242, 0.08691],
    109.5:  [-0.3521, 18.0954, 0.08723],
    110.0:  [-0.3521, 18.2689, 0.08755],
}

lms_m_2_5 = {
    65.0:   [-0.3521,  7.4327, 0.08217],
    65.5:   [-0.3521,  7.5504, 0.08214],
    66.0:   [-0.3521,  7.6673, 0.08212],
    66.5:   [-0.3521,  7.7834, 0.08212],
    67.0:   [-0.3521,  7.8986, 0.08213],
    67.5:   [-0.3521,  8.0132, 0.08214],
    68.0:   [-0.3521,  8.1272, 0.08217],
    68.5:   [-0.3521,  8.2410, 0.08221],
    69.0:   [-0.3521,  8.3547, 0.08226],
    69.5:   [-0.3521,  8.4680, 0.08231],
    70.0:   [-0.3521,  8.5808, 0.08237],
    70.5:   [-0.3521,  8.6927, 0.08243],
    71.0:   [-0.3521,  8.8036, 0.08250],
    71.5:   [-0.3521,  8.9135, 0.08257],
    72.0:   [-0.3521,  9.0221, 0.08264],
    72.5:   [-0.3521,  9.1292, 0.08272],
    73.0:   [-0.3521,  9.2347, 0.08278],
    73.5:   [-0.3521,  9.3390, 0.08285],
    74.0:   [-0.3521,  9.4420, 0.08292],
    74.5:   [-0.3521,  9.5438, 0.08298],
    75.0:   [-0.3521,  9.6440, 0.08303],
    75.5:   [-0.3521,  9.7425, 0.08308],
    76.0:   [-0.3521,  9.8392, 0.08312],
    76.5:   [-0.3521,  9.9341, 0.08315],
    77.0:   [-0.3521, 10.0274, 0.08317],
    77.5:   [-0.3521, 10.1194, 0.08318],
    78.0:   [-0.3521, 10.2105, 0.08317],
    78.5:   [-0.3521, 10.3012, 0.08315],
    79.0:   [-0.3521, 10.3923, 0.08311],
    79.5:   [-0.3521, 10.4845, 0.08305],
    80.0:   [-0.3521, 10.5781, 0.08298],
    80.5:   [-0.3521, 10.6737, 0.08290],
    81.0:   [-0.3521, 10.7718, 0.08279],
    81.5:   [-0.3521, 10.8728, 0.08268],
    82.0:   [-0.3521, 10.9772, 0.08255],
    82.5:   [-0.3521, 11.0851, 0.08241],
    83.0:   [-0.3521, 11.1966, 0.08225],
    83.5:   [-0.3521, 11.3114, 0.08209],
    84.0:   [-0.3521, 11.4290, 0.08191],
    84.5:   [-0.3521, 11.5490, 0.08174],
    85.0:   [-0.3521, 11.6707, 0.08156],
    85.5:   [-0.3521, 11.7937, 0.08138],
    86.0:   [-0.3521, 11.9173, 0.08121],
    86.5:   [-0.3521, 12.0411, 0.08105],
    87.0:   [-0.3521, 12.1645, 0.08090],
    87.5:   [-0.3521, 12.2871, 0.08076],
    88.0:   [-0.3521, 12.4089, 0.08064],
    88.5:   [-0.3521, 12.5298, 0.08054],
    89.0:   [-0.3521, 12.6495, 0.08045],
    89.5:   [-0.3521, 12.7683, 0.08038],
    90.0:   [-0.3521, 12.8864, 0.08032],
    90.5:   [-0.3521, 13.0038, 0.08028],
    91.0:   [-0.3521, 13.1209, 0.08025],
    91.5:   [-0.3521, 13.2376, 0.08024],
    92.0:   [-0.3521, 13.3541, 0.08025],
    92.5:   [-0.3521, 13.4705, 0.08027],
    93.0:   [-0.3521, 13.5870, 0.08031],
    93.5:   [-0.3521, 13.7041, 0.08036],
    94.0:   [-0.3521, 13.8217, 0.08043],
    94.5:   [-0.3521, 13.9403, 0.08051],
    95.0:   [-0.3521, 14.0600, 0.08060],
    95.5:   [-0.3521, 14.1811, 0.08071],
    96.0:   [-0.3521, 14.3037, 0.08083],
    96.5:   [-0.3521, 14.4282, 0.08097],
    97.0:   [-0.3521, 14.5547, 0.08112],
    97.5:   [-0.3521, 14.6832, 0.08129],
    98.0:   [-0.3521, 14.8140, 0.08146],
    98.5:   [-0.3521, 14.9468, 0.08165],
    99.0:   [-0.3521, 15.0818, 0.08185],
    99.5:   [-0.3521, 15.2187, 0.08206],
    100.0:  [-0.3521, 15.3576, 0.08229],
    100.5:  [-0.3521, 15.4985, 0.08252],
    101.0:  [-0.3521, 15.6412, 0.08277],
    101.5:  [-0.3521, 15.7857, 0.08302],
    102.0:  [-0.3521, 15.9320, 0.08328],
    102.5:  [-0.3521, 16.0801, 0.08354],
    103.0:  [-0.3521, 16.2298, 0.08381],
    103.5:  [-0.3521, 16.3812, 0.08408],
    104.0:  [-0.3521, 16.5342, 0.08436],
    104.5:  [-0.3521, 16.6889, 0.08464],
    105.0:  [-0.3521, 16.8454, 0.08493],
    105.5:  [-0.3521, 17.0036, 0.08521],
    106.0:  [-0.3521, 17.1637, 0.08551],
    106.5:  [-0.3521, 17.3256, 0.08580],
    107.0:  [-0.3521, 17.4894, 0.08611],
    107.5:  [-0.3521, 17.6550, 0.08641],
    108.0:  [-0.3521, 17.8226, 0.08673],
    108.5:  [-0.3521, 17.9924, 0.08704],
    109.0:  [-0.3521, 18.1645, 0.08736],
    109.5:  [-0.3521, 18.3390, 0.08768],
    110.0:  [-0.3521, 18.5158, 0.08800],
    110.5:  [-0.3521, 18.6948, 0.08832],
    111.0:  [-0.3521, 18.8759, 0.08864],
    111.5:  [-0.3521, 19.0590, 0.08896],
    112.0:  [-0.3521, 19.2439, 0.08928],
    112.5:  [-0.3521, 19.4304, 0.08960],
    113.0:  [-0.3521, 19.6185, 0.08991],
    113.5:  [-0.3521, 19.8081, 0.09022],
    114.0:  [-0.3521, 19.9990, 0.09054],
    114.5:  [-0.3521, 20.1912, 0.09085],
    115.0:  [-0.3521, 20.3846, 0.09116],
    115.5:  [-0.3521, 20.5789, 0.09147],
    116.0:  [-0.3521, 20.7741, 0.09177],
    116.5:  [-0.3521, 20.9700, 0.09208],
    117.0:  [-0.3521, 21.1666, 0.09239],
    117.5:  [-0.3521, 21.3636, 0.09270],
    118.0:  [-0.3521, 21.5611, 0.09300],
    118.5:  [-0.3521, 21.7588, 0.09331],
    119.0:  [-0.3521, 21.9568, 0.09362],
    119.5:  [-0.3521, 22.1549, 0.09393],
    120.0:  [-0.3521, 22.3530, 0.09424],
}

LMS = {
    "boys": {
        "0_2": lms_m_0_2,
        "2_5": lms_m_2_5
    },
    "girls": {
        "0_2": lms_f_0_2,
        "2_5": lms_f_2_5
    }
}

def compute_whz(y, L, M, S):
    if y <= 0 or M <= 0 or S <= 0:
        raise ValueError("weight (y), M e S devono essere > 0")
    if abs(L) < 1e-12:
        return math.log(y / M) / S
    return ((y / M) ** L - 1.0) / (L * S)


def bool_to_int(v: bool) -> int:
    return 1 if v else 0


class RegistryForm(QWidget):
    """
    Widget riusabile: stessa UI per creazione e modifica.
    Contiene:
      - costruzione UI
      - calcolo WHZ automatico
      - clear()
      - get_data()
      - set_data(row)
      - validate(data)
    """
    def __init__(self, *, taratassi_readonly: bool = False, parent=None):
        super().__init__(parent)
        self._build()
        self.set_taratassi_readonly(taratassi_readonly)

    # ---------- UI helpers ----------
    def _row(self, label: str, widget: QWidget) -> QHBoxLayout:
        r = QHBoxLayout()
        r.addWidget(QLabel(label))
        r.addWidget(widget, 1)
        return r


    def set_taratassi_readonly(self, readonly: bool) -> None:
        self.taratassi.setReadOnly(readonly)
        # opzionale: rendilo anche visivamente "non editabile"
        # self.taratassi.setStyleSheet("background:#f3f3f3;" if readonly else "")

    # ---------- WHZ logic (spostata da FormTab) ----------
    def _get_age(self) -> int:
        dichiarata = int(self.declared_age.value())
        stimata = int(self.age_estimation.value())
        if abs(dichiarata - stimata) > 3:
            return stimata
        return dichiarata

    def _get_quantized_height(self) -> float:
        d = Decimal(str(self.height.value()))
        # arrotonda a 0.5 (utile perché le chiavi LMS sono ogni 0.5 cm)
        return float(d.quantize(Decimal("0.5"), rounding=ROUND_HALF_UP))

    def _get_lms_values(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        age = self._get_age()
        sex = self.gender.currentText()
        height = self._get_quantized_height()
        if not height:
            return None, None, None

        if sex == "Maschio":
            sex_key = "boys"
        elif sex == "Femmina":
            sex_key = "girls"
        else:
            return None, None, None

        age_key = "0_2" if age <= 24 else "2_5"

        table = LMS.get(sex_key, {}).get(age_key, {})
        vals = table.get(height)
        if not vals:
            return None, None, None
        return vals[0], vals[1], vals[2]

    def _update_whz_status(self):
        text = (self.whz.text() or "").strip()
        try:
            v = float(text.replace(",", "."))
        except ValueError:
            self.whz_status.setText("")
            self.whz_status.setStyleSheet("")
            return


        color = 'inherit'
        if v >= -2:
            txt = "Non Malnutrito"
            bg_color = "2fb538"
        elif v >= -3:
            txt = "Malnutrizione Moderata"
            color = '000'
            bg_color = "cedb3b"
        else:
            txt = "Malnutrizione Severa"
            bg_color = "e03d3a"

        style = f"""
                QLineEdit {{
                    background-color: #{bg_color};
                    color: #{color};
                    font-weight: 600;
                    border: 1px solid #999;
                    border-radius: 6px;
                    padding: 4px;
                }}
                """

        self.whz_status.setText(txt)
        self.whz_status.setStyleSheet(style)

    def _update_whz_value(self) -> None:
        try:
            l, m, s = self._get_lms_values()
            weight = float(self.weight.value())

            if l is None or m is None or s is None or weight <= 0:
                self.whz.setText("")
                return

            whz = round(compute_whz(weight, l, m, s), 1)
            self.whz.setText(str(whz))
            self._update_whz_status()
        except Exception:
            # se height fuori range LMS, ecc.
            self.whz.setText("")

    def _force_uppercase(self, text):
        widget = self.sender()
        if widget is None:
            return

        upper = text.upper()
        if text != upper:
            widget.setText(upper)

    # ---------- Build UI ----------
    def _build(self) -> None:
        lay = QVBoxLayout(self)

        # Taratassi
        self.taratassi = QLineEdit()
        self.taratassi.textChanged.connect(self._force_uppercase)
        lay.addLayout(self._row("N° Taratassi", self.taratassi))

        # village
        self.village = QComboBox()
        self.village.addItems(VILLAGGI)
        lay.addLayout(self._row("Villaggio", self.village))

        # Consensi
        self.consent = QCheckBox("Sì")
        self.witnessed = QCheckBox("Sì")
        lay.addWidget(QLabel("Spiegazione consenso informato"))
        lay.addWidget(self.consent)
        lay.addWidget(QLabel("Consenso orale con testimone"))
        lay.addWidget(self.witnessed)

        # Età mesi dichiarata
        self.declared_age = QSpinBox()
        self.declared_age.setRange(0, 2400)
        self.declared_age.editingFinished.connect(self._update_whz_value)
        lay.addLayout(self._row("Età in mesi dichiarata", self.declared_age))

        # Età mesi stimata
        self.age_estimation = QSpinBox()
        self.age_estimation.setRange(0, 2400)
        self.age_estimation.editingFinished.connect(self._update_whz_value)
        lay.addLayout(self._row("Età in mesi stimata", self.age_estimation))

        # gender
        self.gender = QComboBox()
        self.gender.addItems(SESSI)
        self.gender.currentIndexChanged.connect(self._update_whz_value)
        lay.addLayout(self._row("Sesso", self.gender))

        # Misure
        self.muac = QDoubleSpinBox()
        self.muac.setRange(0, 1000)
        self.muac.setDecimals(2)
        self.muac.setSingleStep(0.1)
        lay.addLayout(self._row("Circonferenza braccio in cm (MUAC)", self.muac))

        self.weight = QDoubleSpinBox()
        self.weight.setRange(0, 1000)
        self.weight.setDecimals(2)
        self.weight.setSingleStep(0.1)
        self.weight.editingFinished.connect(self._update_whz_value)
        lay.addLayout(self._row("Peso (Kg)", self.weight))

        self.height = QDoubleSpinBox()
        self.height.setRange(0, 300)
        self.height.setDecimals(1)   # uguale alla creazione
        self.height.setSingleStep(0.5)
        self.height.editingFinished.connect(self._update_whz_value)
        lay.addLayout(self._row("Altezza (cm)", self.height))

        self.whz = QLineEdit()
        self.whz.setReadOnly(True)
        self.whz.setPlaceholderText("Viene calcolato automaticamente")
       # lay.addLayout(self._row("Indice WHZ", self.whz))

        # nuovo campo dinamico
        self.whz_status = QLineEdit()
        self.whz_status.setReadOnly(True)
        self.whz_status.setAlignment(Qt.AlignCenter)
        self.whz_status.setFixedWidth(220)  # scegli tu
        self.whz_status.setPlaceholderText("Livello Malnutrizione")

        # container riga: WHZ + Status
        whz_row_widget = QWidget()
        whz_row_lay = QHBoxLayout(whz_row_widget)
        whz_row_lay.setContentsMargins(0, 0, 0, 0)
        whz_row_lay.setSpacing(10)
        whz_row_lay.addWidget(self.whz, 1)  # prende spazio
        whz_row_lay.addWidget(self.whz_status, 0)  # fisso

        lay.addLayout(self._row("Indice WHZ", whz_row_widget))

        # Domande (uguali alla creazione)
        self.q1 = QComboBox(); self.q1.addItems(YES_NO_NS)
        self.q2 = QComboBox(); self.q2.addItems(YES_NO)
        self.q3 = QComboBox(); self.q3.addItems(YES_NO_NS)
        self.q4 = QComboBox(); self.q4.addItems(YES_NO_NS)
        self.q5 = QComboBox(); self.q5.addItems(YES_NO)

        lay.addLayout(self._row("Negli ultimi 7 giorni ha mangiato meno/rifiutato cibo?", self.q1))
        lay.addLayout(self._row("Ieri ha mangiato almeno 3 volte (oltre al latte)?", self.q2))
        lay.addLayout(self._row("Diarrea ultime 2 settimane?", self.q3))
        lay.addLayout(self._row("Febbre ultime 2 settimane?", self.q4))
        lay.addLayout(self._row("Prende ancora latte materno?", self.q5))

        lay.addStretch(1)

    # ---------- Data binding ----------
    def clear(self) -> None:
        self.taratassi.setText("")
        self.village.setCurrentIndex(0)
        self.consent.setChecked(False)
        self.witnessed.setChecked(False)
        self.declared_age.setValue(0)
        self.age_estimation.setValue(0)
        self.gender.setCurrentIndex(0)
        self.muac.setValue(0)
        self.weight.setValue(0)
        self.height.setValue(0)
        self.q1.setCurrentIndex(0)
        self.q2.setCurrentIndex(0)
        self.q3.setCurrentIndex(0)
        self.q4.setCurrentIndex(0)
        self.q5.setCurrentIndex(0)
        self.whz.setText("")

    def get_data(self) -> Dict[str, Any]:
        # Forza ricalcolo WHZ prima di leggere il valore
        self._update_whz_value()

        return {
            "taratassi": self.taratassi.text().strip(),
            "village": self.village.currentText(),
            "consent": bool_to_int(self.consent.isChecked()),
            "witnessed": bool_to_int(self.witnessed.isChecked()),
            "declared_age": int(self.declared_age.value()),
            "age_estimation": int(self.age_estimation.value()),
            "gender": self.gender.currentText(),
            "muac": float(self.muac.value()) if self.muac.value() != 0 else None,
            "weight": float(self.weight.value()) if self.weight.value() != 0 else None,
            "height": float(self.height.value()) if self.height.value() != 0 else None,
            "whz": float(self.whz.text()) if self.whz.text() else None,
            "q1": self.q1.currentText(),
            "q2": self.q2.currentText(),
            "q3": self.q3.currentText(),
            "q4": self.q4.currentText(),
            "q5": self.q5.currentText(),
        }

    def set_data(self, row: Dict[str, Any]) -> None:
        # blocca segnali se vuoi evitare calcoli WHZ intermedi mentre setti valori
        self.taratassi.setText(row.get("taratassi", "") or "")
        self.village.setCurrentText(row.get("village", "-") or "-")
        self.consent.setChecked((row.get("consent") or 0) == 1)
        self.witnessed.setChecked((row.get("witnessed") or 0) == 1)

        self.declared_age.setValue(int(row.get("declared_age") or 0))
        self.age_estimation.setValue(int(row.get("age_estimation") or 0))  # <-- fix bug: era declared_age
        self.gender.setCurrentText(row.get("gender", "-") or "-")

        self.muac.setValue(float(row.get("muac") or 0))
        self.weight.setValue(float(row.get("weight") or 0))
        self.height.setValue(float(row.get("height") or 0))

        self.q1.setCurrentText(row.get("q1", "-") or "-")
        self.q2.setCurrentText(row.get("q2", "-") or "-")
        self.q3.setCurrentText(row.get("q3", "-") or "-")
        self.q4.setCurrentText(row.get("q4", "-") or "-")
        self.q5.setCurrentText(row.get("q5", "-") or "-")

        # ricalcola WHZ e, se non calcolabile, mostra quello salvato (se presente)
        self._update_whz_value()
        if not self.whz.text() and row.get("whz") is not None:
            self.whz.setText(str(row["whz"]))

    # ---------- Validation ----------
    def validate(self, data: Optional[Dict[str, Any]] = None, *, require_taratassi: bool = True) -> Tuple[bool, str]:
        if data is None:
            data = self.get_data()

        labels = {
            "taratassi": "N° Taratassi",
            "village": "Village",
            "consent": "Spiegazione consenso informato",
            "witnessed": "Consenso orale con testimone",
            "declared_age": "Età in mesi dichiarata",
            "age_estimation": "Età in mesi stimata",
            "gender": "Sesso",
            "muac": "MUAC",
            "weight": "Peso",
            "height": "Altezza",
            "whz": "WHZ",
        }

        # ordine “umano” (simile al tuo)
        ordered_keys = [
            "taratassi", "village",
            "consent", "witnessed",
            "declared_age", "age_estimation", "gender",
            "muac", "weight", "height", "whz",
            "q1", "q2", "q3", "q4", "q5"
        ]

        for key in ordered_keys:
            if key == "taratassi" and not require_taratassi:
                continue

            value = data.get(key)

            missing = False
            if key in ("village", "gender", "q1", "q2", "q3", "q4", "q5"):
                missing = (value is None) or (value == "") or (value == "-")
            elif key in ("consent", "witnessed"):
                missing = (value != 1)  # devono essere spuntati
            elif key in ("declared_age", "age_estimation"):
                missing = (value is None) or (int(value) <= 0)
            elif key == "whz":
                # IMPORTANT: whz=0.0 è valido, quindi controlla solo None
                missing = (value is None)
            else:
                # muac/weight/height: se 0 li trasformiamo in None, quindi basta None
                missing = (value is None)

            if missing:
                if key.startswith("q"):
                    return False, f"Domanda {key[1:]} mancante"
                return False, f"{labels.get(key, key)} è obbligatorio."

        return True, ""

class FormTab(QWidget):
    def __init__(self, on_saved_callback):
        super().__init__()
        self.on_saved_callback = on_saved_callback
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # form riusabile
        self.form = RegistryForm(taratassi_readonly=False)
        lay.addWidget(self.form, 1)

        # Pulsanti
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Salva compilazione")
        self.clear_btn = QPushButton("Svuota form")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.clear_btn)
        lay.addLayout(btns)

        self.save_btn.clicked.connect(self._save)
        self.clear_btn.clicked.connect(self.form.clear)

    def _save(self):
        data = self.form.get_data()
        ok, msg = self.form.validate(data, require_taratassi=True)
        if not ok:
            QMessageBox.warning(self, "Errore", msg)
            return

        try:
            insert_registry(data)
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Errore salvataggio", "N° Taratassi già esistente.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))
            return

        QMessageBox.information(self, "OK", "Compilazione salvata correttamente.")
        self.on_saved_callback()
        self.form.clear()

class EditDialog(QDialog):
    def __init__(self, taratassi: str, parent=None):
        super().__init__(parent)
        self.taratassi_value = taratassi
        self.setWindowTitle(f"Modifica: {taratassi}")
        self.resize(700, 600)
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)

        # stesso form della creazione, ma taratassi in sola lettura
        self.form = RegistryForm(taratassi_readonly=True, parent=self)
        lay.addWidget(self.form, 1)

        btns = QHBoxLayout()
        self.save_btn = QPushButton("Salva modifiche")
        self.cancel_btn = QPushButton("Annulla")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        lay.addLayout(btns)

        self.save_btn.clicked.connect(self._save)
        self.cancel_btn.clicked.connect(self.reject)

    def _load(self):
        row = get_registry(self.taratassi_value)
        if not row:
            QMessageBox.critical(self, "Errore", "Record non trovato.")
            self.reject()
            return

        self.form.set_data(row)

    def _save(self):
        full_data = self.form.get_data()

        ok, msg = self.form.validate(full_data, require_taratassi=True)
        if not ok:
            QMessageBox.warning(self, "Errore", msg)
            return

        # taratassi non va aggiornato (chiave), quindi lo togliamo dall'update
        data = dict(full_data)
        data.pop("taratassi", None)

        try:
            update_registry(self.taratassi_value, data)
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))
            return

        QMessageBox.information(self, "OK", "Modifiche salvate.")
        self.accept()

class ResultsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self.refresh()

    def _build(self):
        lay = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cerca Taratassi...")
        self.refresh_btn = QPushButton("Aggiorna")
        self.export_btn = QPushButton("Esporta CSV")
        self.edit_btn = QPushButton("Modifica selezionato")
        top.addWidget(self.edit_btn)

        top.addWidget(self.search, 1)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.export_btn)
        lay.addLayout(top)

        self.table = QTableWidget()
        lay.addWidget(self.table, 1)

        self.refresh_btn.clicked.connect(self.refresh)
        self.search.textChanged.connect(self.refresh)
        self.export_btn.clicked.connect(self.export_csv)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.table.cellDoubleClicked.connect(self.edit_selected)

    def refresh(self):
        rows = list_registry(self.search.text())
        self._fill(rows)

    def _fill(self, rows):
        db_headers = [
            "taratassi", "village", "declared_age", "age_estimation", "gender",
            "muac", "weight", "height", "whz",
            "q1","q2","q3","q4","q5",
            "created_at"
        ]
        header_labels = [
            "Taratassi", "Villaggio", "Età dichiarata", "Età stimata", "Sesso",
            "MUAC", "Peso", "Altezza", "WHZ",
            "Domanda 1", "Domanda 2", "Domanda 3", "Domanda 4", "Domanda 5",
            "Data creazione"
        ]
        self.table.setColumnCount(len(db_headers))
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.setRowCount(len(rows))

        for r_i, r in enumerate(rows):
            for c_i, h in enumerate(db_headers):
                v = r[h]

                item = QTableWidgetItem("" if v is None else str(v))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # sola lettura
                self.table.setItem(r_i, c_i, item)

        self.table.resizeColumnsToContents()

    def export_csv(self):
        rows = list_registry(self.search.text())
        if not rows:
            QMessageBox.information(self, "Nessun dato", "Non ci sono record da esportare.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salva CSV", "risultati.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            export_rows_to_csv(rows, path)
            QMessageBox.information(self, "OK", "CSV esportato correttamente.")
        except Exception as e:
            QMessageBox.critical(self, "Errore export", str(e))

    def _selected_taratassi(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)  # colonna taratassi
        return item.text().strip() if item else None

    def edit_selected(self, *_):
        tar = self._selected_taratassi()
        if not tar:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga da modificare.")
            return

        dlg = EditDialog(tar, self)
        if dlg.exec():
            self.refresh()

class UpdateWorker(QObject):
    finished = Signal(object)   # Path | None
    error = Signal(str)

    @Slot()
    def run(self):
        try:
            path = check_update_and_download()
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))


class InfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(12)

        self.lbl_title = QLabel("<h2>Info</h2>")
        lay.addWidget(self.lbl_title)

        self.lbl_version = QLabel(f"<b>Versione attuale:</b> v{__version__}")
        lay.addWidget(self.lbl_version)

        self.lbl_repo = QLabel(f'<b>Repository:</b> <a href="{REPO_URL}">{REPO_URL}</a>')
        self.lbl_repo.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.lbl_repo.setOpenExternalLinks(True)
        lay.addWidget(self.lbl_repo)

        self.btn_updates = QPushButton("Cerca aggiornamenti")
        self.btn_updates.clicked.connect(self.on_check_updates)
        lay.addWidget(self.btn_updates)

        self.lbl_status = QLabel("")
        lay.addWidget(self.lbl_status)

        lay.addStretch(1)

    def on_check_updates(self):
        self.btn_updates.setEnabled(False)
        self.lbl_status.setText("Controllo aggiornamenti... (potrebbero volerci diversi minuti)")

        # Thread per non bloccare la GUI
        self.thread = QThread(self)
        self.worker = UpdateWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_update_finished)
        self.worker.error.connect(self.on_update_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_update_finished(self, path):
        self.btn_updates.setEnabled(True)
        self.lbl_status.setText("")

        if path is None:
            QMessageBox.information(self, "Aggiornamenti", "Sei già aggiornato ✅")
            return

        msg = (
            "Aggiornamento scaricato ✅\n\n"
            f"File: {path}\n\n"
            "Per aggiornare:\n"
            "1) Chiudi l'app\n"
            "2) Estrai lo zip\n"
            "3) Sostituisci i file dell'app (NON il database)"
        )
        box = QMessageBox(self)
        box.setWindowTitle("Aggiornamenti")
        box.setText(msg)

        open_btn = box.addButton("Apri cartella download", QMessageBox.ActionRole)
        box.addButton("OK", QMessageBox.AcceptRole)

        box.exec()

        if box.clickedButton() == open_btn:
            # apri cartella contenente lo zip
            folder = str(path.parent)
            webbrowser.open(f"file://{folder}")

    def on_update_error(self, err: str):
        self.btn_updates.setEnabled(True)
        self.lbl_status.setText("")
        QMessageBox.critical(self, "Aggiornamenti", f"Errore:\n\n{err}")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.version = __version__
        self.setWindowTitle(f"Questionario Malnutrizione - v{self.version}")
        self.resize(1100, 700)

        lay = QVBoxLayout(self)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs)

        self.results_tab = ResultsTab()
        self.form_tab = FormTab(on_saved_callback=self.results_tab.refresh)
        self.info_tab = InfoTab()

        self.tabs.addTab(self.form_tab, "Nuova compilazione")
        self.tabs.addTab(self.results_tab, "Risultati")
        self.tabs.addTab(self.info_tab, "Informazioni")


def main():
    init_db()
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
