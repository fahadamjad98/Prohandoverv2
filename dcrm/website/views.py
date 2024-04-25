from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm, AddpropertyForm, LoginForm, MaintenanceTicketForm, UserProfileForm, ChequeForm, TenantSearchForm, PropertySearchForm
from .models import Record, Property, MaintenanceTicket, Product, User
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .forms import Quotation, ProductForm, ResetPasswordForm, QuotationForm
from django.db.models import Sum, F
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from django import template
from django.core.mail import send_mail
from .tasks import send_login_email, send_register_email, send_contract_expiry_reminder
from celery import current_app
from django.contrib.auth import update_session_auth_hash
from django.forms import inlineformset_factory
from django.db import IntegrityError
from django.db.models import Q




def index(request):
    return render(request, 'index.html')



def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # Enqueue the Celery task to send login email
                send_login_email.delay(user.email, user.username)

                # Redirect based on user type
                if user.is_admin:
                    return redirect('home')
                elif user.is_tenant:
                    return redirect('home')
                elif user.is_PF:
                    return redirect('problem_fixers')
                elif user.is_owner:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Invalid form submission. Please check your input.')

    return render(request, 'login.html', {'form': form})

register = template.Library()

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@login_required
def home(request):
    user = request.user

    if user.is_owner:
        return owner_dashboard(request, user)
    elif user.is_tenant:
        return tenant_dashboard(request)
    else:
        return redirect('index.html')



def owner_dashboard(request, owner_username):
    # Retrieve the owner based on the username
    owner = get_object_or_404(User, username=owner_username, is_owner=True)

    # Retrieve relevant data for the owner's dashboard
    records = Record.objects.filter(user=owner)
    properties = Property.objects.filter(user=owner)
    total_records_count = records.count()
    total_properties_count = properties.count()
    maintenance_tickets = MaintenanceTicket.objects.filter(record__user=owner)

    owner_records = Record.objects.filter(user=owner)
    days_until_expiry_list = [(record, (record.contract_end - timezone.now().date()).days) for record in owner_records]

    context = {
        'owner': owner,
        'records': records,
        'properties': properties,
        'total_records_count': total_records_count,
        'total_properties_count': total_properties_count,
        'maintenance_tickets': maintenance_tickets,
        'days_until_expiry_list': days_until_expiry_list,
        'owner_username': owner_username,
    }

    return render(request, 'home.html', context)

@login_required
def list_of_records(request):
    records = Record.objects.filter(user=request.user)
    maintenance_tickets = MaintenanceTicket.objects.filter(record__user=request.user)
    form = TenantSearchForm(request.GET)

    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        if search_query:
            records = records.filter(first_name__icontains=search_query) | records.filter(last_name__icontains=search_query)

    return render(request, 'list_of_records.html', {'records': records, 'maintenance_tickets': maintenance_tickets, 'form': form})

@login_required
def list_of_properties(request):
    if request.user.is_authenticated and request.user.is_owner:
        properties = Property.objects.filter(user=request.user)
        search_form = PropertySearchForm(request.GET)

        if search_form.is_valid():
            search_query = search_form.cleaned_data.get('search_query')
            
            if search_query:
                properties = properties.filter(
                    Q(property_number__icontains=search_query) |
                    Q(property_location__icontains=search_query)
                )
        
        return render(request, 'list_of_properties.html', {'properties': properties, 'search_form': search_form})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('index')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']  # Move this line here
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            #send email to the registered user
            send_register_email.delay(email, username)
            messages.success(request, f"Account created for {username}")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


@login_required
def customer_record(request, pk):
    customer_record = get_object_or_404(Record, id=pk, user=request.user)
    document_info_urls = zip(
        [
            customer_record.tenant_doc_info_1,
            customer_record.tenant_doc_info_2,
            customer_record.tenant_doc_info_3,
            customer_record.tenant_doc_info_4,
            customer_record.tenant_doc_info_5,
            customer_record.tenant_doc_info_6,
        ],
        [
            customer_record.tenant_document_1.url if customer_record.tenant_document_1 else None,
            customer_record.tenant_document_2.url if customer_record.tenant_document_2 else None,
            customer_record.tenant_document_3.url if customer_record.tenant_document_3 else None,
            customer_record.tenant_document_4.url if customer_record.tenant_document_4 else None,
            customer_record.tenant_document_5.url if customer_record.tenant_document_5 else None,
            customer_record.tenant_document_6.url if customer_record.tenant_document_6 else None,
        ]
    )

    days_until_expiry = (customer_record.contract_end - timezone.now().date()).days
    current_date = timezone.now().date()

    if not customer_record.reminder_sent and days_until_expiry == 100:
        send_contract_expiry_reminder.apply_async(
            (request.user.email, request.user.username, days_until_expiry)
        )

    return render(
        request,
        'record.html',
        {
            'customer_record': customer_record,
            'days_until_expiry': days_until_expiry,
            'current_date': current_date,
            'document_info_urls': document_info_urls,
        },
    )


    
@login_required 
def delete_record(request, pk):
    if request.user.is_authenticated:
        # Ensure that the record belongs to the currently logged-in user
        record_to_delete = get_object_or_404(Record, id=pk, user=request.user)

        # Retrieve the associated property before deleting the record
        property_instance = record_to_delete.property

        # Delete the record
        record_to_delete.delete()

        # If the property is associated, update the is_associated field
        if property_instance:
            property_instance.is_associated = False
            property_instance.save()

        messages.success(request, "Record Deleted Successfully")
        return redirect('home')
    else:
        messages.success(request, "You must be logged in!")
        return redirect('home')
        

@login_required
def add_record(request):
    if request.method == 'POST':
        form = AddRecordForm(request.user, request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            property_id = request.POST.get('property')
            property_instance = get_object_or_404(Property, id=property_id, user=request.user)

            if property_instance.is_associated:
                messages.error(request, "Property is already associated with another record.")
                return redirect('add_record')

            try:
                record = form.save(commit=False)
                record.user = request.user
                record.email = form.cleaned_data['tenant_email']
                record.property = property_instance
                record.save()

                # Mark the property as associated
                property_instance.is_associated = True
                property_instance.save()
                
                # Accessing name and unit number associated with the property through the record
                property_name = record.property.property_name
                property_number = record.property.property_number

                messages.success(request, f"Tenant Added for Property: {property_name}, Unit Number: {property_number}")

                return redirect('home')
            except IntegrityError:
                messages.error(request, "An error occurred while adding the record. Please try again.")
    else:
        form = AddRecordForm(request.user)

    return render(request, 'add_record.html', {'form': form})

    
@login_required
def update_record(request, pk):
    current_record = get_object_or_404(Record, id=pk, user=request.user)

    # Retrieve the associated property of the current record
    property_instance = current_record.property

    # Pass the property instance to the form for prepopulating the property field
    form = AddRecordForm(request.user, request.POST or None, instance=current_record, initial={'property': property_instance, 'tenant_email': current_record.email})

    if request.method == 'POST':
        if form.is_valid():
            # Proceed with saving the form
            record = form.save(commit=False)
            record.email = form.cleaned_data['tenant_email']
            record.save()

            messages.success(request, "Record Updated")
            return redirect('home')

    return render(request, 'update_record.html', {'form': form})
     
    



def add_cheque(request, record_id):
    record = get_object_or_404(Record, id=record_id, user=request.user)

    if request.method == 'POST':
        cheque_form = ChequeForm(request.POST)
        if cheque_form.is_valid():
            cheque = cheque_form.save(commit=False)
            cheque.record = record
            cheque.save()
            messages.success(request, "Cheque information added successfully.")
            return redirect('home')  # Redirect to the desired page

    else:
        cheque_form = ChequeForm()

    return render(request, 'add_cheque.html', {'cheque_form': cheque_form})
        
        
@login_required
def owner_property(request, pk):
    # Ensure that the property belongs to the currently logged-in user
    owner_property = get_object_or_404(Property, id=pk, user=request.user)

    # Get the URLs and labels for all three documents
    document_info_urls = zip(
        [
            owner_property.property_doc_info_1,
            owner_property.property_doc_info_2,
            owner_property.property_doc_info_3,
        ],
        [
            owner_property.property_document_1.url if owner_property.property_document_1 else None,
            owner_property.property_document_2.url if owner_property.property_document_2 else None,
            owner_property.property_document_3.url if owner_property.property_document_3 else None,
        ]
    )

    return render(request, 'property.html', {'owner_property': owner_property, 'document_info_urls': document_info_urls})

            
        
@login_required
def delete_property(request, pk):
    # Ensure that the property belongs to the currently logged-in user
    delete_it = get_object_or_404(Property, id=pk, user=request.user)

    delete_it.delete()
    messages.success(request, "Property Deleted Successfully")
    return redirect('home')
        
        
@login_required
def add_property(request):
    if request.method == 'POST':
        # Create an instance of AddpropertyForm with both request.POST and request.FILES
        form = AddpropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the property information
            property_instance = form.save(commit=False)
            property_instance.user = request.user
            property_instance.save()

            # Since you're handling property documents within AddpropertyForm,
            # there's no need for a separate DocumentForm.
            # You can handle property documents here if needed.

            messages.success(request, "Property Added")
            if request.user.is_owner:
                return redirect('list_of_properties')
            elif request.user.is_tenant:
                return redirect('add_record')
    else:
        # If the request method is GET, create a new instance of AddpropertyForm
        form = AddpropertyForm()

    return render(request, 'add_property.html', {'form': form})





@login_required
def update_property(request, pk):
    current_property = get_object_or_404(Property, id=pk, user=request.user)

    form = AddpropertyForm(request.POST or None, instance=current_property)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Property has been updated")
            return redirect('home')

    return render(request, 'update_property.html', {'form': form})




def admin(request):
    return render(request,'admin.html')



def owner(request):
    return render(request,'home.html')


@login_required
def create_maintenance_ticket(request):
    if request.user.is_authenticated and request.user.is_tenant:
        if request.method == 'POST':
            form = MaintenanceTicketForm(request.POST)
            if form.is_valid():
                try:
                    # Assuming you have a way to get the current tenant record (adjust this based on your logic)
                    record = Record.objects.get(email=request.user.email)
                except Record.DoesNotExist:
                    record = None

                if record:
                    ticket = form.save(commit=False)
                    ticket.record = record
                    ticket.save()
                    messages.success(request, "Maintenance Ticket Created Successfully")
                    return redirect('home')  # Assuming 'tenant_dashboard' is the correct URL name
                else:
                    messages.error(request, "Tenant record not found. Please ensure your record is set up.")
            else:
                messages.error(request, "Invalid form submission. Please check your input.")
        else:
            form = MaintenanceTicketForm()

        return render(request, 'create_maintenance_ticket.html', {'form': form})
    else:
        messages.error(request, "You are not authenticated as a tenant.")
        return redirect('home')  # Redirect to the home page or login page


@login_required
def tenant_dashboard(request):
    if request.user.is_authenticated and request.user.is_tenant:
        user_email = request.user.email
        try:
            record = Record.objects.get(email=user_email)
            maintenance_tickets = MaintenanceTicket.objects.filter(record=record)
        except Record.DoesNotExist:
            record = None
            maintenance_tickets = []

        return render(request, 'tenant_dashboard.html', {'record': record, 'maintenance_tickets': maintenance_tickets})
    else:
        return redirect('index.html')  # or another appropriate URL
    
    
@login_required
def delete_maintenance_ticket(request, ticket_id):
    ticket = get_object_or_404(MaintenanceTicket, id=ticket_id)

    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Maintenance Ticket Deleted Successfully")

    return redirect('home')  # Redirect to the correct URL after deletion


@login_required
def view_maintenance_tickets(request, record_id, ticket_id):
    record = get_object_or_404(Record, id=record_id)
    maintenance_tickets = MaintenanceTicket.objects.filter(record=record)
    return render(request, 'view_maintenance_tickets.html', {'maintenance_tickets': maintenance_tickets, 'record': record, 'ticket_id': ticket_id})


@login_required
def problem_fixers(request):
    if request.user.is_authenticated and request.user.is_PF:
        # Fetch all maintenance tickets
        
        maintenance_tickets = MaintenanceTicket.objects.all()
        

        #print(maintenance_tickets)  # Add this line for debugging purposes

        return render(request, 'problem_fixers.html', {'maintenance_tickets': maintenance_tickets})
    else:
        return render(request, 'access_denied.html')

    
    

@login_required
def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        print('Received POST request with data:', request.POST)
        ticket = get_object_or_404(MaintenanceTicket, id=ticket_id)
        new_status = request.POST.get('status')

        # Handle rejection reason
        rejection_reason = request.POST.get('rejection_reason', '')

        if new_status == 'Rejected for Inspection':
            ticket.rejection_reason = rejection_reason

        # Update the status only if it's a valid choice
        if new_status in [choice[0] for choice in MaintenanceTicket.APPROVAL_CHOICES]:
            ticket.status = new_status
            
            if new_status == 'Quotation Approved By Owner':
                ticket.quote_owner_approval = True
            elif new_status == 'Quotation Approved By Tenant':
                ticket.quote_tenant_approval = True
            

            ticket.save()

            # Display a success message
            messages.success(request, "Ticket status updated successfully")
            
            if request.user.is_owner or request.user.is_tenant:
            # Redirect the user to the appropriate page
                return redirect('home')
            else:
                return redirect('problem_fixers')

    # Display an error message
    messages.error(request, "Error: Invalid status or ticket not found")

    # Redirect the user to the appropriate page
    return redirect('home')


@login_required
def create_quotation(request, ticket_id, record_id):
    ticket = get_object_or_404(MaintenanceTicket, id=ticket_id)
    record = get_object_or_404(Record, id=record_id)
   

    if request.method == 'POST':
        QuotationFormSet = formset_factory(ProductForm, extra=1)
        formset = QuotationFormSet(request.POST)

        if formset.is_valid():
           
            # Create a Quotation instance
            quotation = Quotation(record=record, maintenance_ticket=ticket)
            quotation.save()

            # Save the products and associate them with the quotation
            for form in formset:
                product = form.save(commit=False)
                
                # Convert 'paid_by_owner' to boolean
                paid_by_owner = form.cleaned_data.get('paid_by_owner')
                product.paid_by_owner = paid_by_owner

                product.quotation = quotation
                product.save()

            ticket.status = 'Quotation Created'
            ticket.save()
            messages.success(request, "Quotation created successfully")
            return redirect('problem_fixers')  # Redirect to the appropriate URL after successful submission
        else:
            messages.error(request, "Invalid form submission. Please check your input.")
    else:
        formset = formset_factory(ProductForm, extra=1)

    return render(request, 'create_quotation.html', {'formset': formset})



@login_required
def view_quotations(request, record_id, ticket_id):

    ticket = get_object_or_404(MaintenanceTicket, id=ticket_id)
    record = get_object_or_404(Record, id=record_id)
    maintenance_ticket = get_object_or_404(MaintenanceTicket, id=ticket_id, record=record)
    
    # Fetch all quotations related to the specified maintenance ticket
    quotations = Quotation.objects.filter(maintenance_ticket=maintenance_ticket)
    
    # Initialize totals for owners and tenants
    owner_total = 0
    tenant_total = 0
    
    # Dictionary to store products for each quotation
    quotation_products = {}
    
    # Populate the dictionary with products for each quotation
    for quotation in quotations:
        products = Product.objects.filter(quotation=quotation)
        quotation.total_amount = products.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        quotation_products[quotation] = products
        
        # Separate totals for owners and tenants
        for product in products:
            if request.user.is_owner and product.paid_by_owner:
                owner_total += product.total
            elif request.user.is_tenant and not product.paid_by_owner:
                tenant_total += product.total
                
    total_of_all_totals = round(sum(quotation.total_amount for quotation in quotations), 2)
    
    return render(request, 'view_quotations.html', {
        'record': record,
        'quotations': quotations,
        'quotation_products': quotation_products,
        'owner_total': round(owner_total, 2),
        'tenant_total': round(tenant_total, 2),
        'total_of_all_totals': total_of_all_totals,
        'ticket': ticket,
    })
    


@login_required
def update_quotation(request, record_id, ticket_id, quotation_id):
    # Fetch the necessary objects
    record = get_object_or_404(Record, id=record_id)
    ticket = get_object_or_404(MaintenanceTicket, id=ticket_id)
    quotation = get_object_or_404(Quotation, id=quotation_id, maintenance_ticket=ticket)

    ProductFormSet = inlineformset_factory(Quotation, Product, form=ProductForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = QuotationForm(request.POST, instance=quotation)
        formset = ProductFormSet(request.POST, instance=quotation)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            messages.success(request, "Quotation updated successfully")
            return redirect('view_quotations', record_id=record.id, ticket_id=ticket.id)
        else:
            messages.error(request, "Invalid form submission. Please check your input.")
    else:
        form = QuotationForm(instance=quotation)
        formset = ProductFormSet(instance=quotation)

    return render(request, 'update_quotation.html', {
        'record': record,
        'ticket': ticket,
        'quotation': quotation,
        'form': form,
        'product_formset': formset,
        # Add other necessary context variables...
    })
    
@login_required
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Assuming you have a User model and the current user is authenticated
            user = request.user

            # Check the old password
            if not user.check_password(form.cleaned_data['password_old']):
                messages.error(request, 'Old password is incorrect.')
                return redirect('reset_password')

            # Update the user's password
            user.set_password(form.cleaned_data['password_new1'])
            user.save()

            # Update the session to reflect the password change
            update_session_auth_hash(request, user)

            messages.success(request, 'Password successfully updated.')
            return redirect('home')  # Redirect to the home page or wherever you want

    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})         
            



def my_profile(request):
    # Assuming you have a user object available in the request
    user = request.user
    context = {'user': user}

    return render(request, 'user_profile.html', context)


@login_required
def update_my_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()

            # Update corresponding fields in the signup model
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.registered_number = form.cleaned_data['registered_number']
            user.save()

            messages.success(request, "Profile has been updated")
            return redirect('my_profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'update_user_profile.html', {'form': form})



#User 
def check_username(request):
    username = request.POST.get('username')
    exists = get_user_model().objects.filter(username=username).exists()

    if exists:
        message = "<div style='color: red;'> This username already exists </div>"
    else:
        message = "<div style='color: green;'> This username is available </div>"

    return HttpResponse(message)
    

def list_of_tickets(request):
    if request.user.is_authenticated and request.user.is_PF:
        # Fetch all maintenance tickets
        
        maintenance_tickets = MaintenanceTicket.objects.all()
        

        #print(maintenance_tickets)  # Add this line for debugging purposes

        return render(request, 'list_of_tickets.html', {'maintenance_tickets': maintenance_tickets})
    else:
        return render(request, 'access_denied.html')

#def add_solo_tenant(request):
#    user = request.user
#    if request.method == 'POST':
#        form = UserProfileForm(request.POST, instance=user)
#        if form.is_valid():
#            form.save()
#            user.first_name = form.cleaned_data['first_name']
#            user.last_name = form.cleaned_data['last_name']
#            user.email = form.cleaned_data['email']
#            user.registered_number = form.cleaned_data['registered_number']
#            user.save()
#            messages.success(request, "Profile has been updated")
#            return redirect('add_property')
#        else:
#            print(form.errors)  # Print form errors to debug
#    else:
#        form = UserProfileForm(instance=user)
#    print(form)  # Print form object to verify it's passed to the template
#    return render(request, 'add_solo_tenant.html', {'form': form})







    
    
