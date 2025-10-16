from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor
import sys

# -----------------------
# Model
# -----------------------
class RectModel:
    def __init__(self):
        # Each rect: (QRectF, selected)
        self.rects = [
            {"rect": QRectF(50, 50, 100, 60), "selected": False},
            {"rect": QRectF(200, 120, 120, 80), "selected": False},
            {"rect": QRectF(150, 250, 90, 90), "selected": False},
        ]

    def get_rects(self):
        return self.rects

    def select_rect_at(self, point: QPointF):
        """Return True if a rect was selected."""
        selected_any = False
        for r in self.rects:
            if r["rect"].contains(point):
                r["selected"] = True
                selected_any = True
            else:
                r["selected"] = False
        return selected_any


# -----------------------
# View
# -----------------------
class CanvasView(QWidget):
    clicked = pyqtSignal(QPointF)  # emitted when user clicks

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setMinimumSize(400, 400)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event.position())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for r in self.model.get_rects():
            rect = r["rect"]
            if r["selected"]:
                pen = QPen(QColor("red"), 4)  # thicker red border if selected
            else:
                pen = QPen(QColor("black"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)


# -----------------------
# Controller
# -----------------------
class CanvasController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        # connect signal from view to handler
        self.view.clicked.connect(self.handle_click)

    def handle_click(self, pos: QPointF):
        if self.model.select_rect_at(pos):
            print(f"Clicked on a rect at {pos}")
        else:
            print(f"No rect at {pos}")
        self.view.update()


# -----------------------
# App setup
# -----------------------
def main():
    app = QApplication(sys.argv)
    model = RectModel()
    view = CanvasView(model)
    controller = CanvasController(model, view)

    view.setWindowTitle("MVC Rectangle Click Example")
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
