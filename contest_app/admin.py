from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from contest_app.models import uploads, appiled_for, contests, users_data, sloka, quiz_question, quiz_an

class upload_admin_table(admin.TabularInline):
    model = uploads

class apply_admin_table(admin.TabularInline):
    model = appiled_for

class quiz_ans_table(admin.TabularInline):
    model = quiz_an

class DataAdmin(admin.ModelAdmin):
    search_fields=('mail_id', 'phone_num', 'id',)
    inlines = [
        apply_admin_table,
        upload_admin_table,
        quiz_ans_table
    ]

class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

admin.site.register(users_data, DataAdmin)
admin.site.register(contests)
admin.site.register(sloka, YourModelAdmin)
admin.site.register(quiz_question, YourModelAdmin)