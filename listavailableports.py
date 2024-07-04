import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

available_ports = list_serial_ports()
print("Available serial ports:", available_ports)