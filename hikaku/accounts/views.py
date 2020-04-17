from django.shortcuts import render
from allauth.account import views
from allauth.account.views import *
import requests
from django.contrib.auth.models import User
from accounts.models import CustomUser #自作のユーザーモデルを使用するために読み込む
from scraping.models import ItemFavorite
from accounts.forms import MyCustomSignupForm


# Create your views here.

class SigninView(views.LoginView):
    template_name = 'accounts/index.html'

    def dispatch(self, request, *args, **kwargs):
        response = super(SigninView, self).dispatch(request, *args, **kwargs)
        return response

    def form_valid(self, form):
      return super(SigninView, self).form_valid(form)

signin_view = SigninView.as_view()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#関数型で記述　(余裕があればallauthでの実装も)

def signup_func(request):
    user2 = CustomUser.objects.all()
    context = {'form': MyCustomSignupForm}
    if request.method == 'POST':
        user_name = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        department = request.POST.get('department')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user = CustomUser.objects.create_user(
            user_name=user_name,
            full_name=full_name,
            email=email,
            department=department,
            password=password1)

        user.save()

        context = {
            "username" :username,
        }

        return render(request, 'account/signup.html', context)
    return render(request, 'account/signup.html', context)

#ユーザーホーム画面の表示(ユーザー名、本名、email-address を表示)
def home(request):
    user = request.user
    if user.is_authenticated:
        #username = request.GET.get("username")
        user_object = CustomUser.objects.get(username=user)
        try:
            registered_item_list = ItemFavorite.objects.filter(username=user)
        except:
            registered_item_list = None
            pass
        
        context = {
            "user" : user, 
            "registered_item_list" : registered_item_list,
        }
       
        return render(request, 'account/home.html', context)
    else:
        context = {
            "user" : None
        }
        return render(request, 'account/home.html', context)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class SignupView(RedirectAuthenticatedUserMixin, CloseableSignupMixin,
                 AjaxCapableProcessFormViewMixin, FormView):
#    template_name = "account/signup." + app_settings.TEMPLATE_EXTENSION
    template_name = "account/signup.html"
    form_class = SignupForm
    redirect_field_name = "next"
    success_url = None

    

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'signup', self.form_class)

    def get_success_url(self):
        # Explicitly passed ?next= URL takes precedence
        ret = (
            get_next_redirect_url(
                self.request,
                self.redirect_field_name) or self.success_url)
        return ret

    def form_valid(self, form):
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance
        self.user = form.save(self.request)
        try:
            return complete_signup(
                self.request, self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response

    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        form = ret['form']
        email = self.request.session.get('account_verified_email')
        if email:
            email_keys = ['email']
            if app_settings.SIGNUP_EMAIL_ENTER_TWICE:
                email_keys.append('email2')
            for email_key in email_keys:
                form.fields[email_key].initial = email
        login_url = passthrough_next_redirect_url(self.request,
                                                  reverse("account_login"),
                                                  self.redirect_field_name)
        redirect_field_name = self.redirect_field_name
        redirect_field_value = get_request_param(self.request,
                                                 redirect_field_name)
        ret.update({"login_url": login_url,
                    "redirect_field_name": redirect_field_name,
                    "redirect_field_value": redirect_field_value})
        return ret



signup = SignupView.as_view()


