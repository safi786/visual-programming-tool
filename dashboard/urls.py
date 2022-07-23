from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard', views.index, name='dashboard'),

    path('project/<str:pk>/', views.project, name='project'),
    path('project-update/<str:pk>/', views.projectUpdate, name='projectUpdate'),

    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('public-projects/', views.PublicProjectListView.as_view(), name='public-projects'),
    path('public-projects/import/<int:id>/', views.ImportProject, name='import-project'),
    path('imported-projects/', views.ImportedProjectListView.as_view(), name='imported-projects'),
    path('projects/add/', views.ProjectCreate.as_view(), name='project-add'),

    # path('project/update/<int:pk>/', views.ProjectUpdate.as_view(), name='project-update'),
    path('project/update/<int:pk>/', views.addLibrary, name='project-update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('project/import/<int:pk>/delete/', views.ImportedProjectDeleteView.as_view(), name='imported-project-delete'),

    path('libraries/', views.LibraryListView.as_view(), name='libraries'),
    path('public-libraries/', views.PublicLibraryListView.as_view(), name='public-libraries'),
    path('public-libraries/import/<int:id>/', views.ImportProject, name='import-libraries'),
    path('imported-libraries/', views.ImportedLibraryListView.as_view(), name='imported-libraries'),
    path('libraries/add/', views.LibraryCreate.as_view(), name='library-add'),
    path('library/update/<int:pk>/', views.LibraryUpdateView.as_view(), name='library-update'),
    path('library/<int:pk>/delete/', views.LibraryDeleteView.as_view(), name='library-delete'),

    path('program/<int:pk>/delete/', views.ProgramDeleteView.as_view(), name='program-delete'),
    
    path('library/<str:pk>/', views.libraryView, name='library'),
    path('addLibrary', views.addLibrary, name='addLibrary'),
    path('libraryEdit/<str:pk>/', views.libraryEdit, name='libraryEdit'),
    path('run/<str:pk>/', views.run_code, name='run'),
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),
]
