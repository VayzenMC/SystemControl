from django.db import models
import uuid

class Device(models.Model):
    name = models.CharField(max_length=100, verbose_name="Qurilma nomi")
    device_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Maxsus Token")
    is_online = models.BooleanField(default=False, verbose_name="Aloqadami")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Oxirgi faollik")

    def __str__(self):
        return self.name

class Command(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='commands', verbose_name="Qurilma")
    command_text = models.TextField(verbose_name="Buyruq (CMD/Bash)")
    password = models.CharField(max_length=200, blank=True, null=True, verbose_name="Tizim paroli") # <-- Parol shu yerda saqlanadi
    response_text = models.TextField(blank=True, null=True, verbose_name="Natija")
    is_executed = models.BooleanField(default=False, verbose_name="Bajarildimi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} -> {self.command_text[:30]}"