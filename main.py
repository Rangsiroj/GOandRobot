from gnu_interface import GNUGo
from vision import VisionSystem
from middleware import generate_mapping, board_to_robot_coords, mapping
import time
import csv
import os
from datetime import datetime

# ใช้ mapping แบบ dynamic (ยังใช้ได้ในอนาคต ถ้าอยากพัฒนาเรื่องพิกัดเพิ่ม)
mapping = generate_mapping(start_x=90, start_y=85, step=24)

# เตรียมระบบบันทึก CSV แบบ 'w' (ลบของเก่า)
csv_filename = "go_moves.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "player", "move"])

# เรียกใช้งาน GNU Go และระบบกล้อง
gnugo = GNUGo()
vision = VisionSystem()
vision.run()

try:
    while True:
        print("กำลังตรวจสอบกระดาน...")
        frame, warped, new_move = vision.detect_new_stone()
        if new_move:
            print(f"ตรวจพบหมากที่ตำแหน่ง: {new_move}")

            # บันทึกข้อมูลฝั่ง A (มนุษย์)
            timestamp = datetime.now().isoformat()
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, "A", new_move])

            gnugo.play_move("black", new_move)

            # คำแนะนำของ AI สำหรับ B
            ai_move = gnugo.genmove("white")
            print(f"AI เดินหมากที่: {ai_move}")
            print(f"📢 กรุณาวางหมากสีขาวที่ตำแหน่ง: {ai_move}")

            # บันทึกข้อมูลฝั่ง B (AI)
            timestamp = datetime.now().isoformat()
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as file: # 'w' = ลบไฟล์เดิม แล้วเขียนใหม่ทุกครั้งที่รัน / 'a'= เพิ่มบรรทัดใหม่ต่อจากของเดิม (เก็บข้อมูลเดิมไว้)
                writer = csv.writer(file)
                writer.writerow([timestamp, "B", ai_move])

        time.sleep(1)

except KeyboardInterrupt:
    gnugo.close()
    vision.release()
    print("ปิดโปรแกรมแล้ว")