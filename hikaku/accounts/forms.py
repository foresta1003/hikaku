from allauth.account.forms import SignupForm
from .models import CustomUser
from django import forms #必要？

class MyCustomSignupForm(SignupForm):
    class Meta:
        model = CustomUser

    full_name = forms.fields.CharField(
        max_length=20, label='名前(フルネーム)', initial='' ,help_text="フルネーム")
    
    department = forms.fields.ChoiceField(
        choices=(
            ('1', '所属１'),
            ('2', '所属２'),
            ('3', 'なし')
        ),
        label='所属'
    )

    def signup(self, request,user):
        user.department = self.cleaned_data['所属']
        #user.weight = self.cleaned_data['weight']
        user.save()
        return user

