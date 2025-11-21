from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import Assignment, Vote, GameSettings
import json


def home(request):
    """
    Vista para la ruta raíz '/'.
    Redirige al Dashboard si está logueado, o al Login si no lo está.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Guardamos el usuario, pero NO lo logueamos automáticamente
            
            # 1. Mensaje de éxito para que aparezca en la pantalla de Login
            messages.success(request, '¡Tu cuenta ha sido creada con éxito! Por favor, inicia sesión.')
            
            # 2. Redirección al Login en lugar del Dashboard
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'game/signup.html', {'form': form})

@login_required
def dashboard(request):
    settings_obj = GameSettings.objects.first()
    is_reveal_time = False
    if settings_obj and timezone.now() >= settings_obj.reveal_date:
        is_reveal_time = True

    # Verificar si el  usuario ya definio a quien le regala
    has_assigned = Assignment.objects.filter(giver=request.user).exists()

    # Calcular progreso de votacion (cuantos le faltan por votar)
    total_users = User.objects.exclude(id=request.user.id).count()
    my_votes_count = Vote.objects.filter(voter=request.user).count()

    context = {
        'is_reveal_time': is_reveal_time,
        'reveal_date': settings_obj.reveal_date if settings_obj else None,
        'has_assigned': has_assigned,
        'pending_votes': total_users - my_votes_count,
    }
    return render(request, 'game/dashboard.html', context)

@login_required
def set_my_target(request):
    if request.method == 'POST':
        target_id = request.POST.get('target_user')
        target_user = get_object_or_404(User, id=target_id)
        
        assignment, created = Assignment.objects.get_or_create(giver=request.user)
        assignment.set_receiver(target_user.username)
        return redirect('dashboard')
    
    # Lista de posibles personas (excluyendo al propio usuario)
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'game/set_target.html', {'users': users})

# game/views.py

@login_required
def voting_area(request):
    # 1. Obtener IDs de usuarios por los que YA he votado
    voted_ids = Vote.objects.filter(voter=request.user).values_list('target_giver_id', flat=True)
    
    # 2. Filtrar los objetivos pendientes (excluyendo por los que ya voté y a mí mismo)
    pending_targets = User.objects.exclude(id__in=voted_ids).exclude(id=request.user.id)

    # 3. NUEVO: Obtener los objetos de voto completos para mostrarlos en la lista lateral
    my_votes = Vote.objects.filter(voter=request.user).select_related('target_giver')

    if request.method == 'POST':
        target_giver_id = request.POST.get('target_giver_id')
        guessed_receiver_id = request.POST.get('guessed_receiver_id')

        if target_giver_id and guessed_receiver_id:
            target = get_object_or_404(User, id=target_giver_id)
            guess = get_object_or_404(User, id=guessed_receiver_id)
            
            # Guardamos o actualizamos el voto
            vote, created = Vote.objects.get_or_create(voter=request.user, target_giver=target)
            vote.set_guess(guess.username)
            
            messages.success(request, f'¡Anotado! Crees que {target.username} le regala a {guess.username}.')

        return redirect('voting_area')
    
    # Lista de todos los usuarios para el dropdown
    all_users = User.objects.all()

    context = {
        'pending_targets': pending_targets,
        'all_users': all_users,
        'my_votes': my_votes  # <--- ¡ENVIAMOS ESTA LISTA AL TEMPLATE!
    }

    return render(request, 'game/voting_area.html', context)
    # Usuarios por los que No he votado aun y no soy yo
    voted_ids = Vote.objects.filter(voter=request.user).values_list('target_giver_id', flat=True)
    pending_targets = User.objects.exclude(id__in=voted_ids).exclude(id=request.user.id)

    if request.method == 'POST':
        target_giver_id = request.POST.get('target_giver_id')
        guessed_receiver_id = request.POST.get('guessed_receiver_id')

        # Es buena práctica verificar que no sean None antes de buscar
        if target_giver_id and guessed_receiver_id:
            target = get_object_or_404(User, id=target_giver_id)
            guess = get_object_or_404(User, id=guessed_receiver_id)

        vote, created = Vote.objects.get_or_create(voter=request.user, target_giver=target)
        vote.set_guess(guess.username)

        # 2. AÑADIR ESTE MENSAJE DE ÉXITO
        messages.success(request, f'¡Predicción guardada! Crees que {target.username} le regala a {guess.username}.')

        return redirect('voting_area')
    
    # Para el dropdown: todos los usuarios menos el target_giver y el mismo target (logica basica)
    all_users = User.objects.all()

    return render(request, 'game/voting_area.html', {
        'pending_targets': pending_targets,
        'all_users': all_users
    })

@login_required
def results_dashboard(request):
    settings_obj = GameSettings.objects.first()
    if not settings_obj or timezone.now() < settings_obj.reveal_date:
        return render(request, 'game/too_early.html')
    
    users = User.objects.all()
    scoreboard = [] 

    # Mapas de contadores globales
    correct_guesses = 0
    total_votes = 0

    # 1. Mapa de Realidad: ¿Quién le regala a quién realmente?
    reality_map = {} 
    assignments = Assignment.objects.all()
    for a in assignments:
        reality_map[a.giver.username] = a.get_receiver()

    # 2. Procesar a CADA usuario
    for u in users:
        points = 0
        vote_details = [] # <--- Aquí guardaremos la historia pública de votos
        
        user_votes = Vote.objects.filter(voter=u)
        
        for v in user_votes:
            total_votes += 1
            guessed_username = v.get_guess() # Quién dijo el usuario que era el receptor
            target_giver_username = v.target_giver.username # Sobre quién estaba votando
            
            # Verificamos contra la realidad
            real_receiver = reality_map.get(target_giver_username)
            
            is_correct = False
            if real_receiver and real_receiver == guessed_username:
                points += 1
                correct_guesses += 1
                is_correct = True
            
            # Guardamos el detalle público
            vote_details.append({
                'target': target_giver_username,   # El votante dijo que ESTA PERSONA...
                'guessed': guessed_username,       # ...le regalaba a ESTA OTRA
                'is_correct': is_correct
            })

        scoreboard.append({
            'username': u.username,
            'points': points,
            'vote_details': vote_details # <--- Pasamos la lista al template
        })

    # Ordenar ganadores (fuera del bucle)
    scoreboard.sort(key=lambda x: x['points'], reverse=True)
    winner = scoreboard[0] if scoreboard else None


    # --- NUEVO: Preparar la lista oficial de asignaciones ---
    official_assignments = []
    for a in assignments:
        official_assignments.append({
            'giver': a.giver.username,
            'receiver': a.get_receiver() # Esto ya devuelve el nombre desencriptado
        })
    # -------------------------------------------------------

    # Datos para Chart.js
    chart_labels = [x['username'] for x in scoreboard]
    chart_data = [x['points'] for x in scoreboard]

    context = {
    'winner': winner,
    'scoreboard': scoreboard,
    'official_assignments': official_assignments,
    'chart_labels': json.dumps(chart_labels),
    'chart_data': json.dumps(chart_data),
    'accuracy': round((correct_guesses/total_votes)*100, 2) if total_votes > 0 else 0
    }
        
    return render(request, 'game/results.html', context)


