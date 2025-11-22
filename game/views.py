from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib import messages
from .models import Assignment, Vote, GameSettings
import json


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return redirect("login")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "¡Tu cuenta ha sido creada con éxito! Por favor, inicia sesión.",
            )
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "game/signup.html", {"form": form})


@login_required
def dashboard(request):
    settings_obj = GameSettings.objects.first()
    is_reveal_time = False
    if settings_obj and timezone.now() >= settings_obj.reveal_date:
        is_reveal_time = True

    has_assigned = Assignment.objects.filter(giver=request.user).exists()
    total_users = User.objects.exclude(id=request.user.id).count()
    my_votes_count = Vote.objects.filter(voter=request.user).count()

    context = {
        "is_reveal_time": is_reveal_time,
        "reveal_date": settings_obj.reveal_date if settings_obj else None,
        "has_assigned": has_assigned,
        "pending_votes": total_users - my_votes_count,
    }
    return render(request, "game/dashboard.html", context)


@login_required
def set_my_target(request):
    if request.method == "POST":
        target_id = request.POST.get("target_user")
        target_user = get_object_or_404(User, id=target_id)
        assignment, created = Assignment.objects.get_or_create(giver=request.user)
        assignment.set_receiver(target_user.username)
        messages.success(request, f"¡Listo! Le regalarás a {target_user.username}.")
        return redirect("dashboard")

    users = User.objects.exclude(id=request.user.id)
    return render(request, "game/set_target.html", {"users": users})


# --- NUEVA VISTA PARA ELIMINAR VOTO ---
@login_required
def delete_vote(request, vote_id):
    # 1. Obtener el voto asegurando que pertenece al usuario actual
    vote = get_object_or_404(Vote, id=vote_id, voter=request.user)

    # 2. Verificar FECHA LÍMITE
    settings_obj = GameSettings.objects.first()
    if settings_obj and timezone.now() >= settings_obj.reveal_date:
        messages.error(
            request, "🚫 ¡El tiempo ha terminado! Ya no puedes cambiar tus votos."
        )
        return redirect("voting_area")

    # 3. Verificar que NO sea el Auto-Voto (el voto sobre mi propio regalo)
    #    Si el usuario predijo que "él mismo" regala, es el voto fijo del sistema.
    if vote.get_guess() == request.user.username:
        messages.warning(
            request, "No puedes eliminar la asignación de tu propio Amigo Secreto."
        )
        return redirect("voting_area")

    # 4. Eliminar
    target_name = vote.target_giver.username
    vote.delete()
    messages.info(
        request,
        f"Has retirado tu predicción sobre {target_name}. ¡Vuelve a intentarlo!",
    )

    return redirect("voting_area")


@login_required
def voting_area(request):
    # 1. Validación: Obligar a asignar regalo antes de votar
    has_assigned = Assignment.objects.filter(giver=request.user).exists()
    if not has_assigned:
        messages.warning(
            request,
            "⚠️ ¡Alto ahí! Antes de hacer predicciones, debes definir a quién le regalas.",
        )
        return redirect("set_target")

    # 2. AUTO-VOTO
    try:
        my_assignment = Assignment.objects.get(giver=request.user)
        my_giftee_username = my_assignment.get_receiver()

        if my_giftee_username:
            my_giftee_user = User.objects.get(username=my_giftee_username)
            auto_vote, created = Vote.objects.get_or_create(
                voter=request.user, target_giver=my_giftee_user
            )
            if created or auto_vote.get_guess() != request.user.username:
                auto_vote.set_guess(request.user.username)

    except (Assignment.DoesNotExist, User.DoesNotExist):
        pass

    # 3. PROCESAR VOTO MANUAL (POST)
    if request.method == "POST":
        # Validar fecha antes de aceptar el voto POST también
        settings_obj = GameSettings.objects.first()
        if settings_obj and timezone.now() >= settings_obj.reveal_date:
            messages.error(request, "🚫 ¡Tiempo agotado! No se guardaron los cambios.")
            return redirect("voting_area")

        target_receiver_id = request.POST.get("target_giver_id")
        guessed_santa_id = request.POST.get("guessed_receiver_id")

        if target_receiver_id and guessed_santa_id:
            target = get_object_or_404(User, id=target_receiver_id)
            santa_guess = get_object_or_404(User, id=guessed_santa_id)

            vote, created = Vote.objects.get_or_create(
                voter=request.user, target_giver=target
            )
            vote.set_guess(santa_guess.username)

            messages.success(
                request,
                f"¡Anotado! Crees que {santa_guess.username} le regala a {target.username}.",
            )
        return redirect("voting_area")

    # 4. PREPARACIÓN DE DATOS
    my_votes = Vote.objects.filter(voter=request.user).select_related("target_giver")

    voted_target_ids = []
    used_santa_usernames = set()

    for vote in my_votes:
        voted_target_ids.append(vote.target_giver_id)
        guess = vote.get_guess()
        if guess:
            used_santa_usernames.add(guess)

    pending_targets = User.objects.all()
    pending_targets = pending_targets.exclude(id=request.user.id)
    pending_targets = pending_targets.exclude(id__in=voted_target_ids)

    possible_santas = User.objects.exclude(id=request.user.id)
    possible_santas = possible_santas.exclude(username__in=used_santa_usernames)

    # --- NUEVO: Determinar si se puede editar ---
    settings_obj = GameSettings.objects.first()
    can_edit = True
    if settings_obj and timezone.now() >= settings_obj.reveal_date:
        can_edit = False
    # ---------------------------------------------

    context = {
        "pending_targets": pending_targets,
        "all_users": possible_santas,
        "my_votes": my_votes,
        "can_edit": can_edit,  # Enviamos esto al template
    }

    return render(request, "game/voting_area.html", context)


@login_required
def results_dashboard(request):
    settings_obj = GameSettings.objects.first()
    if not settings_obj or timezone.now() < settings_obj.reveal_date:
        return render(request, "game/too_early.html")

    users = User.objects.all()
    scoreboard = []
    correct_guesses = 0
    total_votes = 0

    reality_map = {}
    assignments = Assignment.objects.all()
    for a in assignments:
        reality_map[a.giver.username] = a.get_receiver()

    inverse_reality_map = {v: k for k, v in reality_map.items() if v}

    for u in users:
        points = 0
        vote_details = []
        user_votes = Vote.objects.filter(voter=u)

        for v in user_votes:
            total_votes += 1
            target_receiver_username = v.target_giver.username
            guessed_santa_username = v.get_guess()

            real_santa = inverse_reality_map.get(target_receiver_username)

            is_correct = False
            if real_santa and real_santa == guessed_santa_username:
                points += 1
                correct_guesses += 1
                is_correct = True

            vote_details.append(
                {
                    "target": target_receiver_username,
                    "guessed": guessed_santa_username,
                    "is_correct": is_correct,
                }
            )

        scoreboard.append(
            {
                "username": u.username,
                "points": points,
                "vote_details": vote_details,
            }
        )

    scoreboard.sort(key=lambda x: x["points"], reverse=True)
    winner = scoreboard[0] if scoreboard else None

    official_assignments = [
        {"giver": a.giver.username, "receiver": a.get_receiver()} for a in assignments
    ]
    chart_labels = [x["username"] for x in scoreboard]
    chart_data = [x["points"] for x in scoreboard]

    context = {
        "winner": winner,
        "scoreboard": scoreboard,
        "official_assignments": official_assignments,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "accuracy": round((correct_guesses / total_votes) * 100, 2)
        if total_votes > 0
        else 0,
    }

    return render(request, "game/results.html", context)
