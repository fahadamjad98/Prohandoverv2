# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.core.validators import MinValueValidator, FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
import magic


class User(AbstractUser):
    email = models.EmailField(unique=True)
    registered_number = PhoneNumberField(blank=False)
    is_admin = models.BooleanField('Is admin', default=False)
    is_owner = models.BooleanField('Is owner', default=False)
    is_tenant = models.BooleanField('Is tenant', default=False)
    is_PF = models.BooleanField('Is problem fixers', default=False)

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set')


ext_validator = FileExtensionValidator(['pdf','png','jpg','jpeg'])
def validate_file_mimetype(file):
    accept = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    print("Detected MIME type:", file_mime_type)  # Add this line to print the detected MIME type
    if file_mime_type not in accept:
        raise ValidationError("Unsupported file type")
    
    
class Property(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property_number = models.CharField(max_length=10)
    property_name = models.CharField(max_length=100)
    property_size = models.DecimalField(max_digits=10, decimal_places=2)
    property_location = models.CharField(max_length=100)
    is_associated = models.BooleanField(default=False)
    property_type = models.CharField(max_length=50, choices=[
        ('Apartment', 'Apartment'),
        ('Land', 'Land'),
        ('Villa', 'Villa'),
        ('Town House', 'Town House'),
        # Add more choices as needed
    ])
    property_bedrooms = models.IntegerField()
    property_bathrooms = models.IntegerField()
    property_rentedFor = models.DecimalField(max_digits=10, decimal_places=2)
    DOCUMENT_LABEL_CHOICES = [
        ('Title Deed', 'Title Deed'),
        ('Passport or Emirates ID', 'Emirates ID'),
        ('POA Document', 'POA Document'),
        # Add more choices as needed
    ]
    property_doc_info_1 = models.CharField(max_length=100, choices=DOCUMENT_LABEL_CHOICES, blank=True, null=True)
    property_document_1 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    property_doc_info_2 = models.CharField(max_length=100, choices=DOCUMENT_LABEL_CHOICES, blank=True, null=True)
    property_document_2 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    property_doc_info_3 = models.CharField(max_length=100, choices=DOCUMENT_LABEL_CHOICES, blank=True, null=True)
    property_document_3 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    

    def __str__(self):
        return f"{self.property_number} {self.property_name}"




class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)  # Email field should be unique
    phone = PhoneNumberField(blank=False)
    address = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, related_name='records')
    dewa = models.CharField(max_length=50)
    contract_start = models.DateField()
    contract_end = models.DateField()
    annual_rent = models.CharField(max_length=50)
    contract_value = models.CharField(max_length=50)
    security_deposit = models.CharField(max_length=50)
    reminder_sent = models.BooleanField(default=False)
    mode_of_payment = models.CharField(max_length=20, choices=[
        ('Cheque', 'Cheque'),
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Other', 'Other'),
    ])
    number_of_cheques = models.IntegerField(blank=True, null=True)
    TENANT_DOC_LABEL_CHOICES = [
        ('Ejari', 'Ejari'),
        ('Passport', 'Passport'),
        ('Tenancy Contract', 'Tenancy Contract'),
        ('Emirates ID', 'Emirates ID'),
        ('Visa', 'Visa'),
        ('Cheque/Cash Receipt', 'Cheque/Cash Receipt'),
        
        # Add more choices as needed
    ]
    tenant_doc_info_1 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_1 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    tenant_doc_info_2 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_2 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    tenant_doc_info_3 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_3 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    tenant_doc_info_4 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_4 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    tenant_doc_info_5 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_5 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    tenant_doc_info_6 = models.CharField(max_length=100, choices=TENANT_DOC_LABEL_CHOICES, blank=True, null=True)
    tenant_document_6 = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype], blank=True, null=True)
    
    
    def get_property_owner(self):
        return self.property.user

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Cheque(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='cheques')
    cheque_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cheque_date = models.DateField()
    cheque_owner = models.CharField(max_length=70)
    bank_name = models.CharField(max_length = 50)
    paid_to = models.CharField(max_length=70)


class MaintenanceTicket(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved for Inspection', 'Approved for Inspection'),
        ('Rejected for Inspection', 'Rejected for Inspection'),
        ('Quotation Created', 'Quotation Created'),
    ]

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Status before approval from owner
    status = models.CharField(max_length=80, choices=STATUS_CHOICES, default='Pending Approval for Inspection')
    
    # Approval status from owner
    APPROVAL_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Fixed", "Fixed"),
        ('Pending Approval', 'Pending Approval'),
        ('Approved for Inspection', 'Approved for Inspection'),
        ('Rejected for Inspection', 'Rejected for Inspection'),
        ('Inspection Done', 'Inspection Done'),
        ('Quotation Created', 'Quotation Created'),
        ('Quotation Approved By Owner',  'Quotation Approved By Owner'),
        ('Quotation Approved By Tenant',  'Quotation Approved By Tenant'),
        ('Quotation Rejected By Owner',  'Quotation Rejected By Owner'),
        ('Quotation Rejected By Tenant',  'Quotation Rejected By Tenant'),
        ('Issue Resolved', 'Issue Resolved'),
        ('Issue Not Resolved', 'Issue Not Resolved'),
    ]
    inspection_date = models.DateField(null=True, blank=True)
    inspection_time = models.TimeField(null=True, blank=True)
    owner_approval = models.CharField(max_length=60, choices=APPROVAL_CHOICES, default='Pending Approval')
    # Status after approval from owner
    maintenance_status = models.CharField(max_length=60, choices=STATUS_CHOICES, default='Pending Maintenance')
    rejection_reason = models.TextField(blank=True, null=True)
    quote_owner_approval = models.BooleanField(default=False)
    quote_tenant_approval = models.BooleanField(default=False)


    def update_maintenance_status(self, new_status):
        # Add any additional logic here, e.g., validation checks
        self.maintenance_status = new_status
        self.save()
    
class Quotation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    record = models.ForeignKey('Record', on_delete=models.CASCADE, related_name='quotations')
    maintenance_ticket = models.ForeignKey('MaintenanceTicket', on_delete=models.CASCADE, related_name='quotations')

class Product(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_by_owner = models.BooleanField()  # Add this field
    
    def save(self, *args, **kwargs):
        if self.price is not None and self.quantity is not None:
            # Calculate the total only if price and quantity are not None
            self.total = self.price * self.quantity
        else:
            # Handle the case where either price or quantity is None
            self.total = None
        super().save(*args, **kwargs)
    

    

#ext_validator = FileExtensionValidator(['pdf','png','jpg','jpeg'])
#def validate_file_mimetype(file):
#    accept = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
#    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
#    print("Detected MIME type:", file_mime_type)  # Add this line to print the detected MIME type
#    if file_mime_type not in accept:
#        raise ValidationError("Unsupported file type")
    
#class Document(models.Model):
#        name  = models.CharField(max_length=10)
#        document = models.FileField(upload_to='documents/', validators=[ext_validator, validate_file_mimetype])