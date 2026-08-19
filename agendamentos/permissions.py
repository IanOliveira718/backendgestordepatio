"""
Permissões por tipo de usuário:

Admin        → acesso total
Portaria     → ver agendamentos, modificar status de agendamento, ver pallets (sem modificar)
Recebimento  → ver agendamentos, modificar status de agendamento, ver e modificar status de pallets
Fornecedor   → criar agendamentos e ver apenas os próprios
"""
from rest_framework.permissions import BasePermission


def get_tipo(user):
    try:
        return user.profile.tipo
    except Exception:
        return None


def is_blocked(user):
    try:
        return user.profile.bloqueado
    except Exception:
        return False


class NaoBloqueado(BasePermission):
    message = "Acesso bloqueado. Entre em contato com o administrador."

    def has_permission(self, request, view):
        return request.user.is_authenticated and not is_blocked(request.user)


class IsAdmin(BasePermission):
    message = "Acesso restrito a administradores."

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_tipo(request.user) == "administrador"


class IsAdminOuPortariaOuRecebimento(BasePermission):
    message = "Sem permissão para esta ação."

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_tipo(request.user) in (
            "administrador", "portaria", "recebimento"
        )


class IsAdminOuRecebimento(BasePermission):
    message = "Sem permissão para modificar pallets."

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_tipo(request.user) in (
            "administrador", "recebimento"
        )


class IsAdminOuFornecedor(BasePermission):
    message = "Sem permissão para esta ação."

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_tipo(request.user) in (
            "administrador", "fornecedor"
        )

class IsAdminMeioAmbienteOuColaborador(BasePermission):
    message = "Sem permissão para esta ação."

    def has_permission(self, request, view):
        return request.user.is_authenticated and get_tipo(request.user) in (
            "administrador","colaborador","meio_ambiente"
        )
