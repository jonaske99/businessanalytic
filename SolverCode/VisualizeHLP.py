import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from HLPMain import parse
from SolveHLP import HLPSolver


def draw_layout(data, xdata, ydata, lengths, widths, title="HFLP Layout"):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Raumgröße setzen
    ax.set_xlim(0, data.getRoomLength())
    ax.set_ylim(0, data.getRoomWidth())
    ax.set_aspect("equal")

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", alpha=0.4)

    # Jede Unit als Rechteck zeichnen
    for i, (xc, yc, l, w) in enumerate(zip(xdata, ydata, lengths, widths)):
        left = xc - l / 2
        bottom = yc - w / 2

        rect = Rectangle((left, bottom), l, w, fill=False, linewidth=2)
        ax.add_patch(rect)

        ax.text(
            xc,
            yc,
            str(i),
            ha="center",
            va="center",
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) != 2:
        print("Usage: python VisualizeHLP.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    data = parse(input_file)
    solver = HLPSolver(data)
    objval = solver.buildAndSolveModel(LP=False, strengthen=True, separate=False)

    if objval >= 0.0:
        xdata, ydata, lengths, widths, peris, areas = solver.getLayout()
        draw_layout(data, xdata, ydata, lengths, widths, title=input_file)
    else:
        print("Keine gültige Lösung gefunden.")


if __name__ == "__main__":
    main()