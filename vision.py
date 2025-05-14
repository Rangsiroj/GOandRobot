import cv2
import numpy as np
import cv2.aruco as aruco

class VisionSystem:
    def __init__(self, url='http://10.153.244.243:4747/video'):
        self.cap = cv2.VideoCapture(url)
        self.prev_frame = None
        self.last_warped = None
        self.board_size = (500, 500)
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters()
        self.mapping = {}  # ✅ จะอัปเดตภายหลัง

        if not self.cap.isOpened():
            print("❌ ไม่สามารถเปิดกล้องได้")
        else:
            print("✅ กล้องเปิดสำเร็จ")

    def detect_aruco_corners(self, gray, frame):
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)

        if ids is None or len(ids) < 4:
            return None

        id_to_point = {int(id[0]): np.mean(corner[0], axis=0) for id, corner in zip(ids, corners)}
        required_ids = [0, 1, 2, 3]
        if not all(i in id_to_point for i in required_ids):
            return None

        src_pts = np.float32([
            id_to_point[0],
            id_to_point[1],
            id_to_point[2],
            id_to_point[3],
        ])

        padding = 40
        center = np.mean(src_pts, axis=0)

        def expand(pt):
            direction = pt - center
            norm = np.linalg.norm(direction)
            if norm == 0:
                return pt
            return pt + padding * direction / norm

        expanded_pts = np.float32([expand(pt) for pt in src_pts])
        return expanded_pts

    def pixel_to_board_position(self, x, y):
        col = int(x / (self.board_size[0] / 19))
        row = int(y / (self.board_size[1] / 19))

        letters = "ABCDEFGHJKLMNOPQRST"  # ไม่มี I
        col = max(0, min(col, 18))
        row = max(0, min(row, 18))

        position = f"{letters[col]}{19 - row}"
        return position

    def detect_new_stone(self):
        ret, frame = self.cap.read()
        if not ret:
            print("❌ ไม่สามารถดึงภาพจากกล้องได้")
            return None, self.last_warped, None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_corners = self.detect_aruco_corners(gray, frame)

        if aruco_corners is None:
            return frame, self.last_warped, None

        # Perspective warp
        dst_pts = np.float32([
            [0, 0],
            [self.board_size[0], 0],
            [self.board_size[0], self.board_size[1]],
            [0, self.board_size[1]]
        ])
        matrix = cv2.getPerspectiveTransform(aruco_corners, dst_pts)
        warped = cv2.warpPerspective(frame, matrix, self.board_size)
        self.last_warped = warped

        # ✅ สร้าง mapping grid แล้ว warp ไปตาม matrix
        letters = "ABCDEFGHJKLMNOPQRST"
        raw_grid = []
        label_list = []
        step = self.board_size[0] / 18
        for row in range(19):
            for col in range(19):
                x = col * step
                y = row * step
                raw_grid.append([[x, y]])
                label_list.append(f"{letters[col]}{19 - row}")

        raw_grid = np.array(raw_grid, dtype=np.float32)
        warped_points = cv2.perspectiveTransform(raw_grid, matrix)

        self.mapping = {
            label: tuple(pt[0]) for label, pt in zip(label_list, warped_points)
        }

        # ตรวจหาเม็ดหมาก
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_warped, (5, 5), 0)
        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
            param1=50, param2=30, minRadius=10, maxRadius=30
        )

        move_detected = None
        if self.prev_frame is not None:
            diff = cv2.absdiff(self.prev_frame, gray_warped)
            changed = np.sum(diff > 50)

            if changed > 5000 and circles is not None:
                print("✅ ตรวจพบหมากใหม่")
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    cx, cy = i[0], i[1]
                    move_detected = self.pixel_to_board_position(cx, cy)
                    break

        self.prev_frame = gray_warped
        return frame, warped, move_detected

    def draw_mapping_grid(self, image):
        for label, (x, y) in self.mapping.items():
            cv2.circle(image, (int(x), int(y)), 2, (0, 255, 0), -1)
            cv2.putText(image, label, (int(x)+2, int(y)-2), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 255, 0), 1)

    def run(self):
        print("🔁 เริ่มระบบกล้อง กด ESC เพื่อออก")
        while True:
            frame, warped, move = self.detect_new_stone()

            if frame is not None:
                cv2.imshow("กล้องสด", frame)
            if warped is not None:
                if self.mapping:
                    self.draw_mapping_grid(warped)
                cv2.imshow("กระดานตรง", warped)
            else:
                blank = np.zeros((self.board_size[1], self.board_size[0], 3), dtype=np.uint8)
                cv2.imshow("กระดานตรง", blank)

            if move:
                print(f"เจอหมากที่: {move}")

            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.release()

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()