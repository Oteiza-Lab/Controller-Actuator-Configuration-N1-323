import serial
import logging

BAUD_RATE = 9600  # Replace with the appropriate baud rate for your device

def test_serial_connection(port, baud_rate):
    try:
        with serial.Serial(port, baud_rate, timeout=2) as ser:
            logging.info(f"Opened port {port} successfully.")
            ser.write(b't 1\r')  # Example command
            response = ser.read_until(b'\r').decode().strip()
            logging.info(f"Response from {port}: {response}")
            return response
    except serial.SerialException as e:
        logging.error(f"Failed to open port {port}: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ports_to_test = ['COM1', 'COM3']
    for port in ports_to_test:
        response = test_serial_connection(port, BAUD_RATE)
        if response:
            print(f"Port {port} responded: {response}")
        else:
            print(f"Port {port} did not respond.")