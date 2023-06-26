from django.contrib import admin
from .models import User, Store, Vehicle, Route, RouteDetail
# Register your models here.

admin.site.register(User)
admin.site.register(Store)
admin.site.register(Vehicle)
admin.site.register(Route)
admin.site.register(RouteDetail)
