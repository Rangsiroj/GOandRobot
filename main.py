from gnu_interface import GNUGo
from vision import VisionSystem
from middleware import board_to_robot_coords
from robot_controller import move_robot
import time

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
            x, y = board_to_robot_coords(ai_move)
            move_robot(x, y)
        time.sleep(1)
except KeyboardInterrupt:
    gnugo.close()
    vision.release()
    print("ปิดโปรแกรมแล้ว")
    #test
