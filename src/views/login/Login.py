#================================================================================================================================================
#---------------------------------------------------------------------Import---------------------------------------------------------------------
#================================================================================================================================================


import flet as ft
import mysql.connector
import re
import hashlib


#================================================================================================================================================
#----------------------------------------------------------------------MySQL---------------------------------------------------------------------
#================================================================================================================================================


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="testdb"
)

mycursor = mydb.cursor()
sqlTable = "INSERT INTO login_details (First_Name, Last_Name, Class_Sec, Email, Password, DOC) VALUES (%s, %s, %s, %s,%s, %s)"
EmailVerification = "SELECT Password FROM login_details WHERE Email = (%s)"


#================================================================================================================================================
#----------------------------------------------------------------------Main----------------------------------------------------------------------
#================================================================================================================================================


def hash_password(password):
    encodedpassword = password.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(encodedpassword)
    hashed_password = sha256.hexdigest()
    return hashed_password


def Validate_LoginEmail(email):
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False  


class Login(ft.Column):
    Login_Email = ft.Ref[ft.TextField]()
    Login_Password = ft.Ref[ft.TextField]()
    

    def sign_in(self, e):
        page = self.page
        if Validate_LoginEmail(self.Login_Email.current.value):
            try:
                mycursor.execute(EmailVerification, [self.Login_Email.current.value.lower()])
                result = mycursor.fetchone()
                if result and result[0] == hash_password(self.Login_Password.current.value):
                    self.page.go('/LoginSuccess')
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ERROR, color=ft.colors.ON_ERROR),
                                ft.Text(
                                    "Invalid Email or Password",
                                    color=ft.colors.ON_ERROR,
                                ),
                            ]
                        ),
                        bgcolor=ft.colors.ERROR,
                        duration=2000
                    )
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    ft.Row(
                        controls=[
                            ft.Icon(name=ft.icons.ERROR, color=ft.colors.ON_ERROR),
                            ft.Text(
                                "Please enter a valid Email ID",
                                color=ft.colors.ON_ERROR,
                            ),
                        ]
                    ),
                    bgcolor=ft.colors.ERROR,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Row(
                    controls=[
                        ft.Icon(name=ft.icons.ERROR, color=ft.colors.ON_ERROR),
                        ft.Text(
                            "Check your Credentials..",
                            color=ft.colors.ON_ERROR,
                        ),
                    ]
                ),
                bgcolor=ft.colors.ERROR,
                duration=2000
            )
            page.snack_bar.open = True
            page.update()

  
    def __init__(self, page: ft.Page):
        super().__init__()
        page.title = 'Login'
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        page.window_resizable = True
        page.window_maximized = False
        page.update()
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.alignment.top_center
        self.spacing = 10
        self.controls = [
            ft.Container(
                content=ft.Text(
                    "Login",
                    weight=ft.FontWeight.W_900,
                    size=30,
                ),
                margin=ft.margin.only(bottom=20),
                alignment=ft.alignment.center
            ),
            ft.TextField(
                border_radius=ft.border_radius.all(16),
                hint_text="Email",
                width=250,
                filled=True,
                border_color='transparent',
                text_size=16,
                content_padding=ft.padding.all(10),
                ref=self.Login_Email
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
                ref=self.Login_Password
            ),
            ft.FilledButton(
                text="Sign in",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=16),
                ),
                width=250,
                height=50,
                on_click=self.sign_in
            )
            # ft.Container(
            #     content=ft.Row(
            #         controls=[
            #             ft.Text('New user?'),
            #             ft.TextButton('Sign up', on_click=lambda _: page.go("/Registration"))
            #         ],
            #         alignment=ft.MainAxisAlignment.START,
            #     ),
            #     margin=ft.margin.only(left=40, top=15)
            # )
        ]

