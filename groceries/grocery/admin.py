from django.contrib import admin
from .models import GroceryList, GroceryItem, UserProfile

# Register your models here.

admin.site.register(GroceryList)
admin.site.register(GroceryItem)
admin.site.register(UserProfile)
