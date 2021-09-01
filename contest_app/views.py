
from django.core import serializers
from django.db.models.query import QuerySet
from django.http.response import Http404
from django.shortcuts import redirect, render, HttpResponse
from django.views.decorators import csrf
import razorpay
import random
import json
import os
from django.forms.models import model_to_dict
import uuid
from contest_app import models
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email import encoders
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from threading import Thread
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
path = os.path.abspath('.')
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    path+'/static/creds.json', scope)


@csrf_exempt
def quiz_answers(request, user_id):
    try:
        user = models.users_data.objects.get(id=user_id)
        for i in json.loads(request.POST['ans']):
            if i != '':
                q = models.quiz_question.objects.get(id=i[0])
                models.quiz_an.objects.create(i_id=user, question=q,
                                              answer_given=i[1], correct_answer=q.answer)
        app = models.appiled_for.objects.get(i_id=user)
        app.uploaded = True
        app.save()
        return HttpResponse("success")
    except Exception as e:
        return HttpResponse("error")


def send_mail(receiver_address, contests, name, url):
    contests = contests.split(',')
    imgs = ['contests.pdf']
    for i in contests:
        if i != '':
            img = i.replace(' ', '_')
            imgs.append(img+".pdf")
    mail_content = '<div style="font-size: 1.2rem">Hi <b>{name}</b>,<Br><Br>Thank you for your registration.<br><Br>Your unique URL : <b><Br><a href="https://contest.upgrace.in/uploads/{url}">https://contest.upgrace.in/uploads/{url}</a></b><Br><Br>Please keep your User ID Safe.<br><Br>Best regards,<br><b>Prabhupada Anugas</b><Br><Br>Connect with us : <br><br><a href="https://www.youtube.com/channel/UC0G2Sep-8nqqz3xPZnazCOQ"><img style="width: 50px;" src="https://contest.upgrace.in/static/youtube.png"></a>&nbsp;&nbsp;&nbsp;<a href="https://www.facebook.com/sribaladev"><img style="width: 50px;" src="https://contest.upgrace.in/static/facebook.png"></a>&nbsp;&nbsp;&nbsp;<a href="https://www.instagram.com/prabhupada_anugas/"><img style="width: 50px;" src="https://contest.upgrace.in/static/instagram.png"></a></div>'.format(
        name=name, url=url)

    sender_address = 'upgrace.in@gmail.com'
    sender_pass = '(Hari@47)'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Prabhupada Anugas - Online Janmashtami Contest'
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))

    for f in imgs:
        with open(path+"/static/pdfs/"+f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(path+"/static/pdfs/"+f)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(
            path+"/static/pdfs/"+f)
        message.attach(part)

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')


def contest_updation(request, mdl):
    contests_id = json.loads(request.POST['contest_id'])
    con = ''
    for i in contests_id:
        mdl_con = models.contests.objects.get(id=i)
        models.appiled_for.objects.create(
            i_id=mdl, contest_mdl=mdl_con)
        con = con + mdl_con.contest_name + ','
    return con


def sheet_updation(hash, name, mail_id, phone_num, contests, order_id):
    client = gspread.authorize(credentials)
    sheet = client.open("online").sheet1
    sheet.append_row([hash, name, mail_id, phone_num, contests, order_id])


@csrf_exempt
def verify_payment(request):
    try:
        razorpay_order_id = request.POST['razorpay_order_id']
        razorpay_payment_id = request.POST['razorpay_payment_id']
        razorpay_signature = request.POST['razorpay_signature']

        client = razorpay.Client(
            auth=("rzp_live_GTQXloyqzNvF11", "GRuslqA9mI5naGz6vCA23z8O"))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        c = client.utility.verify_payment_signature(params_dict)
        if c is None:

            mdl = models.users_data.objects.create(id=str(uuid.uuid1()).replace('-', ''),
                                                   name=request.POST['name'], mail_id=request.POST['mail_id'], phone_num=request.POST[
                'phone_num'], razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id, razorpay_signature=razorpay_signature)

            c = contest_updation(request, mdl)

            thread = Thread(target=send_mail, args=(
                request.POST['mail_id'], c, request.POST['name'], mdl.id))
            thread.start()

            thread1 = Thread(target=sheet_updation, args=(mdl.id, request.POST['name'], request.POST['mail_id'],
                                                          request.POST['phone_num'], c, razorpay_order_id))
            thread1.start()

            context = {
                'result': 'success',
                'id': mdl.id
            }
        else:
            context = {
                'result': 'verify_failed'
            }
    except Exception as e:
        context = {
            'result': 'errror'
        }
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')


def create_an_order(request):
    if request.method == 'POST':
        fees = 0
        contests_id = json.loads(request.POST['contest_id'])
        for i in contests_id:
            mdl = models.contests.objects.get(id=i)
            fees = mdl.fees + fees
        client = razorpay.Client(
            auth=("rzp_live_GTQXloyqzNvF11", "GRuslqA9mI5naGz6vCA23z8O"))
        order_currency = 'INR'
        order_receipt = 'ord_rcpt'+str(random.randint(0, 100000))
        c = client.order.create(dict(amount=int(str(fees)+"00"),
                                currency=order_currency, receipt=order_receipt))
        context = {
            'order': c
        }
        data = json.dumps(context, indent=4, sort_keys=True, default=str)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponse("Method Not Allowed")


def register(request):
    try:
        if request.method == 'POST':
            mdl = models.users_data.objects.create(id=str(uuid.uuid1()).replace('-', ''),
                                                   name=request.POST['name'], mail_id=request.POST['mail_id'], phone_num=request.POST['phone_num'])
            c = contest_updation(request, mdl)

            thread = Thread(target=send_mail, args=(
                request.POST['mail_id'], c, request.POST['name'], mdl.id))
            thread.start()

            thread1 = Thread(target=sheet_updation, args=(mdl.id, request.POST['name'], request.POST['mail_id'],
                                                          request.POST['phone_num'], c, 'None'))
            thread1.start()

            context = {
                'result': 'success',
                'id': mdl.id
            }
        else:
            context = {
                'result': 'Method not allowed'
            }
    except Exception as e:
        context = {
            'result': 'Error'
        }
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')


def manual_register():
    import csv

    path = os.path.join('.')
    file = path+'/static/online.csv'
    lg = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                print(row[0])
                mdl = models.users_data.objects.create(
                    id=row[0], name=row[1], mail_id=row[2], phone_num=row[3])
                contests = row[4].split(',')
                for i in contests:
                    if i != '':
                        mdl_con = models.contests.objects.get(contest_name=i)
                        models.appiled_for.objects.create(
                            i_id=mdl, contest_mdl=mdl_con)

    print("Done")


def uploads(request, user_id):
    if request.method == 'POST':
        try:
            m = models.users_data.objects.filter(id=user_id)
            con = models.contests.objects.filter(
                contest_name=request.POST['contest_name'])
            num_of_uploads = request.POST['num_of_uploads']
            files = []
            if num_of_uploads == "2":
                file_1 = request.FILES['file1']
                file_2 = request.FILES['file2']
                files.append([file_1, file_2])
            elif num_of_uploads == "3":
                file1 = request.FILES['file1']
                file2 = request.FILES['file2']
                file3 = request.FILES['file3']
                files.append([file1, file2, file3])
            else:
                file01 = request.FILES['file1']
                files.append([file01])
            for i in files[0]:
                i._name = str(uuid.uuid1()) + "." + i._name.split('.')[1]
                mdl = models.uploads.objects.create(
                    i_id=m[0], contest_name=con[0], file_name=i)
            # Uploaded true
            app = models.appiled_for.objects.get(i_id=m[0], contest_mdl=con[0])
            app.uploaded = True
            app.save()
            return redirect('/uploads/'+user_id)
        except Exception as e:
            return HttpResponse('Please contact us some unknown error has occured. <br> Error : ' + e)
    else:
        try:
            m = models.users_data.objects.filter(id=user_id)
            mdl = models.appiled_for.objects.filter(i_id=m[0])
            context = {
                "data": mdl
            }
            return render(request, 'upload_page.html', context)
        except Exception as e:
            return HttpResponse('Please contact us some unknown error has occured. <br> Error : ' + e)




def quiz_questions(request):
    qq = models.quiz_question.objects.all()
    data = serializers.serialize("json", qq)
    data = json.dumps(data, indent=4, sort_keys=True, default=str)
    return HttpResponse(data, content_type='application/json')


def quiz(request, user_id):
    try:
        mdl = models.users_data.objects.get(id=user_id)
        con = models.contests.objects.get(contest_name="Quiz")
        m = models.appiled_for.objects.get(i_id=mdl, contest_mdl=con)
        if m.uploaded == True:
            return HttpResponse("Winners list will be released on 2nd Sep")
        else:
            return render(request, 'quiz.html')
    except Exception as e:
        return HttpResponse("You are not registered for this event.")

###### QUIZ SCORE FINDING
def quiz_sheet_updation(hash, name, email, score):
    client = gspread.authorize(credentials)
    sheet = client.open("online").get_worksheet(1)
    # https://docs.google.com/spreadsheets/d/1PZZa6C1sNrkxmytl5q4epRr0V9R7lqvdIIPR8NFMku4/edit?usp=sharing
    sheet.append_row([hash, name, email, score])

def find_score(ans_list):
    score = 0
    for i in ans_list:
        question_mdl = models.quiz_question.objects.get(id=i.question.id)
        if i.answer_given == question_mdl.answer:
            score += 1
    return score

def match_answers(request):
    quiz_contest = models.contests.objects.get(contest_name='Quiz')
    participators = models.appiled_for.objects.filter(contest_mdl=quiz_contest)

    for i in participators:
        answers_list = models.quiz_an.objects.filter(i_id=i.i_id)
        sc = find_score(answers_list)
        quiz_sheet_updation(i.i_id.id, i.i_id.name, i.i_id.mail_id, sc)
    return HttpResponse("Database Updated")
###### QUIZ SCORE FINDING

@csrf_exempt
def judging_page(request):
    if request.method == 'POST':
        contest_name = request.POST['contest_name']
        # contest_name = contest_name.replace('_', ' ')
        con = models.contests.objects.get(contest_name=contest_name)
        m = models.uploads.objects.filter(contest_name=con)
        data = serializers.serialize("json", m)
        data = json.dumps(data, indent=4, sort_keys=True, default=str)
        return HttpResponse(data, content_type='application/json')
    else:
        mdl = models.contests.objects.all()
        return render(request, 'judging_page.html', {'contests': mdl})


def sloka(request):
    sl = models.sloka.objects.all()
    return render(request, 'sloka.html', {'data': sl})


def admin_register(request):
    mdl = models.contests.objects.all()
    return render(request, 'registration.html', {'contests': mdl})


def index(request):
    mdl = models.contests.objects.all()
    return render(request, 'index.html', {'contests': mdl})
