from . import views

from aiohttp import web


routes = [

    web.view('/accounts', views.CreateUser),
    web.view(r'/accounts/{pk:\d+}', views.RetrieveUpdateDeleteUser),

]
