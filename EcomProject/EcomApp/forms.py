from django import forms
from .models import Category,Customer,Products,Order
from django .contrib.auth import(
    authenticate,
    get_user_model
)

User= get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
        return super(LoginForm, self).clean(*args, **kwargs)

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'