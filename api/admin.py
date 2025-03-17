from django.contrib import admin

from api.models import (
    CustomUser,
    Medicine,
    Bill
)

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Medicine)
admin.site.register(Bill)


