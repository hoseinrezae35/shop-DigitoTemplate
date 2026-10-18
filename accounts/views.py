from urllib.parse import urlparse, quote
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views.generic import View, FormView
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from .models import User
from django.contrib import messages
from .forms import EmailAuthenticationForm, RegisterForm
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.http import url_has_allowed_host_and_scheme


class LoginClassView(LoginView):
    template_name = 'home/index.html'
    redirect_authenticated_user = True
    form_class = EmailAuthenticationForm

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return resolve_url('/')

    def dispatch(self, request, *args, **kwargs):
        # اگه کاربر لاگین بود و درخواست AJAX، JSON برگردون
        if request.user.is_authenticated and \
                request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
            })
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
            })

        messages.success(self.request, 'خوش آمدید')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]
            return JsonResponse({
                'success': False,
                'errors': errors,
            }, status=400)

        # fallback بدون JS
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        redirect_url = self.request.META.get('HTTP_REFERER', '/')
        parsed = urlparse(redirect_url)
        clean_url = parsed.path or '/'
        separator = '?'
        if next_url:
            return redirect(f"{clean_url}{separator}modal=login&next={quote(next_url)}")
        return redirect(f"{clean_url}{separator}modal=login")


class RegisterView(SuccessMessageMixin, FormView):
    template_name = "home/index.html"
    form_class = RegisterForm
    success_url = reverse_lazy("home:index")
    success_message = 'ثبت نام شما با موفقیت انجام شد'

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return str(self.success_url)

    def form_valid(self, form):
        user = User.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        login(self.request, user)

        # AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url(),
            })

        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]
            return JsonResponse({
                'success': False,
                'errors': errors,
            }, status=400)

        # fallback بدون JS
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        redirect_url = self.request.META.get('HTTP_REFERER', '/')
        parsed = urlparse(redirect_url)
        clean_url = parsed.path or '/'
        return redirect(f"{clean_url}?modal=register")


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('home:index')
