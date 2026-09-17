from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Device, Command


def api_login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view(request, *args, **kwargs)
    return wrapped


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard')
        error = 'Login yoki parol noto\'g\'ri.'
    return render(request, 'remote/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def api_register_device(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    try:
        data = json.loads(request.body or '{}')
        name = str(data.get('name', '')).strip()
        if not name:
            return JsonResponse({'error': 'Device name is required'}, status=400)
        device = Device.objects.create(name=name)
        return JsonResponse({'token': str(device.device_token), 'device_id': device.id})
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@api_login_required
def api_device_list(request):
    devices = Device.objects.all().order_by('name')
    data = []
    for d in devices:
        data.append({
            'id': d.id,
            'name': d.name,
            'device_token': str(d.device_token),
            'is_online': d.is_online,
        })
    return JsonResponse({'devices': data})


@login_required
def dashboard_view(request):
    return render(request, 'remote/frontend/index.html')
@csrf_exempt
@api_login_required
def api_send_command(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            device_id = body.get('device_id')
            command_text = str(body.get('command_text', '')).strip()
            password = body.get('password', '')
            if not device_id or not command_text:
                return JsonResponse({'status': 'error', 'message': 'device_id and command_text are required'}, status=400)
            device = Device.objects.get(id=device_id)
            Command.objects.create(device=device, command_text=command_text, password=password)
            
            return JsonResponse({'status': 'success'})
        except Device.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Device not found'}, status=404)
        except (TypeError, json.JSONDecodeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

# Tanlangan qurilmaning terminal natijalarini olish
@api_login_required
def api_terminal_logs(request, device_id):
    try:
        device = Device.objects.get(id=device_id)
        commands = device.commands.all().order_by('-created_at')[:20]
        logs = []
        for c in commands:
            logs.append({
                'command': c.command_text,
                'response': c.response_text or 'Kutilmoqda...',
                'is_executed': c.is_executed
            })
        return JsonResponse({'logs': logs})
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

@csrf_exempt
def client_poll(request, token):
    try:
        device = Device.objects.get(device_token=token)
        device.is_online = True
        device.save(update_fields=['is_online', 'last_seen'])
        
        # Bajarilmagan buyruqni topish
        command = device.commands.filter(is_executed=False).first()
        if command:
            return JsonResponse({
                'has_command': True,
                'command_id': command.id,
                'command': command.command_text,
                'password': command.password
            })
        return JsonResponse({'has_command': False})
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found'}, status=404)

@csrf_exempt
def client_response(request, token):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command_id = data.get('command_id')
            response_text = data.get('output', data.get('response', ''))
            command = Command.objects.get(id=command_id, device__device_token=token)
            command.response_text = response_text
            command.is_executed = True
            command.save()
            
            return JsonResponse({'status': 'success'})
        except (TypeError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Command.DoesNotExist:
            return JsonResponse({'error': 'Command not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)