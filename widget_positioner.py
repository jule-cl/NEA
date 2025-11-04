# widget_positioner.py

class Widget_Positioner:
    @staticmethod
    def center(widget, x, y):
        widget.move(x - widget.width() // 2, y - widget.height() // 2)
    
    @staticmethod
    def top_left(widget, x, y):
        widget.move(x, y)
    
    @staticmethod
    def top_right(widget, x, y):
        widget.move(x - widget.width(), y)
    
    @staticmethod
    def top_center(widget, x, y):
        widget.move(x - widget.width() // 2, y)
    
    @staticmethod
    def bottom_left(widget, x, y):
        widget.move(x, y - widget.height())
    
    @staticmethod
    def bottom_right(widget, x, y):
        widget.move(x - widget.width(), y - widget.height())
    
    @staticmethod
    def bottom_center(widget, x, y):
        widget.move(x - widget.width() // 2, y - widget.height())
    
    @staticmethod
    def middle_left(widget, x, y):
        widget.move(x, y - widget.height() // 2)
    
    @staticmethod
    def middle_right(widget, x, y):
        widget.move(x - widget.width(), y - widget.height() // 2)