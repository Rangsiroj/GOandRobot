import subprocess

class GNUGo:
    def __init__(self, gnugo_path='gnugo.exe'):
        self.process = subprocess.Popen(
            [gnugo_path, '--mode', 'gtp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def send_command(self, command):
        try:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()
            response_lines = []
            while True:
                line = self.process.stdout.readline()
                if not line or line.strip() == '':
                    break
                response_lines.append(line.strip())
            response = '\n'.join(response_lines)
            if response.startswith('?'):
                print(f"[ERROR] GTP command failed: {command}")
            return response.replace('=', '').strip()
        except Exception as e:
            return f"[EXCEPTION] {e}"

    def play_move(self, color, position):
        return self.send_command(f"play {color} {position}")

    def genmove(self, color):
        return self.send_command(f"genmove {color}")

    def show_board(self):
        return self.send_command("showboard")

    def clear_board(self):
        return self.send_command("clear_board")

    def close(self):
        self.process.terminate()


# สำหรับทดสอบแยก
def test_gnugo():
    ai = GNUGo()
    print(ai.play_move("black", "D4"))
    print(ai.genmove("white"))
    print(ai.show_board())
    ai.clear_board()
    ai.close()

if __name__ == "__main__":
    test_gnugo()