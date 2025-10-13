from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    paginate_by = 10
    template_name = 'cliente/cliente_list.html'
    context_object_name = 'clientes'

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')
    permission_required = 'clientes.add_cliente'

class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')
    permission_required = 'clientes.change_cliente'

class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'cliente/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')
    permission_required = 'clientes.delete_cliente'

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'cliente/cliente_detail.html'
