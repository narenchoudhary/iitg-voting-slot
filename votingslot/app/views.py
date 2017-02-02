from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.views.generic import View

from forms import LoginForm, TokenForm
from models import Appointment, Slot, Student


class LoginView(View):
    """
    View class for handling login functionality.
    """
    template_name = 'app/login.html'
    port = 995
    next = ''

    def get(self, request):
        self.next = request.GET.get('next', '')
        if request.user.is_authenticated():
                return redirect('token')
        args = dict(form=LoginForm(None), next=self.next)
        return render(request, self.template_name, args)

    def post(self, request):
        redirect_to = request.POST.get('next', self.next)
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            server = form.cleaned_data.get('login_server')

            user = auth.authenticate(username=username, password=password,
                                     server=server, port=self.port)
            if user is not None:
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    auth.login(request=request, user=user)
                    return redirect('token')
                else:
                    return redirect(redirect_to)
            else:
                form.add_error(None, 'No such user exists.')
                return render(request, self.template_name, dict(form=form))
        else:
            return render(request, self.template_name, dict(form=form))


class LogoutView(LoginRequiredMixin, View):
    """
    View class for handling logout.
    """
    login_url = reverse_lazy('login')
    http_method_names = ['get', 'head', 'options']

    def get(self, request):
        auth.logout(request=request)
        return redirect('login')


class TokenView(LoginRequiredMixin, View):
    """
    View class for processing Token form and rendering
    token data.
    """
    login_url = reverse_lazy('login')
    raise_exception = False
    template_name = 'app/token.html'

    def get(self, request):
        student = Student.objects.get(user=request.user)
        appointment = None
        form = None
        if student.token_booked:
            appointment = Appointment.objects.get(student=student)
        else:
            form = TokenForm()
        slot_list = Slot.objects.filter(stud_count__gt=99)
        context = dict(appointment=appointment, form=form,
                       student=student, slot_list=slot_list)
        return render(request, self.template_name, context)

    def post(self, request):
        student = Student.objects.get(user=request.user)
        slot_list = Slot.objects.filter(stud_count__gt=99)
        form = TokenForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.student = Student.objects.get(user=request.user)
            appointment = form.save()
            context = dict(student=student, appointment=appointment)
            return render(request, self.template_name, context)
        else:
            context = dict(student=student, form=form, slot_list=slot_list)
            return render(request, self.template_name, context)
