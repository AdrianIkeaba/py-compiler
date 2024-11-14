def main() -> float:
    total_distance: float = 1.5

    total_students: float = 90.0

    step_length: float = 0.78

    distance_meters: float = total_distance * 1000.0

    total_steps: float = distance_meters / step_length

    avg_steps_per_student: float = total_steps / total_students

    return avg_steps_per_student
