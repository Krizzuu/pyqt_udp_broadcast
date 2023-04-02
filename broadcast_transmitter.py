import socket
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QLabel, QPushButton


class BroadcastTransmitter(QMainWindow):
    def __init__(self):
        # setting up gui and it's widgets
        super().__init__()

        self.setWindowTitle("BroadcastTx")
        self.move(200, 200)
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
        self.start_button.setText("Start messaging")
        self.start_button.clicked.connect(self.start)

        self.stop_button = QPushButton(self)
        self.stop_button.move(140, 80)
        self.stop_button.setText("Stop messaging")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)

        msg_label = QLabel(self)
        msg_label.move(10, 110)
        msg_label.setText("Your message")
        self.msg_field = QLineEdit(self)
        self.msg_field.setGeometry(10, 140, 230, 30)
        self.msg_field.setEnabled(False)

        self.send_button = QPushButton(self)
        self.send_button.setGeometry(60, 180, 120, 30)
        self.send_button.setText("Send")
        self.send_button.clicked.connect(self.send)

        self.error = QLabel(self)
        self.error.move(5, 275)
        self.error.setStyleSheet("color: red")

        # creating socket to broadcast messages
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        from constants import BROADCAST_IP_ADDRESS, PORT
        self.ip_field.setText(BROADCAST_IP_ADDRESS)
        self.port_field.setText(str(PORT))
        self.broadcast_ip = ""
        self.port = 0

    def start(self):
        try:
            self.broadcast_ip = self.ip_field.text()
            self.port = int(self.port_field.text())
            # checking if ip and port make sense
            self._check_data()
        except ValueError:
            self.error.setText("Invalid IP or port")

        self.error.clear()
        self.start_button.setEnabled(False)
        self.ip_field.setEnabled(False)
        self.port_field.setEnabled(False)
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.msg_field.setEnabled(True)

    def stop(self):
        self.start_button.setEnabled(True)
        self.ip_field.setEnabled(True)
        self.port_field.setEnabled(True)
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.msg_field.setEnabled(False)

    def send(self):
        msg = self.msg_field.text()
        self.socket.sendto(msg.encode(), (self.broadcast_ip, self.port))

    '''
        simple check if ip field has string that consists of 4 numbers in range [0, 255] separated by dot
    '''
    def _check_data(self):
        b = self.broadcast_ip.split(".")
        if len(b) != 4:
            raise ValueError
        for p in b:
            if int(p) < 0 or int(p) > 255:
                raise ValueError


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BroadcastTransmitter()
    window.show()

    app.exec()
    pass

