from gnu_interface import GNUGo
from vision import VisionSystem
from middleware import generate_mapping, board_to_robot_coords, mapping
# from robot_controller import move_robot
import time

# ใช้ mapping แบบ dynamic (คุณสามารถแก้ค่าได้)
mapping = generate_mapping(start_x=90, start_y=85, step=24)

gnugo = GNUGo()
vision = VisionSystem()
vision.run()

try:
    while True:
        print("กำลังตรวจสอบกระดาน...")
        new_move = vision.detect_new_stone()
        if new_move:
            print(f"ตรวจพบหมากที่ตำแหน่ง: {new_move}")
            gnugo.play_move("black", new_move)
            ai_move = gnugo.genmove("white")
            print(f"AI เดินหมากที่: {ai_move}")
            # x, y = board_to_robot_coords(ai_move)
            # move_robot(x, y)
            print(f"📢 กรุณาวางหมากสีขาวที่ตำแหน่ง: {ai_move}")
        time.sleep(1)

except KeyboardInterrupt:
    gnugo.close()
    vision.release()
    print("ปิดโปรแกรมแล้ว")