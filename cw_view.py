# cw_view.py

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPen

class CW_View(QGraphicsView):
    cell_clicked = pyqtSignal(int, int)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.cell_size = 40
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.draw_grid()

    def draw_grid(self):
        self.scene.clear()
        size = self.model.get_grid_size()
        grid = self.model.get_grid()
        for r in range(size):
            for c in range(size):
                x, y = c * self.cell_size, r * self.cell_size
                rect = QGraphicsRectItem(x, y, self.cell_size, self.cell_size)
                color = "black" if grid[r][c] == "#" else "white"
                rect.setBrush(QBrush(QColor(color)))
                rect.setPen(QPen(Qt.black))
                rect.setData(0, (r, c))
                self.scene.addItem(rect)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsRectItem):
            r, c = item.data(0)
            self.cell_clicked.emit(r, c)
