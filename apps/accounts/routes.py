from . import views

from aiohttp import web


routes = [

    web.view('/accounts', views.CreateUser),
    web.view('/accounts/login', views.LoginUser),
    web.view(r'/accounts/{id:\d+}', views.RetrieveUpdateDeleteUser),

]
