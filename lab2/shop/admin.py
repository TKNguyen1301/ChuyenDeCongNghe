from django.contrib import admin
from .models import Person, Group, Membership, Place, Restaurant, Manufacturer, Car

# Đăng ký models shop
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [MembershipInline]
    search_fields = ['name']

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['person', 'group', 'date_joined', 'invite_reason']
    list_filter = ['date_joined']
    search_fields = ['person__name', 'group__name']

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name', 'address']

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'serves_hot_dogs', 'serves_pizza']
    list_filter = ['serves_hot_dogs', 'serves_pizza']
    search_fields = ['name', 'address']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['country']
    search_fields = ['name', 'country']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'year']
    list_filter = ['manufacturer', 'year']
    search_fields = ['name', 'manufacturer__name']
