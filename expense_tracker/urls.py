from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('users/', views.users, name='users'),
    path('groups/', views.groups, name='groups'),
    path('groups/<int:groupID>/users/', views.getUsersInGroup, name='get users in a group'),
    path('groups/users/', views.addUserToGroup, name='add users to group'),
    path('expenses/', views.expenses, name='expenses'),
    path('settlements/payAmount/', views.payAmount, name='pay amount'),
    path(r'settlements/<int:groupID>/<int:userID>', views.settlements, name='Get Settlemnents'),
]