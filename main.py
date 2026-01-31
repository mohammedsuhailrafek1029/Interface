
#================================================================================================================================================
#---------------------------------------------------------------------Import---------------------------------------------------------------------
#================================================================================================================================================


import flet as ft
import mysql.connector
import mysql
from src.widgets.theme import IconThemeSelector
from src.views.login.Login import Login
from src.views.login.Login_Success import LoginSuccess 
from src.views.login.Registration import Registration
from src.views.login.Edit import Edit
from src.views.login.Remove import Edit as RemovePage


#================================================================================================================================================
#----------------------------------------------------------------------MySQL---------------------------------------------------------------------
#================================================================================================================================================


mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd="123456",
    database = "testdb"
)

mycursor = mydb.cursor()
sqlTable = "INSERT INTO login_details (First_Name, Last_Name, Class_Sec, Email, Password, DOC) VALUES (%s, %s, %s, %s,%s, %s)"
EmailVerification = "SELECT Password FROM login_details WHERE Email = (%s)"


#================================================================================================================================================
#----------------------------------------------------------------------Main----------------------------------------------------------------------
#================================================================================================================================================



def main(page: ft.Page):
    page.title = 'Face Recognition'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.window_resizable = True
    page.window_maximized = True
    page.theme = ft.Theme(color_scheme_seed="#9AACFF",
                          font_family='Candara bold',
                        )
    page.dark_theme = ft.Theme(color_scheme_seed="#9AACFF")


    def route_change(route):
        page.views.append(
            views_handlers(page)[page.route]
        )
        page.update()

    def views_handlers(page):
        return {
            '/Login':ft.View(
                route='/Login',
                controls=[ft.Row(
                            controls=[IconThemeSelector(page=page)],
                            alignment=ft.MainAxisAlignment.START,
                            width=400
                         ),
                Login(page=page)
                ]
            ),
            '/Registration':ft.View(
                route='/Registration',
                controls=[ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=view_pop),
                                IconThemeSelector(page=page)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            width=400
                         ),
                Registration(page=page)
                ]  
            ),
            '/LoginSuccess':ft.View(
                route='/LoginSuccess',
                controls=[ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=view_pop),
                                IconThemeSelector(page=page)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            width=400
                         ),
                LoginSuccess(page=page)
                ]  
            ),
            '/Edit':ft.View(
                route='/Edit',
                controls=[ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=view_pop),
                                IconThemeSelector(page=page)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            width=400
                         ),
                Edit(page=page)
                ]  
            ),
            '/Remove':ft.View(
                route='/Remove',
                controls=[ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=view_pop),
                                IconThemeSelector(page=page)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            width=400
                         ),
                RemovePage(page=page)
                ]  
            )
        }

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.go('/Login')
    page.on_view_pop = view_pop
    page.drawer = ft.NavigationDrawer()
    

ft.app(target=main,assets_dir="./assets")