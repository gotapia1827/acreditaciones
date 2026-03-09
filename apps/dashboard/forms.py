from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import UserProfile


class CrearUsuarioForm(forms.Form):
    """Formulario para crear un nuevo usuario con rol."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre de usuario'
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellido'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña'
    )
    rol = forms.ChoiceField(
        choices=UserProfile.ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol'
    )
    empresa = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Empresa'
    )
    rut = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='RUT'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        # Actualizar perfil creado por el signal
        perfil = user.profile
        perfil.rol = data['rol']
        perfil.empresa = data.get('empresa', '')
        perfil.rut = data.get('rut', '')
        perfil.save()
        return user


class EditarUsuarioForm(forms.ModelForm):
    """Formulario para editar datos y rol de un usuario existente."""

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellido'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )

    class Meta:
        model = UserProfile
        fields = ['rol', 'empresa', 'rut', 'telefono']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            # Cargar datos actuales del User en los campos extra
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

        # Si se pasaron datos POST no pisar los iniciales
        if not args and not kwargs.get('data'):
            if user:
                self.initial['first_name'] = user.first_name
                self.initial['last_name'] = user.last_name
                self.initial['email'] = user.email

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        if commit:
            perfil.save()
        return perfil