from allauth.account.adapter import DefaultAccountAdapter

class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        # Do not persist the user yet so we pass commit=False
        # (last argument)
        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)
        user.user_name = form.cleaned_data.get('username')
        user.department = form.cleaned_data.get('department')
        user.full_name = form.cleaned_data.get('full_name')
        user.save()