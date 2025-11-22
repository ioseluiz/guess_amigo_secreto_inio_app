from django.urls import path
from django.contrib.auth import views as auth_views  # <--- Importante
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Ruta raíz redirige según esté logueado o no
    # --- Autenticación ---
    # Usamos auth_views.LoginView directamente, indicándole tu template
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="game/login.html"),
        name="login",
    ),
    # Para logout también usamos la vista genérica (redirige a login por defecto o lo que digas en settings)
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    # --- Vistas de la App ---
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "set-target/", views.set_my_target, name="set_target"
    ),  # Ojo con el nombre de la vista en views.py
    path("vote/", views.voting_area, name="voting_area"),
    path("vote/delete/<int:vote_id>/", views.delete_vote, name="delete_vote"),
    path("results/", views.results_dashboard, name="results"),
]
