from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(CDC_Board)
admin.site.register(CDC_Error)
admin.site.register(Coaching_Board)
admin.site.register(Coaching)
admin.site.register(CoachingFileMa)
admin.site.register(CDC_Notice)
admin.site.register(CDC_Comment)
admin.site.register(CDC_Comment_reply)