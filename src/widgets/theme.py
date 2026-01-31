#================================================================================================================================================
#---------------------------------------------------------------------Import---------------------------------------------------------------------
#================================================================================================================================================


import flet as ft



#================================================================================================================================================
#----------------------------------------------------------------------Main----------------------------------------------------------------------
#================================================================================================================================================



class ThemeSelector(ft.SegmentedButton):
    def __init__(self,page:ft.Page,scale = 0.8):
        super().__init__(
            segments= [
                ft.Segment(
                value= "dark",
                icon= ft.Icon(ft.icons.DARK_MODE)
                        ),
            ft.Segment(
                value= "light",
                icon= ft.Icon(ft.icons.LIGHT_MODE),
                
                        )
                            ]
                                )
        self.page = page
        self.allow_empty_selection = False
        self.allow_multiple_selection = False
        self.selected = {page.theme_mode}
        self.on_change = self.onChange
        self.scale = scale
 
        
    def onChange(self,e):
        self.page.theme_mode = e.data[2:-2]
        self.page.update()


class IconThemeSelector(ft.IconButton):
    def __init__(self,page:ft.Page,style:ft.ButtonStyle=None):
        super().__init__(
            )
        self.page = page
        self.theme = page.theme_mode
        if self.theme == 'dark':
            self.icon = ft.icons.LIGHT_MODE
            self.update()
        else:
            self.icon = ft.icons.DARK_MODE
            self.update()
        self.on_click = self.onChange
        if style is not None:
            self.style = style

        
    def onChange(self,e):
        self.page.theme_mode = 'light' if self.page.theme_mode == "dark" else 'dark'
        if self.page.theme_mode == 'dark':
            self.icon = ft.icons.LIGHT_MODE
            self.update()
        else:
            self.icon = ft.icons.DARK_MODE
            self.update()
        self.page.update()