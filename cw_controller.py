# cw_controller.py

class CW_Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.cell_clicked.connect(self.on_cell_clicked)

    def on_cell_clicked(self, r, c):
        self.model.toggle_cell(r, c)
        self.view.draw_grid()
