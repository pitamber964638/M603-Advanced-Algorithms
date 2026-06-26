
import sys
sys.path.append(".")

from src.utils import load_constraints, validate_constraints
from src.greedy_solver import greedy_schedule, print_schedule
from src.graph_engine import graph_coloring_schedule, print_graph_summary, print_colored_schedule
from src.optimizer import dp_room_optimised_schedule, print_dp_schedule
from src.backtracker import backtracking_schedule, print_backtracking_schedule
from src.evaluator import evaluate_schedule, print_comparison_table


def main():
    data_path = "data/constraints.json"

    data = load_constraints(data_path)

    print("CAMPUS PUZZLE SCHEDULER")
    print("=" * 90)

    print("\nINPUT VALIDATION")
    print("-" * 90)
    validation_messages = validate_constraints(data)
    for message in validation_messages:
        print("-", message)

    print("\nDATASET SUMMARY")
    print("-" * 90)
    print("Classes:", len(data["classes"]))
    print("Rooms:", len(data["rooms"]))
    print("Student groups:", len(data["student_groups"]))
    print("Time slots:", len(data["time_slots"]))

    # Stage 1
    print("\n\nSTAGE 1: GREEDY BASELINE")
    print("=" * 90)
    greedy_result, greedy_unscheduled = greedy_schedule(data)
    print_schedule(greedy_result, greedy_unscheduled)

    # Stage 2
    print("\n\nSTAGE 2: CONFLICT GRAPH AND WELSH-POWELL COLORING")
    print("=" * 90)
    graph, coloring, graph_schedule, graph_unscheduled = graph_coloring_schedule(data)
    print_graph_summary(graph, coloring)
    print_colored_schedule(graph_schedule, graph_unscheduled)

    # Stage 3
    print("\n\nSTAGE 3: DYNAMIC PROGRAMMING ROOM OPTIMISATION")
    print("=" * 90)
    dp_schedule, dp_unscheduled = dp_room_optimised_schedule(data)
    print_dp_schedule(dp_schedule, dp_unscheduled)

    # Stage 4
    print("\n\nSTAGE 4: BACKTRACKING BEST-EFFORT STRATEGY")
    print("=" * 90)
    bt_schedule, bt_unscheduled, search_nodes = backtracking_schedule(data)
    print_backtracking_schedule(bt_schedule, bt_unscheduled, search_nodes)

    # Final comparison
    print("\n\nFINAL RESULTS")
    print("=" * 90)

    results = [
        evaluate_schedule("Greedy Baseline", greedy_result, greedy_unscheduled, data),
        evaluate_schedule("Graph Coloring", graph_schedule, graph_unscheduled, data),
        evaluate_schedule("Graph Coloring + DP", dp_schedule, dp_unscheduled, data),
        evaluate_schedule("Backtracking Best Effort", bt_schedule, bt_unscheduled, data)
    ]

    print_comparison_table(results)

    print("\nMANUAL FIX LOG")
    print("-" * 90)
    if len(bt_unscheduled) == 0:
        print("All classes were scheduled successfully. No manual fix is required.")
    else:
        print("The following classes require manual intervention:")
        for item in bt_unscheduled:
            print(f"- {item['class_id']}: {item['reason']}")


if __name__ == "__main__":
    main()
