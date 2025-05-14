def generate_mapping(start_x=0, start_y=0, step=1):
    letters = "ABCDEFGHJKLMNOPQRST"
    mapping = {}
    for row in range(19):
        for col in range(19):
            label = f"{letters[col]}{19 - row}"
            x = start_x + col * step
            y = start_y + row * step
            mapping[label] = (x, y)
    return mapping

mapping = {}  # placeholder

def board_to_robot_coords(position):
    return mapping.get(position, (0, 0))