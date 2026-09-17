from django.contrib import admin
from .models import Device, Command

# Admin panelda chiroyli ko'rinishi uchun
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_token', 'is_online', 'last_seen')
    readonly_fields = ('device_token',)

@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ('device', 'command_text', 'is_executed', 'created_at')
    list_filter = ('is_executed', 'created_at')