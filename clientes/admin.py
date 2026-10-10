from django.contrib import admin

from .models import Cliente, Nota


class NotaInline(admin.TabularInline):
    model = Nota
    extra = 0
    readonly_fields = ("criado_em",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "responsavel", "criado_em")
    search_fields = ("nome", "email", "telefone")
    list_filter = ("responsavel",)
    inlines = [NotaInline]


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "autor", "criado_em")
    search_fields = ("texto", "cliente__nome")
