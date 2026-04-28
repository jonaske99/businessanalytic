import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
# parse liest die HFLP-Instanzdatei ein und speichert die Daten in einem LayoutData-Objekt.
# und liefert anschließend die berechnete Platzierung der Units.
from HLPMain import parse
from SolveHLP import HLPSolver


def draw_layout(data, xdata, ydata, lengths, widths, title="HFLP Layout"):
    """
    Visualisiert die vom Solver berechnete HFLP-Lösung.

    Jede Organisationseinheit wird als Rechteck dargestellt.
    Die Solver-Ausgabe besteht aus Mittelpunktkoordinaten (xdata, ydata)
    sowie Länge und Breite der jeweiligen Unit.
    """
    #Das erstellt die Fläche, auf der das Layout gezeichnet wird
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

    # Titel und Achsenbeschriftung der Visualisierung
    ax.set_title(f"Layout-Visualisierung: {title}", fontsize=14, fontweight="bold")
    ax.set_xlabel("X", fontsize=12)
    ax.set_ylabel("Y", fontsize=12)
    # Heller Hintergrund und Raster zur besseren Lesbarkeit der Positionen.
    ax.set_facecolor("#f8f9fa")
    ax.grid(True, linestyle="--", alpha=0.35)


    # Jede Unit als Rechteck zeichnen
    # Im HFLP-Modell besitzt jede Unit einen Mittelpunkt (xc, yc),
    # eine Länge l und eine Breite w.
    for i, (xc, yc, l, w) in enumerate(zip(xdata, ydata, lengths, widths)):
        # Der Solver liefert aber den Mittelpunkt.
        # Matplotlib benötigt die linke untere Ecke des Rechtecks.
        left = xc - l / 2
        bottom = yc - w / 2

        # Dieses Rechteck entspricht einer platzierten Krankenhaus-Einheit im Layout.
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

        # Mittelpunkt der Unit markieren, da der Solver die Position über xc und yc beschreibt.
        ax.plot(xc, yc, marker="o", markersize=3, color="black")

        # Unit-Nummer in die Mitte anzeigen
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

        # Länge und Breite der Unit sowie die daraus berechnete Fläche anzeigen.
        # Die Fläche ergibt sich aus Länge * Breite und kann mit den Flächenvorgaben der Instanz verglichen werden.
        ax.text(
            xc,
            yc - 0.6,
            f"{l:.1f} x {w:.1f}\nA={l*w:.1f}",
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

    # Bild speichern als png
    safe_name = title.replace("\\", "_").replace("/", "_").replace(":", "_")
    plt.tight_layout()
    plt.savefig(f"{safe_name}.png", dpi=200, bbox_inches="tight")
    #Visualisierung anzeigen
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