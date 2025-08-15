# cw_info_area.py

class Info_Area:
    def __init__(self):
        self.__page = 1
        
    def change_page(self, new_page):
        if new_page not in [1, 2, 3, 4]: raise ValueError("new_page has to be 1, 2, 3, or 4")
        self.__page = new_page

    def get_page(self):
        return self.__page