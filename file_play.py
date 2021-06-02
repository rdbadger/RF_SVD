#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Play sigMF recordings
# Author: David Badger
# Description: sigMF sample collection
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
import sip
from gnuradio import fosphor
from gnuradio.fft import window
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget

from gnuradio import qtgui

class file_play(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Play sigMF recordings")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Play sigMF recordings")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "file_play")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.gain = gain = 0
        self.freq = freq = 433.7e6
        self.antenna = antenna = "TX/RX"

        ##################################################
        # Blocks
        ##################################################
        self._gain_range = Range(0, 60, 1, 0, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, 'Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._gain_win)
        self._freq_range = Range(400e6, 6e9, 100e3, 433.7e6, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, 'Freq', "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_win)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_gain(gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_bandwidth(samp_rate, 0)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec())
        self.fosphor_qt_sink_c_0_0 = fosphor.qt_sink_c()
        self.fosphor_qt_sink_c_0_0.set_fft_window(window.WIN_BLACKMAN_hARRIS)
        self.fosphor_qt_sink_c_0_0.set_frequency_range(freq, samp_rate)
        self._fosphor_qt_sink_c_0_0_win = sip.wrapinstance(self.fosphor_qt_sink_c_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._fosphor_qt_sink_c_0_0_win)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_file_source_1 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/david/sigMF_ML/RF_SVD/ptt_2_10_svd_1024_fft/ptt_svd5_1024_fft', True, 0, 0)
        self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)
        # Create the options list
        self._antenna_options = ("TX/RX", "RX2", )
        # Create the labels list
        self._antenna_labels = ("TX/RX", "RX2", )
        # Create the combo box
        self._antenna_tool_bar = Qt.QToolBar(self)
        self._antenna_tool_bar.addWidget(Qt.QLabel('Antenna' + ": "))
        self._antenna_combo_box = Qt.QComboBox()
        self._antenna_tool_bar.addWidget(self._antenna_combo_box)
        for _label in self._antenna_labels: self._antenna_combo_box.addItem(_label)
        self._antenna_callback = lambda i: Qt.QMetaObject.invokeMethod(self._antenna_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._antenna_options.index(i)))
        self._antenna_callback(self.antenna)
        self._antenna_combo_box.currentIndexChanged.connect(
            lambda i: self.set_antenna(self._antenna_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._antenna_tool_bar)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_1, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_file_source_1, 0), (self.fosphor_qt_sink_c_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.uhd_usrp_sink_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "file_play")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.fosphor_qt_sink_c_0_0.set_frequency_range(self.freq, self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0.set_bandwidth(self.samp_rate, 0)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.fosphor_qt_sink_c_0_0.set_frequency_range(self.freq, self.samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(self.freq, 0)

    def get_antenna(self):
        return self.antenna

    def set_antenna(self, antenna):
        self.antenna = antenna
        self._antenna_callback(self.antenna)





def main(top_block_cls=file_play, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
