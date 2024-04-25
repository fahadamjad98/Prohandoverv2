from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Property, User, MaintenanceTicket, Record, Quotation, Product, Cheque
from phonenumber_field.formfields import PhoneNumberField



class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    registered_number = PhoneNumberField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}), required=False)
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'registered_number', 'first_name', 'last_name', 'email', 'password1', 'password2','is_owner','is_tenant','is_PF','is_admin')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

    def clean(self):
        cleaned_data = super().clean()
        is_owner = cleaned_data.get('is_owner')
        is_tenant = cleaned_data.get('is_tenant')

        if not is_owner and not is_tenant:
            raise forms.ValidationError('Please select at least one role (Owner or Tenant).')

        return cleaned_data
         

class AddRecordForm(forms.ModelForm):
    PAYMENT_MODES = [
        ('Cheque', 'Cheque'),
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    
    STATES = [
        ('Abu Dhabi', 'Abu Dhabi'),
        ('Dubai', 'Dubai'),
        ('Sharjah', 'Sharjah'),
        ('Ajman', 'Ajman'),
        ('Umm Al Quwain', 'Umm Al Quwain'),
        ('Ras Al Khaimah' , 'Ras Al Khaimah'),
        ('Fujairah', 'Fujairah'),
    ]
    
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "First Name", "class": "form-control"}), label="First Name:")
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Last Name", "class": "form-control"}), label="Last Name:")
    tenant_email = forms.EmailField(label="Tenant's Email", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Tenant's Email"}))
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}), label="Phone:")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Address", "class": "form-control"}), label="Address:")
    state = forms.ChoiceField(required=True, choices=STATES, widget=forms.Select(attrs={"class": "form-control"}), label="State:")
    property = forms.ModelChoiceField(queryset=Property.objects.all(), widget=forms.Select(attrs={"class": "form-control"}), label="Property")
    dewa = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "DEWA No.", "class": "form-control"}), label="DEWA:")
    contract_start = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control"}))
    contract_end = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control"}))
    annual_rent = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Annual Rent", "class": "form-control"}), label="Annual Rent:")
    contract_value = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Contract Value", "class": "form-control"}), label="Contract Value:")
    security_deposit = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Security Deposit", "class": "form-control"}), label="Security Deposit:")
    mode_of_payment = forms.ChoiceField(required=True, choices=PAYMENT_MODES, widget=forms.Select(attrs={"class": "form-control"}), label="Mode of Payment:")
    
    def __init__(self, user, *args, **kwargs):
        super(AddRecordForm, self).__init__(*args, **kwargs)
        if user.is_tenant:  # Check if the user is a tenant
            # Prepopulate form fields with user's information
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['tenant_email'].initial = user.email
            self.fields['phone'].initial = user.registered_number
            # You can prepopulate additional fields if needed
        else:
            # If the user is not a tenant, keep the fields empty
            pass
        associated_properties = Record.objects.filter(user=user).values_list('property', flat=True)
        self.fields['property'].queryset = Property.objects.filter(user=user).exclude(id__in=associated_properties)
        self.fields['number_of_cheques'].required = False  # Make the field not required by default
        
    class Meta:
        model = Record
        fields = ['first_name', 'last_name', 'tenant_email', 'phone', 'address', 'state', 'property', 'dewa', 'contract_start', 'contract_end', 'annual_rent', 'contract_value', 'security_deposit', 'mode_of_payment', 'number_of_cheques',
                  'tenant_doc_info_1','tenant_document_1',
                  'tenant_doc_info_2','tenant_document_2',
                  'tenant_doc_info_3','tenant_document_3',
                  'tenant_doc_info_4','tenant_document_4',
                  'tenant_doc_info_5','tenant_document_5',
                  'tenant_doc_info_6','tenant_document_6',
                  ]

    def clean(self):
        cleaned_data = super().clean()
        property_id = cleaned_data.get('property')
        tenant_email = cleaned_data.get('tenant_email')

        # Check if a record with the same tenant email already exists for the selected property
        existing_records = Record.objects.filter(property_id=property_id, email=tenant_email)

        # For an update, allow the same email for the current record
        current_record = getattr(self, 'instance', None)
        if current_record:
            existing_records = existing_records.exclude(id=current_record.id)

        if existing_records.exists():
            raise forms.ValidationError(f'A record with the email "{tenant_email}" already exists for this property.')

        return cleaned_data



class ChequeForm(forms.ModelForm):
    class Meta:
        model = Cheque
        fields = '__all__'  # You can specify the fields explicitly if needed
        

class AddpropertyForm(forms.ModelForm):
    PROPERTY_TYPES = [
        ('Apartment', 'Apartment'),
        ('Land', 'Land'),
        ('Villa', 'Villa'),
        ('Town House', 'Town House'),
    ]
    property_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Project Name", "class": "form-control"}), label="Project / Building Name:")
    property_number = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Unit Number", "class": "form-control"}), label="Unit Number:")
    property_size = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Property Size", "class": "form-control"}), label="Property Size:")
    property_location = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Property Location", "class": "form-control"}), label="Property Location:")
    property_type = forms.ChoiceField(required=True, choices=PROPERTY_TYPES, widget=forms.Select(attrs={"class": "form-control"}), label="Property Type")
    property_bedrooms = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Bedrooms", "class": "form-control"}), label="Bedrooms:")
    property_bathrooms = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Bathrooms", "class": "form-control"}), label="Bathrooms:")
    property_rentedFor = forms.DecimalField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Rent Amount", "class": "form-control"}), label="Rented For:")

    class Meta:
        model = Property
        fields = ['property_name', 'property_number', 'property_size', 'property_location', 'property_type', 'property_bedrooms', 'property_bathrooms', 'property_rentedFor', 'property_doc_info_1',
                  'property_document_1', 
                  'property_doc_info_2', 'property_document_2', 
                  'property_doc_info_3', 'property_document_3']
        
        

class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'inspection_time','inspection_date']
        widgets = {
            'title': forms.Textarea(attrs={'cols': 50, 'rows': 1}),
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
            'inspection_date': forms.DateInput(attrs={'type': 'date'}),
            'inspection_time': forms.TimeInput(attrs={'type': 'time', 'min': '09:00', 'max': '18:00'}),
        }



class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = []  # Exclude fields that are moved to the Product model
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'paid_by_owner']
        
        
    paid_by_owner = forms.BooleanField(
        required=False,
        
    )

ProductFormSet = forms.formset_factory(ProductForm)



class ResetPasswordForm(forms.Form):
    password_old = forms.CharField(widget=forms.widgets.PasswordInput(attrs={"placeholder": "Current Password"}), label="Current Password", help_text='Enter your current password.')
    password_new1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "New Password"}), help_text='<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>')
    password_new2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"}), help_text='Confirm the new password.')

    def clean(self):
        cleaned_data = super().clean()
        password_new1 = cleaned_data.get('password_new1')
        password_new2 = cleaned_data.get('password_new2')

        # Check if the new passwords match
        if password_new1 and password_new2 and password_new1 != password_new2:
            raise forms.ValidationError("New passwords do not match.")

        # You can add more custom validation checks here

        return cleaned_data
    
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'registered_number')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Customize the form fields as needed
        
        


    

class TenantSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control mr-sm-2', 
            'placeholder': 'Search'
        })
    )
    

class PropertySearchForm(forms.Form):
    search_query = forms.CharField(max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control mr-sm-2', 
            'placeholder': 'Unit or Location'
    })
    )