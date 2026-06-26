
from src.greedy_solver import build_class_group_map, calculate_total_waste


def build_conflict_graph(data):
    """
    Builds a conflict graph.

    Each class is a node.
    An edge exists between two classes if:
    1. They have the same professor, or
    2. They share at least one student group.
    """
    classes = data["classes"]
    student_groups = data["student_groups"]
    class_to_groups = build_class_group_map(student_groups)

    graph = {class_info["id"]: set() for class_info in classes}

    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            class_a = classes[i]
            class_b = classes[j]

            class_a_id = class_a["id"]
            class_b_id = class_b["id"]

            same_professor = class_a["professor"] == class_b["professor"]

            groups_a = set(class_to_groups.get(class_a_id, []))
            groups_b = set(class_to_groups.get(class_b_id, []))
            shared_group = len(groups_a.intersection(groups_b)) > 0

            if same_professor or shared_group:
                graph[class_a_id].add(class_b_id)
                graph[class_b_id].add(class_a_id)

    return graph


def welsh_powell_coloring(graph):
    """
    Applies Welsh-Powell graph coloring.

    Steps:
    1. Sort nodes by degree in descending order.
    2. Assign the lowest possible color to each node.
    3. Connected nodes cannot have the same color.

    In this project, each color represents a time slot.
    """
    sorted_nodes = sorted(graph.keys(), key=lambda node: len(graph[node]), reverse=True)
    coloring = {}

    for node in sorted_nodes:
        used_neighbor_colors = set()

        for neighbor in graph[node]:
            if neighbor in coloring:
                used_neighbor_colors.add(coloring[neighbor])

        color = 0
        while color in used_neighbor_colors:
            color += 1

        coloring[node] = color

    return coloring


def assign_time_slots_from_coloring(data, coloring):
    """
    Converts graph colors into actual time slots.
    If there are more colors than available time slots, some classes are unscheduled.
    """
    time_slots = data["time_slots"]
    class_lookup = {c["id"]: c for c in data["classes"]}

    time_assignment = {}
    unscheduled = []

    for class_id, color in coloring.items():
        if color < len(time_slots):
            time_assignment[class_id] = time_slots[color]
        else:
            class_info = class_lookup[class_id]
            unscheduled.append({
                "class_id": class_id,
                "students": class_info["students"],
                "professor": class_info["professor"],
                "reason": "Not enough available time slots for graph coloring"
            })

    return time_assignment, unscheduled


def assign_rooms_after_coloring(data, time_assignment):
    """
    Assigns rooms after graph coloring has fixed the time slots.

    This is still a simple room assignment method.
    The DP optimisation will be implemented in the next stage.
    """
    class_lookup = {c["id"]: c for c in data["classes"]}
    rooms = sorted(data["rooms"], key=lambda room: room["capacity"])

    schedule = []
    unscheduled = []

    # Sort larger classes first because they are harder to fit
    class_ids = sorted(
        time_assignment.keys(),
        key=lambda cid: class_lookup[cid]["students"],
        reverse=True
    )

    for class_id in class_ids:
        class_info = class_lookup[class_id]
        time_slot = time_assignment[class_id]
        placed = False

        for room in rooms:
            if room["capacity"] < class_info["students"]:
                continue

            room_already_used = any(
                item["time_slot"] == time_slot and item["room_id"] == room["id"]
                for item in schedule
            )

            if room_already_used:
                continue

            wasted_seats = room["capacity"] - class_info["students"]

            schedule.append({
                "class_id": class_info["id"],
                "professor": class_info["professor"],
                "students": class_info["students"],
                "time_slot": time_slot,
                "room_id": room["id"],
                "room_capacity": room["capacity"],
                "wasted_seats": wasted_seats,
                "method": "Graph Coloring"
            })

            placed = True
            break

        if not placed:
            unscheduled.append({
                "class_id": class_info["id"],
                "students": class_info["students"],
                "professor": class_info["professor"],
                "reason": "No feasible room available after graph coloring"
            })

    return schedule, unscheduled


def graph_coloring_schedule(data):
    """
    Complete Stage 2 process:
    1. Build conflict graph.
    2. Apply Welsh-Powell coloring.
    3. Convert colors into time slots.
    4. Assign rooms using a simple feasibility method.
    """
    graph = build_conflict_graph(data)
    coloring = welsh_powell_coloring(graph)
    time_assignment, time_unscheduled = assign_time_slots_from_coloring(data, coloring)
    schedule, room_unscheduled = assign_rooms_after_coloring(data, time_assignment)

    unscheduled = time_unscheduled + room_unscheduled

    return graph, coloring, schedule, unscheduled


def count_edges(graph):
    """
    Counts undirected graph edges.
    """
    return sum(len(neighbors) for neighbors in graph.values()) // 2


def print_graph_summary(graph, coloring):
    """
    Prints conflict graph details.
    """
    print("CONFLICT GRAPH SUMMARY")
    print("-" * 70)
    print("Number of class nodes:", len(graph))
    print("Number of conflict edges:", count_edges(graph))
    print("Number of colors/time-slot groups used:", len(set(coloring.values())))

    print("\nNode degrees:")
    for node, neighbors in sorted(graph.items()):
        print(f"{node}: degree {len(neighbors)} -> conflicts with {sorted(list(neighbors))}")

    print("\nColor assignment:")
    for class_id, color in sorted(coloring.items(), key=lambda x: x[1]):
        print(f"{class_id}: Color {color}")
    print("-" * 70)


def print_colored_schedule(schedule, unscheduled):
    """
    Prints the graph coloring schedule.
    """
    print("\nGRAPH COLORING OUTPUT")
    print("-" * 70)

    for item in sorted(schedule, key=lambda x: (x["time_slot"], x["room_id"])):
        if item["wasted_seats"] == 0:
            fit_status = "Perfect Fit"
        else:
            fit_status = f"Wasted {item['wasted_seats']} seats"

        print(
            f"Scheduled {item['class_id']} | "
            f"{item['time_slot']} | "
            f"{item['room_id']} | "
            f"{fit_status}"
        )

    for item in unscheduled:
        print(
            f"Unscheduled {item['class_id']} | "
            f"N/A | N/A | "
            f"Reason: {item['reason']}"
        )

    print("-" * 70)
    print("Scheduled classes:", len(schedule))
    print("Unscheduled classes:", len(unscheduled))
    print("Total wasted seats:", calculate_total_waste(schedule))
