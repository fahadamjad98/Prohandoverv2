from django.urls import path
from . import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('record/<int:pk>', views.customer_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('add_record/', views.add_record, name='add_record'),
    path('add_cheque/<int:record_id>/', views.add_cheque, name='add_cheque'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    # Paths for PROPERTY CRUD
    path('property/<int:pk>', views.owner_property, name='property'),
    path('delete_property/<int:pk>', views.delete_property, name='delete_property'),
    path('add_property/', views.add_property, name='add_property'),
    path('update_property/<int:pk>', views.update_property, name='update_property'),
    # path('tenant_dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    # path('show_associated_record/', views.show_associated_record, name='show_associated_record'),
    path('create_maintenance_ticket/', views.create_maintenance_ticket, name='create_maintenance_ticket'),
    path('delete_maintenance_ticket/<int:ticket_id>/', views.delete_maintenance_ticket, name='delete_maintenance_ticket'),
    path('view_maintenance_tickets/<int:record_id>/<int:ticket_id>/', views.view_maintenance_tickets, name='view_maintenance_tickets'),
    path('problemfixers/', views.problem_fixers, name='problem_fixers'),
    path('update_ticket_status/<int:ticket_id>/', views.update_ticket_status, name='update_ticket_status'),
    path('create_quotation/<int:record_id>/<int:ticket_id>/', views.create_quotation, name='create_quotation'),
    path('view_quotations/<int:record_id>/<int:ticket_id>/', views.view_quotations, name='view_quotations'),
    path('update_quotation/<int:record_id>/<int:ticket_id>/<int:quotation_id>/', views.update_quotation, name='update_quotation'),
    path('list_of_records/', views.list_of_records, name='list_of_records'),
    path('list_of_properties/', views.list_of_properties, name='list_of_properties'),
    #path('send_login_email/', views.send_login_email, name='send_login_email'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('update_my_profile/', views.update_my_profile, name='update_my_profile'),
#   path('add_solo_tenant/', views.add_solo_tenant, name='add_solo_tenant'),
    path('list_of_tickets', views.list_of_tickets, name='list_of_tickets'),
    
]


htmx_urlpatterns = [
    path('check_username/', views.check_username, name='check_username'),
] 

htmx_urlpatterns = [
     path('check_username/', views.check_username, name='check_username'),
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += htmx_urlpatterns




