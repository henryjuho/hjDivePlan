#!/usr/bin/env python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import pyqtgraph as pg
import numpy as np


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 1050, 700)  # coords start from top left x, y, width, height
        self.setWindowTitle('Dive planner')

        # set toolbar
        run_plan = QtGui.QAction(QtGui.QIcon('images/play.png'), 'run', self)
        QtGui.QAction.connect(run_plan, QtCore.SIGNAL('triggered()'), self.run_calculation)
        toolbar = self.addToolBar('Run')
        toolbar.addAction(run_plan)
        exit_planner = QtGui.QAction(QtGui.QIcon('images/exit.png'), 'exit', self)
        QtGui.QAction.connect(exit_planner, QtCore.SIGNAL('triggered()'), self.quit_app)
        toolbar.addAction(exit_planner)

        # fonts
        self.header_font = QtGui.QFont('SansSerif', 18)
        self.header_font.setBold(True)
        self.main_font = QtGui.QFont('SansSerif', 16)
        self.options_font = QtGui.QFont('Arial', 14)

        # start main layout
        whole_layout = QtGui.QVBoxLayout()
        whole_layout.addSpacerItem(QtGui.QSpacerItem(120, 10))

        # dive dict
        self.dive_dict = {1: {'d': 0, 't': 0}, 2: {'d': 0, 't': 0}}

        # settings row
        settings_boxes = QtGui.QHBoxLayout()
        settings_boxes.addWidget(self.dive_set_box())
        settings_boxes.addWidget(self.gas_box())
        whole_layout.addLayout(settings_boxes)
        whole_layout.addSpacerItem(QtGui.QSpacerItem(120, 10))

        # plot box
        plot_box = QtGui.QGroupBox('Dive profile')
        plot_box.setFont(self.header_font)
        plot_layout = QtGui.QHBoxLayout()
        self.plot_widget = pg.PlotWidget()
        plot_layout.addWidget(self.plot_widget)
        plot_box.setLayout(plot_layout)
        whole_layout.addWidget(plot_box)

        # param box
        whole_layout.addWidget(self.param_box())

        # push to top and set layout
        # whole_layout.addStretch(1)
        # self.setLayout(whole_layout)

        main_widget = QtGui.QWidget()
        main_widget.setLayout(whole_layout)
        self.setCentralWidget(main_widget)
        self.show()

    def quit_app(self):

        choice = QtGui.QMessageBox.question(self, 'Exit', 'Exit the application?',
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)

        if choice == QtGui.QMessageBox.Yes:
            sys.exit()

        else:
            pass

    def dive_set_box(self):
        # settings group box
        dive_set_box = QtGui.QGroupBox('Dive settings')
        dive_set_box.setFont(self.header_font)

        # start settings layouts
        settings_layout_time = QtGui.QHBoxLayout()
        settings_layout_depth = QtGui.QHBoxLayout()

        # dive 1 data
        d1time = QtGui.QLabel('First dive time:  ', self)
        d1time.setFont(self.main_font)
        d1time.resize(200, 20)
        settings_layout_time.addWidget(d1time)
        self.dt1 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dt1, QtCore.SIGNAL('returnPressed()'), self.store_dt1)
        self.dt1.resize(50, 20)
        self.dt1.setPlaceholderText('time 1')
        self.dt1.setFont(self.options_font)
        settings_layout_time.addWidget(self.dt1)
        d1depth = QtGui.QLabel('First dive depth:', self)
        d1depth.setFont(self.main_font)
        d1depth.resize(200, 20)
        settings_layout_depth.addWidget(d1depth)
        self.dd1 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dd1, QtCore.SIGNAL('returnPressed()'), self.store_dd1)
        self.dd1.resize(50, 20)
        self.dd1.setPlaceholderText('depth 1')
        self.dd1.setFont(self.options_font)
        settings_layout_depth.addWidget(self.dd1)

        # dive 2 data
        d2time = QtGui.QLabel('Second dive time:  ', self)
        d2time.setFont(self.main_font)
        d2time.resize(200, 20)
        settings_layout_time.addWidget(d2time)
        self.dt2 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dt2, QtCore.SIGNAL('returnPressed()'), self.store_dt2)
        self.dt2.resize(50, 20)
        self.dt2.setPlaceholderText('time 2')
        self.dt2.setFont(self.options_font)
        settings_layout_time.addWidget(self.dt2)
        d2depth = QtGui.QLabel('Second dive depth:', self)
        d2depth.setFont(self.main_font)
        d2depth.resize(200, 20)
        settings_layout_depth.addWidget(d2depth)
        self.dd2 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dd2, QtCore.SIGNAL('returnPressed()'), self.store_dd2)
        self.dd2.resize(50, 20)
        self.dd2.setPlaceholderText('depth 2')
        self.dd2.setFont(self.options_font)
        settings_layout_depth.addWidget(self.dd2)
        stack_sets = QtGui.QVBoxLayout()
        stack_sets.addLayout(settings_layout_time)
        stack_sets.addLayout(settings_layout_depth)
        dive_set_box.setLayout(stack_sets)

        return dive_set_box

    def gas_box(self):

        # row one
        gas_box_row1 = QtGui.QHBoxLayout()

        # mix
        mix_label = QtGui.QLabel('Gas mix (% O2): ', self)
        mix_label.setFont(self.main_font)
        mix_label.resize(200, 20)
        gas_box_row1.addWidget(mix_label)
        self.g_mix = QtGui.QComboBox(self)
        for i in range(21, 37):
            self.g_mix.addItem(str(i))
        self.g_mix.setFont(self.options_font)
        #QtGui.QComboBox.connect(self.g_mix, QtCore.SIGNAL('returnPressed()'), self.store_g_mix)
        self.g_mix.resize(50, 20)
        gas_box_row1.addWidget(self.g_mix)

        # sac
        sac_label = QtGui.QLabel('SAC rate l/min: ', self)
        sac_label.setFont(self.main_font)
        sac_label.resize(200, 20)
        gas_box_row1.addWidget(sac_label)
        self.sac = QtGui.QComboBox(self)
        for i in range(10, 51):
            self.sac.addItem(str(i))
        self.sac.setFont(self.options_font)
        # QtGui.QComboBox.connect(self.g_mix, QtCore.SIGNAL('returnPressed()'), self.store_g_mix)
        self.sac.resize(50, 20)
        gas_box_row1.addWidget(self.sac)

        # row two
        gas_box_row2 = QtGui.QHBoxLayout()

        # po2
        po2_label = QtGui.QLabel('max pO2 (bar):   ', self)
        po2_label.setFont(self.main_font)
        po2_label.resize(200, 20)
        gas_box_row2.addWidget(po2_label)
        self.po2 = QtGui.QComboBox(self)
        for i in range(0, 7):
            self.po2.addItem('1.' + str(i))
        self.po2.setFont(self.options_font)
        # QtGui.QLineEdit.connect(self.g_mix, QtCore.SIGNAL('returnPressed()'), self.store_g_mix)
        self.po2.resize(50, 20)
        gas_box_row2.addWidget(self.po2)

        # cylinder size
        cyl_label = QtGui.QLabel('cylinder size (l):', self)
        cyl_label.setFont(self.main_font)
        cyl_label.resize(200, 20)
        gas_box_row2.addWidget(cyl_label)
        self.cyl_size = QtGui.QComboBox(self)
        for i in range(3, 16):
            self.cyl_size.addItem(str(i))
        self.cyl_size.setFont(self.options_font)
        # QtGui.QLineEdit.connect(self.g_mix, QtCore.SIGNAL('returnPressed()'), self.store_g_mix)
        self.cyl_size.resize(50, 20)
        gas_box_row2.addWidget(self.cyl_size)

        gas_set_stack = QtGui.QVBoxLayout()
        gas_set_stack.addLayout(gas_box_row1)
        gas_set_stack.addLayout(gas_box_row2)

        gas_set_box = QtGui.QGroupBox('Gas settings')
        gas_set_box.setFont(self.header_font)
        gas_set_box.setLayout(gas_set_stack)

        return gas_set_box

    def param_box(self):
        param_box = QtGui.QGroupBox('Dive parameters')
        param_box.setFont(self.header_font)
        param_layout = QtGui.QGridLayout()

        pres_end_d1_lab = QtGui.QLabel('Dive 1 end pressure:', self)
        pres_end_d1_lab.setFont(self.main_font)
        param_layout.addWidget(pres_end_d1_lab, 0, 0)

        pres_begin_d2_lab = QtGui.QLabel('Dive 2 start pressure:', self)
        pres_begin_d2_lab.setFont(self.main_font)
        param_layout.addWidget(pres_begin_d2_lab, 1, 0)

        pres_end_d2_lab = QtGui.QLabel('Dive 2 end pressure:', self)
        pres_end_d2_lab.setFont(self.main_font)
        param_layout.addWidget(pres_end_d2_lab, 2, 0)

        min_si_lab = QtGui.QLabel('Min surface interval:', self)
        min_si_lab.setFont(self.main_font)
        param_layout.addWidget(min_si_lab, 3, 0)

        mod_lab = QtGui.QLabel('MOD of gas:', self)
        mod_lab.setFont(self.main_font)
        param_layout.addWidget(mod_lab, 0, 2)

        gas_vol_d1_lab = QtGui.QLabel('Gas volume dive 1 (l):', self)
        gas_vol_d1_lab.setFont(self.main_font)
        param_layout.addWidget(gas_vol_d1_lab, 1, 2)

        gas_vol_d2_lab = QtGui.QLabel('Gas volume dive 2 (l):', self)
        gas_vol_d2_lab.setFont(self.main_font)
        param_layout.addWidget(gas_vol_d2_lab, 2, 2)

        cyl_req_lab = QtGui.QLabel('Cylinder requirements:', self)
        cyl_req_lab.setFont(self.main_font)
        param_layout.addWidget(cyl_req_lab, 3, 2)

        param_box.setLayout(param_layout)
        return param_box

    def run_calculation(self):

        # if dive data for at least dive one not entered warns
        if 0 in self.dive_dict[1].values():
            QtGui.QMessageBox.warning(self, 'No data', 'You must enter data for at least 1 dive!', QtGui.QMessageBox.Ok)
        else:
            t1 = self.dive_dict[1]['t']
            d1 = self.dive_dict[1]['d']
            t2 = self.dive_dict[2]['t']
            d2 = self.dive_dict[2]['d']

            new_plot_data = create_profile(t1, d1, t2, d2)
            self.plot_widget.plotItem.clear()
            self.plot_widget.plot(new_plot_data[0], new_plot_data[1])

    def store_dt1(self):
        self.dive_dict[1]['t'] = float(self.dt1.text())

    def store_dt2(self):
        self.dive_dict[2]['t'] = float(self.dt2.text())

    def store_dd1(self):
        self.dive_dict[1]['d'] = float(self.dd1.text())

    def store_dd2(self):
        self.dive_dict[2]['d'] = float(self.dd2.text())


def create_profile(t1, d1, t2, d2):
    # DIVE ONE
    # calc ascent and descent times
    t_per_m_desc = 1.0 / 30.0  # 30m per min descent rate
    t_per_m_asc = 1.0 / 15.0  # 15m per min to 6m
    t_per_m_asc_6 = 1.0 / 6  # 6m per min above 6m
    safety2surf = 1
    stop_t = 3
    desc_1_time = t_per_m_desc * d1
    asc_1_time2safety = t_per_m_asc * (d1 - 6)
    d1_bt = t1 - desc_1_time - asc_1_time2safety - safety2surf - stop_t

    # DIVE TWO
    desc_2_time = t_per_m_desc * d2
    asc_2_time2safety = t_per_m_asc * (d2 - 6)
    d2_bt = t2 - desc_2_time - asc_2_time2safety - safety2surf

    # SURFACE INTERVAL
    interval = 30

    # PROFILE
    x = [0, desc_1_time, d1_bt, asc_1_time2safety, stop_t, safety2surf, interval,
         desc_2_time, d2_bt, asc_2_time2safety, stop_t, safety2surf]
    x_cum = np.cumsum(x)
    y = [0, -d1, -d1, -6, -6, 0, 0, -d2, -d2, -6, -6, 0]

    return x_cum, y


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
