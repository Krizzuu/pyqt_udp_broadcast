import socket
import sys

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QMutex, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QLabel, QPushButton, QTextBrowser


class UDPReceiver(QObject):
    """
        class responsible for udp receiving process
    """
    new_data = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, ip, port, parent=None):
        super(UDPReceiver, self).__init__(parent)
        self._ip = ip
        self._port = port
        self._running = False
        self._mutex = QMutex()
        self._socket: socket.socket

    def start(self):
        print(f"Receiver opened {self._ip}:{self._port}")
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.bind((self._ip, self._port))
        self.process()

    def stop(self):
        self._mutex.lock()
        self._running = False
        self._mutex.unlock()
        # sending message to itself to unlock receiver from socket.recvfrom()
        self._socket.sendto("".encode(), (self._ip, self._port))

    def running(self):
        try:
            self._mutex.lock()
            return self._running
        finally:
            self._mutex.unlock()

    def process(self):
        while True:
            data, addr = self._socket.recvfrom(1024)
            if not self.running():
                break
            self.new_data.emit(data.decode())
        print("Socket closed")
        self.stopped.emit()



class UDPReceiverWindow(QMainWindow):
    """
        class responsible for displaying GUI of application
        and creating UDPReceiver for given IP and port
    """
    def __init__(self):
        # setting up gui and it's widgets
        super().__init__()

        self.setWindowTitle("BroadcastRx")
        self.move(600, 200)
        self.setFixedSize(250, 300)

        ip_label = QLabel(self)
        ip_label.setText("IP")
        ip_label.move(10, 10)
        self.ip_field = QLineEdit(self)
        self.ip_field.setGeometry(10, 40, 160, 30)

        port_label = QLabel(self)
        port_label.setText("Port")
        port_label.move(180, 10)
        self.port_field = QLineEdit(self)
        self.port_field.setGeometry(180, 40, 60, 30)

        self.start_button = QPushButton(self)
        self.start_button.move(10, 80)
        self.start_button.setText("Start receiving")
        self.start_button.clicked.connect(self.start)

        self.stop_button = QPushButton(self)
        self.stop_button.move(140, 80)
        self.stop_button.setText("Stop receiving")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)

        self.msg_box = QTextBrowser(self)
        self.msg_box.setGeometry(10, 120, 230, 160)

        self.error = QLabel(self)
        self.error.move(5, 275)
        self.error.setStyleSheet("color: red")

        # declaring a thread and receiver fields
        self._receiver = None
        self._thread = None

        # filling text fields with constant data
        from constants import RECEIVER_IP_ADDRESS, PORT
        self.ip_field.setText(RECEIVER_IP_ADDRESS)
        self.port_field.setText(str(PORT))
        # declaring ip and port
        self.ip = ""
        self.port = 0

    def start(self):
        try:
            self.ip = self.ip_field.text()
            self.port = int(self.port_field.text())
            # checking if ip and port make sense
            self._check_data()
        except ValueError:
            self.error.setText("Invalid IP or port")

        self.error.clear()
        self.start_button.setEnabled(False)
        self.ip_field.setEnabled(False)
        self.port_field.setEnabled(False)
        self.stop_button.setEnabled(True)

        # creating a thread and udp receiver
        if not self._thread:
            self._thread = QThread()

        self._receiver = UDPReceiver(self.ip, self.port)
        self._receiver.new_data.connect(self.add_msg)
        self._receiver.stopped.connect(self.on_receiver_stopped)

        self._receiver.moveToThread(self._thread)
        self._thread.started.connect(self._receiver.start)

        self._thread.start()

    def stop(self):
        self._receiver.stop()
        self.start_button.setEnabled(True)
        self.ip_field.setEnabled(True)
        self.port_field.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _check_data(self):
        b = self.ip.split(".")
        if len(b) != 4:
            raise ValueError
        for p in b:
            if int(p) < 0 or int(p) > 255:
                raise ValueError

    @pyqtSlot(str)
    def add_msg(self, text):
        self.msg_box.append(text)

    @pyqtSlot()
    def on_receiver_stopped(self):
        print("Receiver stopped")
        self._thread.quit()
        self._thread.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UDPReceiverWindow()
    window.show()

    app.exec()
    pass

