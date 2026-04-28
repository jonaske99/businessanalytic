import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from HLPMain import parse
from SolveHLP import HLPSolver


def draw_layout(data, xdata, ydata, lengths, widths, title="HFLP Layout"):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Farben für die Units
    colors = [
        "#A8DADC", "#F4A261", "#E9C46A", "#2A9D8F",
        "#E76F51", "#BDE0FE", "#CDB4DB", "#90BE6D",
        "#FFAFCC", "#FFD6A5", "#B5E48C", "#8ECAE6"
    ]

    # Raumgröße setzen
    ax.set_xlim(0, data.getRoomLength())
    ax.set_ylim(0, data.getRoomWidth())
    ax.set_aspect("equal")

    # Titel und Achsen
    ax.set_title(f"Layout-Visualisierung: {title}", fontsize=14, fontweight="bold")
    ax.set_xlabel("X", fontsize=12)
    ax.set_ylabel("Y", fontsize=12)
    ax.set_facecolor("#f8f9fa")
    ax.grid(True, linestyle="--", alpha=0.35)

    # Jede Unit als Rechteck zeichnen
    for i, (xc, yc, l, w) in enumerate(zip(xdata, ydata, lengths, widths)):
        left = xc - l / 2
        bottom = yc - w / 2

        rect = Rectangle(
            (left, bottom),
            l,
            w,
            facecolor=colors[i % len(colors)],
            edgecolor="black",
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(rect)

        # Unit-Nummer in die Mitte
        ax.text(
            xc,
            yc,
            f"{i + 1}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="black",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2")
        )

        # Maße unter die Nummer schreiben
        ax.text(
            xc,
            yc - 0.6,
            f"{l:.1f} x {w:.1f}",
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

    # Bild speichern
    safe_name = title.replace("\\", "_").replace("/", "_").replace(":", "_")
    plt.tight_layout()
    plt.savefig(f"{safe_name}.png", dpi=200, bbox_inches="tight")
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