#!/usr/bin/env python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import padi_tables
import daltons_utils as dl
import pypandoc
import os

class InfoPopup(QtGui.QDialog):
    def __init__(self, parent=None):
        super(InfoPopup, self).__init__(parent)
        self.setGeometry(325, 100, 625, 400)
        self.setWindowTitle('')

        # info fonts
        info_header_font = QtGui.QFont('SansSerif', 25)
        info_header_font.setBold(True)
        info_head_col = QtGui.QPalette()
        info_head_col.setColor(QtGui.QPalette.Foreground, QtCore.Qt.blue)
        sub_head_font = QtGui.QFont('SansSerif', 20)
        sub_head_font.setBold(True)
        text_font = QtGui.QFont('Arial', 15)

        # content
        info_layout = QtGui.QVBoxLayout()
        title_text = QtGui.QLabel('hjDivePlan')
        title_text.setFont(info_header_font)
        title_text.setPalette(info_head_col)
        info_layout.addWidget(title_text)

        info_layout.addStretch(1)

        about_title = QtGui.QLabel('About')
        about_title.setFont(sub_head_font)
        info_layout.addWidget(about_title)

        about_text = ('This program can be used to plan up to two dives, calculating gas requirements, '
                      'minimum surface intervals and other parameters according to the PADI recreational '
                      'dive planner (RDP) which can be found here:')
        about_text_qlabel = QtGui.QLabel(about_text)
        about_text_qlabel.setWordWrap(True)
        about_text_qlabel.setFont(text_font)
        info_layout.addWidget(about_text_qlabel)

        rdp_link = QtGui.QLabel('''<a href='http://elearning.padi.com/company0/tools/RDP_Table%20Met.pdf'>
                                http://elearning.padi.com/company0/tools/RDP_Table%20Met.pdf</a>''')
        rdp_link.setOpenExternalLinks(True)
        rdp_link.setFont(text_font)
        info_layout.addWidget(rdp_link)

        doc_text = 'Full documentation for this package can be found on github at the below link:'
        doc_text_qlabel = QtGui.QLabel(doc_text)
        doc_text_qlabel.setFont(text_font)
        info_layout.addWidget(doc_text_qlabel)

        readme_link = QtGui.QLabel('''<a href='https://github.com/henryjuho/hjDivePlan'>
                                   https://github.com/henryjuho/hjDivePlan</a>''')
        readme_link.setOpenExternalLinks(True)
        readme_link.setFont(text_font)
        info_layout.addWidget(readme_link)

        info_layout.addStretch(2)

        disclaimer_title = QtGui.QLabel('Disclaimer')
        disclaimer_title.setFont(sub_head_font)
        info_layout.addWidget(disclaimer_title)

        disclaimer_text = ('The accuracy of this program cannot be guaranteed and should by no means be used '
                           'as a sole source of dive planning. Also it should be noted that all dives are '
                           'planned as if on air, even if gas mix > 21% 02.')
        disclaimer_text_qlabel = QtGui.QLabel(disclaimer_text)
        disclaimer_text_qlabel.setWordWrap(True)
        disclaimer_text_qlabel.setFont(text_font)
        info_layout.addWidget(disclaimer_text_qlabel)

        info_layout.addStretch(3)

        self.setLayout(info_layout)


class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, header, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.header = header

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None


class TablePopup(QtGui.QDialog):
    def __init__(self, header, my_array, title, offset, parent=None):
        super(TablePopup, self).__init__(parent)

        self.setWindowTitle(title)
        self.setGeometry(120+offset, 120, 1000, 500)
        self.table_viewer = QtGui.QTableView(self)
        self.table_viewer.setModel(MyTableModel(my_array, header))
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.table_viewer)


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100, 100, 1050, 700)  # coords start from top left x, y, width, height
        self.setWindowTitle('hjDivePlan')

        # set toolbar
        toolbar = QtGui.QToolBar(self)
        run_plan = QtGui.QAction(QtGui.QIcon('images/play.png'), 'run', self)
        QtGui.QAction.connect(run_plan, QtCore.SIGNAL('triggered()'), self.run_calculation)
        run_plan.setShortcut('Ctrl+R')
        toolbar.addAction(run_plan)
        tables = QtGui.QAction(QtGui.QIcon('images/tables.png'), 'tables', self)
        QtGui.QAction.connect(tables, QtCore.SIGNAL('triggered()'), self.display_tables)
        tables.setShortcut('Ctrl+T')
        toolbar.addAction(tables)
        save = QtGui.QAction(QtGui.QIcon('images/save.png'), 'save', self)
        QtGui.QAction.connect(save, QtCore.SIGNAL('triggered()'), self.save_plan)
        tables.setShortcut('Ctrl+S')
        toolbar.addAction(save)
        print_button = QtGui.QAction(QtGui.QIcon('images/print.png'), 'print', self)
        QtGui.QAction.connect(save, QtCore.SIGNAL('triggered()'), self.print_plan)
        tables.setShortcut('Ctrl+P')
        toolbar.addAction(print_button)
        info = QtGui.QAction(QtGui.QIcon('images/info2.png'), 'info', self)
        QtGui.QAction.connect(info, QtCore.SIGNAL('triggered()'), self.display_info)
        info.setShortcut('Ctrl+I')
        toolbar.addAction(info)
        exit_planner = QtGui.QAction(QtGui.QIcon('images/exit.png'), 'exit', self)
        exit_planner.setShortcut('Ctrl+Q')
        QtGui.QAction.connect(exit_planner, QtCore.SIGNAL('triggered()'), self.quit_app)
        toolbar.addAction(exit_planner)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, toolbar)

        # fonts
        self.header_font = QtGui.QFont('SansSerif', 16)
        self.header_font.setBold(True)
        self.main_font = QtGui.QFont('SansSerif', 16)
        self.options_font = QtGui.QFont('Arial', 14)
        self.param_palette = QtGui.QPalette()
        self.param_palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.blue)

        # start main layout
        whole_layout = QtGui.QVBoxLayout()
        whole_layout.addSpacerItem(QtGui.QSpacerItem(120, 10))

        # dive params
        self.dive_dict = {1: {'d': 0, 't': 0}, 2: {'d': 0, 't': 0}}
        self.g_mix_val = 21
        self.po2_value = 1.4
        self.cylinder_size_val = 12
        self.sac_rate_val = 25
        self.reserve_val = 'thirds'
        self.refill = False

        # settings row
        settings_boxes = QtGui.QHBoxLayout()
        settings_boxes.addWidget(self.dive_set_box())
        settings_boxes.addWidget(self.gas_box())
        whole_layout.addLayout(settings_boxes)
        whole_layout.addSpacerItem(QtGui.QSpacerItem(120, 10))

        # plot box
        # invert default background foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        plot_box = QtGui.QGroupBox('Dive profile')
        plot_box.setFont(self.header_font)
        plot_layout = QtGui.QHBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Depth', 'm')
        self.plot_widget.setLabel('bottom', 'Time', 'mins')
        self.plot_widget.setFont(self.main_font)
        plot_layout.addWidget(self.plot_widget)
        plot_box.setLayout(plot_layout)
        whole_layout.addWidget(plot_box)

        # param box
        whole_layout.addWidget(self.param_box())

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

    def display_info(self):
        info = InfoPopup()
        info.exec_()

    def display_tables(self):

        # get table 1 data into shape and display
        t1_head = sorted(padi_tables.padi_table_1.keys())
        t1_rows = sorted(padi_tables.end_pressure_groups)
        t1_data = [[x] for x in t1_rows]

        for depth in t1_head:
            flipped_dict = {x[1]: x[0] for x in padi_tables.padi_table_1[depth].items()}
            for i in range(0, len(t1_rows)):
                try:
                    abt = flipped_dict[t1_rows[i]]
                except KeyError:
                    abt = 'NA'
                t1_data[i].append(abt)

        table_1 = TablePopup([''] + t1_head, t1_data, 'Dive table', 0)
        table_1.exec_()

        # get surface table data into shape and display
        st_head = t1_rows
        st_rows = t1_rows
        st_data = [[x] for x in t1_rows]
        for x in st_head:
            start_pres_data = padi_tables.surface_table[x]
            for i in range(0, len(st_rows)):
                st_data[i].append('-'.join(start_pres_data[st_rows[i]]))

        table_st = TablePopup([''] + st_head, st_data, 'Surface table', 10)
        table_st.exec_()

        # get subsequent dives table
        t2_head = sorted(padi_tables.padi_table_2.keys())
        t2_rows = sorted(padi_tables.end_pressure_groups)
        t2_data = [[x] for x in t2_rows]

        for depth in t2_head:
            for i in range(0, len(t2_rows)):
                table_2_row_data = padi_tables.padi_table_2[depth]
                try:
                    time_data = str(table_2_row_data[t2_rows[i]][0]) + ', ' + str(table_2_row_data[t2_rows[i]][1])
                except KeyError:
                    time_data = '0, 0'
                t2_data[i].append(time_data)

        table_2 = TablePopup([''] + t2_head, t2_data, 'Repetitive dive table', 20)
        table_2.exec_()

    def save_plan(self):
        try:
            name = QtGui.QFileDialog.getSaveFileName(self, 'Save Plan')
            mk_down_str = self.output_plan(name)
            pypandoc.convert_text(mk_down_str, 'pdf', format='md', outputfile=name + '.pdf')
            os.remove(name + '.png')
        except AttributeError:
            QtGui.QMessageBox.warning(self, 'No plan', 'You must make a plan to save!', QtGui.QMessageBox.Ok)


    def print_plan(self):
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
        QtGui.QLineEdit.connect(self.dt1, QtCore.SIGNAL('textChanged (const QString&)'), self.store_dt1)
        self.dt1.resize(50, 20)
        self.dt1.setPlaceholderText('time 1')
        self.dt1.setFont(self.options_font)
        settings_layout_time.addWidget(self.dt1)
        d1depth = QtGui.QLabel('First dive depth:', self)
        d1depth.setFont(self.main_font)
        d1depth.resize(200, 20)
        settings_layout_depth.addWidget(d1depth)
        self.dd1 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dd1, QtCore.SIGNAL('textChanged (const QString&)'), self.store_dd1)
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
        QtGui.QLineEdit.connect(self.dt2, QtCore.SIGNAL('textChanged (const QString&)'), self.store_dt2)
        self.dt2.resize(50, 20)
        self.dt2.setPlaceholderText('time 2')
        self.dt2.setFont(self.options_font)
        settings_layout_time.addWidget(self.dt2)
        d2depth = QtGui.QLabel('Second dive depth:', self)
        d2depth.setFont(self.main_font)
        d2depth.resize(200, 20)
        settings_layout_depth.addWidget(d2depth)
        self.dd2 = QtGui.QLineEdit(self)
        QtGui.QLineEdit.connect(self.dd2, QtCore.SIGNAL('textChanged (const QString&)'), self.store_dd2)
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
        QtGui.QComboBox.connect(self.g_mix, QtCore.SIGNAL('activated(const QString&)'), self.store_g_mix)
        self.g_mix.setCurrentIndex(0)
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
        QtGui.QComboBox.connect(self.sac, QtCore.SIGNAL('activated(const QString&)'), self.store_sac)
        self.sac.setCurrentIndex(15)
        self.sac.resize(50, 20)
        gas_box_row1.addWidget(self.sac)

        # fills between dives?
        fills_label = QtGui.QLabel('Fills available? ', self)
        fills_label.setFont(self.main_font)
        fills_label.resize(200, 20)
        gas_box_row1.addWidget(fills_label)
        self.fills = QtGui.QCheckBox(self)
        QtGui.QCheckBox.connect(self.fills, QtCore.SIGNAL('stateChanged (int)'), self.store_fill)
        self.fills.resize(50, 20)
        gas_box_row1.addWidget(self.fills)

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
        self.po2.setCurrentIndex(4)
        self.po2.setFont(self.options_font)
        QtGui.QComboBox.connect(self.po2, QtCore.SIGNAL('activated(const QString&)'), self.store_po2)
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
        self.cyl_size.setCurrentIndex(9)
        self.cyl_size.setFont(self.options_font)
        QtGui.QComboBox.connect(self.cyl_size, QtCore.SIGNAL('activated(const QString&)'), self.store_cyl_size)
        self.cyl_size.resize(50, 20)
        gas_box_row2.addWidget(self.cyl_size)

        # reserve strategy
        reserve_label = QtGui.QLabel('Reserve: ', self)
        reserve_label.setFont(self.main_font)
        reserve_label.resize(200, 20)
        gas_box_row2.addWidget(reserve_label)
        self.reserve = QtGui.QComboBox(self)
        self.reserve.addItem(str('50 bar'))
        self.reserve.addItem(str('thirds'))
        self.reserve.setCurrentIndex(1)
        self.reserve.setFont(self.options_font)
        QtGui.QComboBox.connect(self.reserve, QtCore.SIGNAL('activated(const QString&)'), self.store_reserve)
        self.reserve.resize(50, 20)
        gas_box_row2.addWidget(self.reserve)

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
        self.pres_end_d1 = QtGui.QLabel('', self)
        self.pres_end_d1.setPalette(self.param_palette)
        self.pres_end_d1.setFont(self.main_font)
        param_layout.addWidget(self.pres_end_d1, 0, 1)

        pres_begin_d2_lab = QtGui.QLabel('Dive 2 start pressure:', self)
        pres_begin_d2_lab.setFont(self.main_font)
        param_layout.addWidget(pres_begin_d2_lab, 1, 0)
        self.pres_begin_d2 = QtGui.QLabel('', self)
        self.pres_begin_d2.setFont(self.main_font)
        self.pres_begin_d2.setPalette(self.param_palette)
        param_layout.addWidget(self.pres_begin_d2, 1, 1)

        pres_end_d2_lab = QtGui.QLabel('Dive 2 end pressure:', self)
        pres_end_d2_lab.setFont(self.main_font)
        param_layout.addWidget(pres_end_d2_lab, 2, 0)
        self.pres_end_d2 = QtGui.QLabel('', self)
        self.pres_end_d2.setFont(self.main_font)
        self.pres_end_d2.setPalette(self.param_palette)
        param_layout.addWidget(self.pres_end_d2, 2, 1)

        min_si_lab = QtGui.QLabel('Min surface interval:', self)
        min_si_lab.setFont(self.main_font)
        param_layout.addWidget(min_si_lab, 3, 0)
        self.min_si = QtGui.QLabel('', self)
        self.min_si.setFont(self.main_font)
        self.min_si.setPalette(self.param_palette)
        param_layout.addWidget(self.min_si, 3, 1)

        mod_lab = QtGui.QLabel('MOD of gas:', self)
        mod_lab.setFont(self.main_font)
        param_layout.addWidget(mod_lab, 0, 2)
        self.mod = QtGui.QLabel('', self)
        self.mod.setFont(self.main_font)
        self.mod.setPalette(self.param_palette)
        param_layout.addWidget(self.mod, 0, 3)

        gas_vol_d1_lab = QtGui.QLabel('Gas volume dive 1 (l):', self)
        gas_vol_d1_lab.setFont(self.main_font)
        param_layout.addWidget(gas_vol_d1_lab, 1, 2)
        self.gas_vol_d1_calced = QtGui.QLabel('', self)
        self.gas_vol_d1_calced.setFont(self.main_font)
        self.gas_vol_d1_calced.setPalette(self.param_palette)
        param_layout.addWidget(self.gas_vol_d1_calced, 1, 3)

        gas_vol_d2_lab = QtGui.QLabel('Gas volume dive 2 (l):', self)
        gas_vol_d2_lab.setFont(self.main_font)
        param_layout.addWidget(gas_vol_d2_lab, 2, 2)
        self.gas_vol_d2_calced = QtGui.QLabel('', self)
        self.gas_vol_d2_calced.setFont(self.main_font)
        self.gas_vol_d2_calced.setPalette(self.param_palette)
        param_layout.addWidget(self.gas_vol_d2_calced, 2, 3)

        cyl_req_lab = QtGui.QLabel('Cylinder requirements:', self)
        cyl_req_lab.setFont(self.main_font)
        param_layout.addWidget(cyl_req_lab, 3, 2)
        self.cyl_req_result = QtGui.QLabel('', self)
        self.cyl_req_result.setFont(self.main_font)
        self.cyl_req_result.setPalette(self.param_palette)
        param_layout.addWidget(self.cyl_req_result, 3, 3)

        param_box.setLayout(param_layout)
        return param_box

    def run_calculation(self):

        # if dive data for at least dive one not entered warns
        if 0 in self.dive_dict[1].values() or self.dive_dict[2].values().count(0) == 1:
            QtGui.QMessageBox.warning(self, 'No data', 'You must enter complete data for at least 1 dive!',
                                      QtGui.QMessageBox.Ok)
        else:
            t1 = self.dive_dict[1]['t']
            d1 = self.dive_dict[1]['d']
            t2 = self.dive_dict[2]['t']
            d2 = self.dive_dict[2]['d']

            if padi_tables.max_bottom_time(d1) <= t1:
                QtGui.QMessageBox.critical(self, 'Bottom time exceeded', 'The bottom time for dive 1 exceeds the '
                                           'maximum for the specified depth!', QtGui.QMessageBox.Ok)
            elif d2 != 0 and padi_tables.max_bottom_time(d2) <= t2:
                QtGui.QMessageBox.critical(self, 'Bottom time exceeded', 'The bottom time for dive 2 exceeds the '
                                           'maximum for the specified depth!', QtGui.QMessageBox.Ok)
            elif d1 > dl.mod(self.g_mix_val, self.po2_value) or d2 > dl.mod(self.g_mix_val, self.po2_value):
                QtGui.QMessageBox.critical(self, 'MOD exceeded', 'The maximum operating depth of your gas mix is less '
                                           'than your dive depth!', QtGui.QMessageBox.Ok)
            else:
                if d2 == t2 == 0:
                    single = True
                else:
                    single = False

                # pressure calculations
                self.d1_end_pressure = padi_tables.get_end_pres(t1, d1)
                self.pres_end_d1.setText(self.d1_end_pressure)

                if single is True:
                    self.d2_start_pressure = '-'
                    self.surface_interval = '-'
                    self.d2_end_pressure = '-'
                else:
                    min_d2_start_pressure = padi_tables.min_d2_start_pressure(d2, t2)
                    if min_d2_start_pressure > self.d1_end_pressure:
                        self.d2_start_pressure = self.d1_end_pressure
                    else:
                        self.d2_start_pressure = min_d2_start_pressure
                    self.surface_interval = padi_tables.min_surface(self.d1_end_pressure, d2, t2)
                    self.d2_end_pressure = padi_tables.repeat_dive_end_pressure(self.d2_start_pressure, d2, t2)

                self.pres_begin_d2.setText(self.d2_start_pressure)
                self.min_si.setText(str(self.surface_interval))
                self.pres_end_d2.setText(self.d2_end_pressure)

                # gas calculations
                self.mod_val = dl.mod(self.g_mix_val, self.po2_value)

                self.mod.setText(str(round(self.mod_val, 2)))
                dive_1_volume = self.sac_rate_val * dl.depth2pressure(self.dive_dict[1]['d']) * self.dive_dict[1]['t']
                dive_2_volume = self.sac_rate_val * dl.depth2pressure(self.dive_dict[2]['d']) * self.dive_dict[2]['t']

                if self.reserve_val == 'thirds':
                    reserve_volume_1 = dive_1_volume / 2.0
                    if single is False:
                        reserve_volume_2 = dive_2_volume / 2.0
                    else:
                        reserve_volume_2 = 0
                else:
                    reserve_volume_1 = 50 * self.cylinder_size_val
                    if single is False:
                        reserve_volume_2 = 50 * self.cylinder_size_val
                    else:
                        reserve_volume_2 = 0

                self.gas_vol_d1_calced.setText(str(dive_1_volume) + ' L + ' + str(reserve_volume_1) + ' L reserve')
                self.gas_vol_d2_calced.setText(str(dive_2_volume) + ' L + ' + str(reserve_volume_2) + ' L reserve')

                self.dive_1_total_v = dive_1_volume + reserve_volume_1
                self.dive_2_total_v = dive_2_volume + reserve_volume_2

                if self.refill is True:
                    cyls_needed_d1 = dl.cyl_reqs(self.dive_1_total_v, self.cylinder_size_val)
                    if single is False:
                        cyls_needed_d2 = dl.cyl_reqs(self.dive_2_total_v, self.cylinder_size_val)
                    else:
                        cyls_needed_d2 = [0, 0]
                    self.cyl_req_result.setText('dive 1: ' + str(int(cyls_needed_d1[0])) + ' @ ' +
                                                str(cyls_needed_d1[1]) + ' bar, '
                                                'dive 2:  ' + str(int(cyls_needed_d2[0])) + ' @ ' +
                                                str(cyls_needed_d2[1]) + ' bar')
                else:
                    cyls_needed_both = dl.cyl_reqs(self.dive_1_total_v + self.dive_2_total_v, self.cylinder_size_val)
                    self.cyl_req_result.setText('both dives: ' + str(int(cyls_needed_both[0])) + ' @ ' +
                                                str(cyls_needed_both[1]) + ' bar')

                # plotting
                plot_pen = pg.mkPen('b', width=2)
                new_plot_data = create_profile(t1, d1, t2, d2, self.surface_interval)
                self.plot_widget.plotItem.clear()
                self.plot_widget.plot(new_plot_data[0], new_plot_data[1], pen=plot_pen)

    def store_dt1(self, text):
        if text == '':
            text = 0
        self.dive_dict[1]['t'] = float(text)

    def store_dt2(self, text):
        if text == '':
            text = 0
        self.dive_dict[2]['t'] = float(text)

    def store_dd1(self, text):
        if text == '':
            text = 0
        self.dive_dict[1]['d'] = float(text)

    def store_dd2(self, text):
        if text == '':
            text = 0
        self.dive_dict[2]['d'] = float(text)

    def store_g_mix(self, text):
        self.g_mix_val = int(text)

    def store_po2(self, text):
        self.po2_value = float(text)

    def store_sac(self, text):
        self.sac_rate_val = int(text)

    def store_cyl_size(self, text):
        self.cylinder_size_val = int(text)

    def store_reserve(self, text):
        self.reserve_val = text

    def store_fill(self, state):
        if state == 2:
            self.refill = True
        else:
            self.refill = False

    def output_plan(self, out_name):
        md_dive_data = ('# Dive parameters\n'
                        '\n'
                        '|          | Depth  | Time  | Start pressure | End pressure | Gas Volume (l) |\n'
                        '|:---------|:------:|:-----:|:--------------:|:------------:|:--------------:|\n'
                        '| Dive 1   | {}     | {}    | -              | {}           | {}             |\n'
                        '| Interval | -      | {}    | {}             | {}           | -              |\n'
                        '| Dive 2   | {}     | {}    | {}             | {}           | {}             |\n\n'
                        '').format(self.dive_dict[1]['d'], self.dive_dict[1]['t'], self.d1_end_pressure,
                                   self.dive_1_total_v,
                                   self.surface_interval, self.d1_end_pressure, self.d2_start_pressure,
                                   self.dive_dict[2]['d'], self.dive_dict[2]['t'], self.d2_start_pressure,
                                   self.d2_end_pressure,
                                   self.dive_2_total_v)

        md_gas_data = ('# Gas parameters\n'
                       '\n'
                       '| Mix  | pO2  | SAC rate | MOD  |\n'
                       '|:-----|:----:|:--------:|:----:|\n'
                       '| {}   | {}   | {}       | {}   |\n\n'
                       '').format(self.g_mix_val, self.po2_value, self.sac_rate_val, self.mod_val)

        # save plot
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        plot_name = out_name + '.png'
        exporter.export(plot_name)

        plot_md = ('# Dive profile\n'
                   '\n'
                   '![profile]({})\n').format(plot_name)

        return ''.join([md_dive_data, md_gas_data, plot_md])


def create_profile(t1, d1, t2, d2, si):
    # DIVE ONE
    # calc ascent and descent times
    t_per_m_desc = 1.0 / 30.0  # 30m per min descent rate
    t_per_m_asc = 1.0 / 15.0  # 15m per min to 6m
    t_per_m_asc_6 = 1.0 / 6  # 6m per min above 6m
    safety2surf = 1
    stop_t = 3
    desc_1_time = t_per_m_desc * d1
    asc_1_time2safety = t_per_m_asc * (d1 - 6)
    d1_bt = t1  # t1 - desc_1_time - asc_1_time2safety - safety2surf - stop_t

    # DIVE TWO
    desc_2_time = t_per_m_desc * d2
    asc_2_time2safety = t_per_m_asc * (d2 - 6)
    d2_bt = t2  # t2 - desc_2_time - asc_2_time2safety - safety2surf

    # SURFACE INTERVAL
    interval = si

    # PROFILE
    x = [0, desc_1_time, d1_bt, asc_1_time2safety, stop_t, safety2surf]
    y = [0, -d1, -d1, -6, -6, 0]

    if not d2 == t2 == 0:
        x += [interval, desc_2_time, d2_bt, asc_2_time2safety, stop_t, safety2surf]
        y += [0, -d2, -d2, -6, -6, 0]

    x_cum = np.cumsum(x)

    return x_cum, y


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
