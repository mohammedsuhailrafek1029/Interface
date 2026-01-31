#================================================================================================================================================
#---------------------------------------------------------------------Import---------------------------------------------------------------------
#================================================================================================================================================


import flet as ft
from flet import dropdown
from flet_core.control_event import ControlEvent
import mysql.connector
import datetime
import mysql
import re
import hashlib

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
sqlTable = "INSERT INTO login_details (First_Name, Last_Name, Class_Sec, Email, Password, DOC) VALUES (%s, %s, %s, %s, %s, %s)"
EmailVerification = "SELECT Password FROM login_details WHERE Email = (%s)"


#================================================================================================================================================
#--------------------------------------------------------------Registeration---------------------------------------------------------------------
#================================================================================================================================================


def hash_password(password):
            encodedpassword = password.encode('utf-8')
            sha256 = hashlib.sha256()
            sha256.update(encodedpassword)
            hashed_password = sha256.hexdigest()
            return hashed_password


def Validate_RegEmail(email):
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False


class Registration(ft.Column):
    First_Name = ft.Ref[ft.TextField]()
    Last_Name = ft.Ref[ft.TextField]()
    Class_Sec = ft.Ref[ft.Dropdown]()
    Reg_Email = ft.Ref[ft.TextField]()
    Password = ft.Ref[ft.TextField]()
    Confirm_Password = ft.Ref[ft.TextField]()
    def __init__(self,page:ft.Page):
        def Reg_Submit(e:ControlEvent):
            self.page = page
            if all([self.Reg_Email.current.value, self.First_Name.current.value, self.Last_Name.current.value, self.Class_Sec.current.value,
                    self.Password.current.value,self.Password.current.value==self.Confirm_Password.current.value,
                    Validate_RegEmail(self.Reg_Email.current.value)==True]):
                try:
                    mycursor.execute(sqlTable, [self.First_Name.current.value, self.Last_Name.current.value, self.Class_Sec.current.value,
                                                self.Reg_Email.current.value.lower(), hash_password(self.Password.current.value), datetime.datetime.now()])
                    mydb.commit()
                    self.page.go('/Login')
                    page.update()
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ERROR, color=ft.colors.ON_ERROR),
                                ft.Text(
                                    "Check the Given Details...",
                                    color=ft.colors.ON_ERROR,
                                ),
                            ]
                        ),
                        bgcolor=ft.colors.ERROR,
                        duration=2000
                    )
                    page.snack_bar.open = True
                    page.update()
        super().__init__(self)
        self.page = page
        page.title = 'Registration'
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        page.window_resizable = True
        page.window_maximized = False
        page.update()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment=ft.alignment.center
        self.spacing = 10
        self.controls = [
            ft.Container(
                content=ft.Text("Registration",
                    weight=ft.FontWeight.W_900,
                    size=30,
                    color=ft.colors.SURFACE_TINT
                ),
                margin=ft.margin.only(bottom=20),
                alignment=ft.alignment.center
            ),
            ft.TextField(
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="First Name",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref=self.First_Name
            ),
            ft.TextField(
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="Last Name",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref=self.Last_Name
            ), 
            ft.Dropdown(      
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="Class & Sec",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                options=[dropdown.Option('I'),
                    dropdown.Option('II'),
                    dropdown.Option('III'),
                    dropdown.Option('IV'),
                    dropdown.Option('V'),
                    dropdown.Option('VI'),
                    dropdown.Option('VII'),
                    dropdown.Option('VIII'),
                    dropdown.Option('IX'),
                    dropdown.Option('X'),
                    dropdown.Option('XI'),
                    dropdown.Option('XII'),
                ],
                ref=self.Class_Sec
            ), 
            ft.TextField(
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="Email",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref=self.Reg_Email
            ),                        
            ft.TextField(
                password=True,
                can_reveal_password=True,
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="Password",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref = self.Password
            ),  
            ft.TextField(
                password=True,
                can_reveal_password=True,
                border_radius=ft.border_radius.all(16),
                height=60,
                hint_text="Confirm Password",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref=self.Confirm_Password
            ),
            ft.FilledButton(
                text="Sign Up",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=Reg_Submit
            ),
            ft.Row(
            )
            
        ]
        self.Reg_Email.on_change = Validate_RegEmail
    

        