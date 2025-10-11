from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    paginate_by = 10
    template_name = 'clientes_app/cliente_list.html'

class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes_app/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    permission_required = 'clientes_app.add_cliente'

class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes_app/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    permission_required = 'clientes_app.change_cliente'

class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes_app/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')
    permission_required = 'clientes_app.delete_cliente'

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes_app/cliente_detail.html'
