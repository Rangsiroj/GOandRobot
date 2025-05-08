from pymodbus.client.sync import ModbusTcpClient

# def move_robot(x, y):
#     client = ModbusTcpClient("10.159.241.192")
#     client.connect()
#     client.write_register(0, int(x))
#     client.write_register(1, int(y))
#     client.close()

def move_robot(x, y):
    print(f"[SIMULATION] หุ่นยนต์ควรไปที่: X={x}, Y={y}")
