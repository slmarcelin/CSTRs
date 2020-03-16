import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

print([port.device for port in ports])
