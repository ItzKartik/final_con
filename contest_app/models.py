from django.db import models
from django.db.models.base import ModelStateFieldsCacheDescriptor
from django.db.models.fields import CharField
from django.utils.translation import TranslatorCommentWarning
import uuid 

class contests(models.Model):
    contest_name = models.CharField(max_length=100)
    coordinator_name = models.CharField(max_length=100)
    coordinator_phone = models.IntegerField()
    fees = models.IntegerField()
    pdf = models.FileField(upload_to='static/pdfs')

    def __str__(self):
        return self.contest_name

class users_data(models.Model):
    id = models.CharField(primary_key=True, max_length=1000)
    name = models.CharField(max_length=100)
    mail_id = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=1000, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=1000, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.mail_id

class appiled_for(models.Model):
    i_id = models.ForeignKey(users_data, on_delete=models.CASCADE)
    contest_mdl = models.ForeignKey(contests, on_delete=models.DO_NOTHING)
    uploaded = models.BooleanField(default=False)

class uploads(models.Model):
    i_id = models.ForeignKey(users_data, on_delete=models.CASCADE)
    contest_name = models.ForeignKey(contests, on_delete=models.DO_NOTHING)
    file_name = models.FileField(upload_to='static/uploads')

class sloka(models.Model):
    eng_text = models.TextField(max_length=1000)
    eng_audio = models.TextField(max_length=1000)
    hin_text = models.TextField(max_length=1000)
    hin_audio = models.TextField(max_length=1000)

    def __str__(self):
        return self.eng_text

class quiz_question(models.Model):
    eng_question = models.TextField(max_length=5000)
    hin_question = models.TextField(max_length=5000)
    answer  = models.TextField(max_length=2000, null=True, blank=True)
    option1 = models.TextField(max_length=2000, null=True, blank=True)
    option2 = models.TextField(max_length=2000, null=True, blank=True)
    option3 = models.TextField(max_length=2000, null=True, blank=True)
    option4 = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.eng_question

class quiz_an(models.Model):
    i_id = models.ForeignKey(users_data, on_delete=models.CASCADE)
    question = models.ForeignKey(quiz_question, on_delete=models.CASCADE)
    answer_given = models.TextField(max_length=2000)
    correct_answer = models.TextField(max_length=2000, null=True, blank=True)

