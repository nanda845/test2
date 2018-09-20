import hashlib
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
import string
from datetime import datetime

from serializers import CelebrityDetailsSerializer, BookingPriceSerializer, BookingCottageSerializer, BookingSerializer
from .models import Token, CelebrityDetails, CelebritySchedules, PublicSuggestions, Users, SocialMedias, BookingPrice, \
    BookingCottage, Category
from django.contrib.auth.models import User
from django.db import transaction
from push_notifications.models import GCMDevice
from django.db.models import Q
from threading import Thread
from django.core.mail import EmailMessage, send_mail
from django.template.loader import get_template
import datetime
from django.utils import timezone


@api_view(['POST'])
def login(request):

    mobile_number = request.data["mobile_number"]
    login_password = request.data["password"]

    encrypt = encrypt_password(login_password)

    try:
        user = User.objects.filter(username=mobile_number)
        if user:
            if user[0].is_active:
                if str(user[0].password) == encrypt:
                    profile = Users.objects.filter(mobile_number=mobile_number)
                    token_number = random_number()
                    token_object = token(token_number, profile[0])
                    return Response({'token_role': token_object.role, 'token_number': token_object.token},
                                    status=status.HTTP_200_OK)
                else:
                    return Response("Invalid Username or Password", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Account Blocked, please contact the customer service",
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            mess = "Mobile Number doesnt exist"
            return Response(mess, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def logout(request):
    try:
        token_number = Token.objects.get(token=request.META['HTTP_AUTHORIZATION'])
        token_number.delete()
        return Response('logged out', status=status.HTTP_200_OK)
    except KeyError as key:
        if key.message == 'HTTP_AUTHORIZATION':
            return Response("Session Expired", status=status.HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):

    try:
        reg = request.data
        with transaction.atomic():
            user = User()
            user.first_name = reg['full_name']
            user.last_name = ''
            user.username = reg['mobile_number']
            user.email = reg['email']
            user.password = encrypt_password(reg['password'])
            user.save()

            reg['user'] = user
            reg['role'] = "public"
            register_user = Users(**reg)
            register_user.save()

        return Response(status=status.HTTP_200_OK)
    except IntegrityError as e:
        print "************"
        if 'email' in e.args[0]:
            err = {'field': 'Email', 'value': reg['email']}
        elif 'username' in e.args[0]:
            err = {'field': 'Mobile Number', 'value': reg['mobile_number']}

        return Response(err, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


def encrypt_password(password):
    encrypt = hashlib.md5(password).hexdigest()
    return encrypt


def random_number():

    chars = string.ascii_uppercase + string.digits
    random_num = ''.join(random.choice(chars) for _ in range(50))

    check = Token.objects.filter(token=random_num)

    if check:
        random_number()

    return random_num


def token(token_number, profile):

    token_object = Token()
    token_object.token = token_number
    token_object.role = profile.role
    token_object.user = profile
    token_object.save()

    return token_object


def authentication(token_number):

    try:
        token_object = Token.objects.get(token=token_number)
        return token_object
    except Exception as e:
        print "######################################################"
        print "Invalid Token: " + token_number
        print e
        print "######################################################"
        return Response("Session Expired", status=status.HTTP_401_UNAUTHORIZED)

def authentication1(token_number):

    try:
        token_object = Token.objects.get(token=token_number)
        print token_object
        print token_object.user_id
        return token_object.user_id
    except Exception as e:
        print "######################################################"
        print "Invalid Token: " + token_number
        print e
        print "######################################################"
        return Response("Session Expired", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def upload_celebrity_details(request):
    try:
        temp = {}
        for data in request.data:
            temp[data] = request.data[data]

        celebrity = CelebrityDetails(**temp)
        celebrity.save()

        th = Thread(target=send_notifications, args=(celebrity.title, ))
        th.start()

        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def fetch_celebrity_details(request):
    try:
        language = request.data['language']
        page = request.data['page']
        details = CelebrityDetails.objects.filter(Q(language=language) | Q(language='all'), page=page).order_by('-id')
        details_value = details.values()

        if details:
            if details[0].image_path:
                for idx, detail in enumerate(details_value):
                        detail['image_path'] = details[idx].image_path.url

        return Response(details_value, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_celebrity_details(request):
    try:
        print "$$$$$$$$$$$$$$$$$$$$$$$$$", request.data
        id = request.data['id']
        celebrity = CelebrityDetails.objects.filter(id = id)
        temp = {}
        for data in request.data:
            temp[data] = request.data[data]

        serializer = CelebrityDetailsSerializer(celebrity[0], temp)
        if serializer.is_valid(Exception):
            serializer.save()

        # th = Thread(target=send_notifications, args=(serializer.title,))
        # th.start()

        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_celebrity_details(request):
    try:
        print "#################", request.data
        id = request.data['id']
        CelebrityDetails.objects.filter(id=id).delete()
        language = request.data['language']
        page = request.data['page']
        details = CelebrityDetails.objects.filter(Q(language=language) | Q(language='all'), page=page).order_by('-id')
        details_value = details.values()

        if details:
            if details[0].image_path:
                for idx, detail in enumerate(details_value):
                    detail['image_path'] = details[idx].image_path.url

        return Response(details_value, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_celebrity_video(request):
    try:
        print "#################", request.data
        id = request.data['id']
        CelebrityDetails.objects.filter(id=id).delete()
        return Response("successfully deleted", status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def upload_carousel_images(request):
    try:
        celebrity_details = CelebrityDetails()
        celebrity_details.image_path = request.FILES['image_path']
        celebrity_details.page = request.data['page']
        celebrity_details.save()

        return Response('Success', status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def fetch_carousel_images(request):
    try:
        details = CelebrityDetails.objects.filter(page='home').order_by('id')
        details_value = details.values('image_path','id')

        for idx, detail in enumerate(details_value):
            detail['image_path'] = details[idx].image_path.url
        return Response(details_value, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_image(request):
    try:
        image_id = request.data['id']
        CelebrityDetails.objects.filter(id=image_id).delete()
        details = CelebrityDetails.objects.filter(page='home')
        details_value = details.values('image_path','id')

        for idx, detail in enumerate(details_value):
            detail['image_path'] = details[idx].image_path.url

        return Response({'message':"Succefully deleted image", 'data':details_value}, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def save_celebrity_schedules(request):
    try:
        schedule = CelebritySchedules(**request.data)
        schedule.save()
        th = Thread(target=send_notifications, args=(schedule,))
        th.start()
        return Response("Success", status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def fetch_celebrity_schedules(request):
    try:
        language = request.data['language']
        print language, "-----------------------------------------------"
        print datetime.now(), "-------------------------------------------------"
        schedules = CelebritySchedules.objects.filter(Q(language=language) | Q(language='all'), at__gte= datetime.now()).values().order_by('at')
        return Response(schedules, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_schedule(request):
    try:
        print "****************", request.data
        id = request.data['id']
        CelebritySchedules.objects.filter(id=id).delete()
        return Response("successfully deleted", status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_public_suggestion(request):
    try:
        token_object = authentication(request.META['HTTP_AUTHORIZATION'])
        request.data['user'] = token_object.user
        suggestion = PublicSuggestions(**request.data)
        suggestion.save()
        return Response("Success", status=status.HTTP_200_OK)
    except KeyError as key:
        if key.message == 'HTTP_AUTHORIZATION':
            return Response("Session Expired", status=status.HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def publish_public_suggestions(request):
    try:
        suggestion_id = request.data['id']
        suggestion = PublicSuggestions.objects.get(id=suggestion_id)
        suggestion.publish = not suggestion.publish
        suggestion.save()
        return Response("Success", status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_public_suggestions(request):
    try:
        suggestions = PublicSuggestions.objects.filter().values('id', 'suggestion', 'at', 'publish', 'user__full_name').\
            order_by('at')

        return Response(suggestions, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_public_suggestions(request):
    try:
        suggestions = PublicSuggestions.objects.filter(publish=True).values('suggestion', 'at', 'user__full_name').\
            order_by('at')

        return Response(suggestions, status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_public_suggestion(request):
    try:
        print "****************", request.data
        id = request.data['id']
        PublicSuggestions.objects.filter(id=id).delete()
        return Response("successfully deleted", status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_mobile_token(request):
    try:
        request.data['active'] = True
        request.data['cloud_message_type'] = 'FCM'
        GCMDevice.objects.update_or_create(**request.data)

        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e

        return Response(status=status.HTTP_400_BAD_REQUEST)


def send_notifications(message):
    try:
        mobiles = GCMDevice.objects.all()
        mobiles.send_message(message)

    except Exception as e:
        print e


@api_view(['POST'])
def save_social_id(request):
    try:
        # social = SocialMedias(**request.data)
        # social.save()

        # SocialMedias.objects.filter(social=request.data['social']).update(social_id=request.data['social_id'])
        social = SocialMedias.objects.filter(social=request.data['social'])
        if social:
            social.update(social_id=request.data['social_id'])
        else:
            socialid = SocialMedias(**request.data)
            socialid.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def fetch_social_id(request):
    try:
        social = SocialMedias.objects.filter(social=request.data['social']).values()
        return Response(social, status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_login(request):
    try:
        token_number = request.data['token']
        role = Token.objects.filter(token=token_number).values('role')

        return Response(role, status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def change_password(request):
    if request.data['flag'] == 1:
        print "yes"
        print "flag 0"
        username = request.data['mobile_number']
        print "password username is", username
        confirm_password = request.data['newPassword']
        encrypt_confirm = hashlib.md5(confirm_password).hexdigest()
        print 'encrypted confirm_password', encrypt_confirm
        login_obj = User.objects.get(username=username)
        if login_obj.password == encrypt_confirm:
            data = {"message": "same password already exists", "status": 100}
        else:
            login_obj.password = encrypt_confirm
            login_obj.save()
            Users.objects.filter(mobile_number=username).update(password=confirm_password)
            data = {"message": "password changed", "status": 200}

    elif request.data['flag'] == 2:
        print "no"
        gettoken = Token.objects.filter(token=request.META['HTTP_AUTHORIZATION'])
        print gettoken
        if gettoken:
            current_password = request.data['password']
            encrypt_current = hashlib.md5(current_password).hexdigest()
            print 'encrypted current_password', encrypt_current
            confirm_password = request.data['newPassword']
            encrypt_confirm = hashlib.md5(confirm_password).hexdigest()
            print 'encrypted confirm_password', encrypt_confirm
            login_obj = Users.objects.filter(id=gettoken[0].user_id)
            # print login_obj[0].password, "hi old one"
            # print encrypt_current, "hi new one"
            gotoauthuser = User.objects.get(username = login_obj[0].mobile_number)
            if gotoauthuser.password == encrypt_confirm:
                data = {"message": "same password already exists", "status": 100}
            else:
                Users.objects.filter(id=gettoken[0].user_id).update(password=confirm_password)
                loginnewobj = User.objects.get(username=login_obj[0].mobile_number)
                loginnewobj.password = encrypt_confirm
                loginnewobj.save()
                data = {"message": "password changed", "status": 200}
        else:
            data = {"message": "no get token"}

    else:
        data = {"message":"no flag"}
    return Response(data, status=status.HTTP_200_OK)



@api_view(['POST'])
def mail_confirmation(request):
    print "aaaaaaaaaaaaaa"
    getmail = request.body
    print "mail is",getmail
    user_profile = User.objects.get(email = getmail)
    print "..........................", user_profile
    print "profile mail is", user_profile.email
    print "profile id is", user_profile.username
    login_encrypt_id = User.objects.get(username = user_profile.username)
    print "login id is", login_encrypt_id.username
    # print "login_encrypt_id is", login_encrypt_id.referencesmartid
    send_mail(
    'GCELEBRITY PASSWORD CHANGE',
        get_template('email_template.html').render(
            dict({
                'Link':'http://127.0.0.1:8000/static/Kurinji_frontend/index.html#/setPassword/'+login_encrypt_id.username,
                'Username': user_profile.first_name
            })
        ),

    'gcelebrity.gowdanar@gmail.com',
    [getmail],
    fail_silently=False,
    )
    data = {"message": "SUCCESSFULLY LINK HAS SENT TO YOUR MAIL, PLEASE CHECK IT", "status": 200}
    return Response(data)

@api_view(['POST'])
def checkcurrentpassword(request):
    token = request.META['HTTP_AUTHORIZATION']
    finduser = Token.objects.filter(token = token)
    print "user is", finduser[0].user_id
    founduser = Users.objects.filter(id = finduser[0].user_id)
    print founduser[0].mobile_number, "mobilenumber.........................."
    print request.data, "current password.................................."
    encrypt_current = hashlib.md5(request.data['currentpassword']).hexdigest()
    checkpwd = User.objects.filter(username = founduser[0].mobile_number, password = encrypt_current)
    if checkpwd:
        print "YES"
        data = {"status": 200}
    else:
        print "NO"
        data = {"status": 400}
    return Response(data)


@api_view(['POST'])
def message_notification(request):
    try:
        notification_message = request.data
        print notification_message
        send_notifications(notification_message['n_message'])
        return Response("Success", status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def set_default_price(request):
    request.data['startdate'] = datetime.date.today()
    request.data['enddate'] = datetime.date.max
    default = BookingPrice.objects.filter(enddate = request.data['enddate'])
    if default:
        default.update(price = request.data['price'])
    else:	
    	profile = BookingPrice(**request.data)
    	profile.save()
    return Response("successfully Updated")

@api_view(['POST'])
def set_custom_price(request):
    # request.data['status'] = True
    # profile = BookingPrice(**request.data)
    # profile.save()
    # return Response("successfully Updated")
    try:
        block_strt_date = request.data['startdate']
        block_end_date = request.data['enddate']
        block_date_form = datetime.datetime.strptime(block_strt_date, '%Y-%m-%d')
        block_end_date_form = datetime.datetime.strptime(block_end_date, '%Y-%m-%d')
        block = BookingPrice.objects.filter(status=True)
        delta = block_end_date_form - block_date_form
        for i in range(delta.days):
            next_date = block_date_form + timedelta(days=i+1)
            blocked_records = block.filter(startdate__lte=next_date, enddate__gte=next_date)
            if not blocked_records:
                print "setting custom price"
                request.data['status'] = True
                block = BookingPrice(**request.data)
                block.save()
                return Response(status=status.HTTP_200_OK)
            else:
                print "not available"
                message = "Dates Unavailable"
                return Response(message, status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


from datetime import timedelta
@api_view(['POST'])
def search_dates(request):
    client_id = authentication1(request.META['HTTP_AUTHORIZATION'])
    lists = []
    book_strt_date = request.data['startdate']
    booked_end_date = request.data['enddate']
    book_date_form = datetime.datetime.strptime(book_strt_date, '%Y-%m-%d')
    booked_end_date_form = datetime.datetime.strptime(booked_end_date, '%Y-%m-%d')
    booking_rec1 = BookingPrice.objects.exclude(enddate=datetime.date.max)
    booking_rec2 = BookingCottage.objects.all()
    print booking_rec2
    delta = booked_end_date_form - book_date_form
    for i in range(delta.days):
        next_date = book_date_form + timedelta(days=i)
        print "inside for"
        booking_check = booking_rec2.filter(startdate__lte=next_date, enddate__gt=next_date)
        print booking_check
        if not booking_check:
            booking_records = booking_rec1.filter(startdate__lte=next_date, enddate__gte=next_date).first()
            print "inside first if"
            if booking_records is not None:
                lists.append(booking_records.price)
                print "inside second if"
            else:
                print "inside else"
                max_date_record = BookingPrice.objects.filter(enddate=datetime.date.max).first()
                lists.append(max_date_record.price)

            roomprice= sum(lists)
            gst = (roomprice*18)/100
            ccavenue = (roomprice*2)/100
            totalprice = gst+roomprice+ccavenue
            nights = delta.days
            data = {'gst':gst,'roomprice':roomprice,'totalprice':totalprice,'nights':nights,'ccavenue':ccavenue}
            print data
        else:
            print "unavailable"
            data = "Dates UnAvailable"
            return Response(data,status=status.HTTP_200_OK)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def show_prices(request):
    today_date = datetime.date.today()
    pricetable = BookingPrice.objects.filter(status = True, enddate__gte = today_date).order_by('startdate')
    defaultprice = BookingPrice.objects.filter(status = False)
    serializable_obj = BookingPriceSerializer(pricetable,many=True)
    serializable_obj1 = BookingPriceSerializer(defaultprice,many=True)
    data = {'serializable_obj1':serializable_obj1.data,'serializable_obj':serializable_obj.data}
    return Response(data,status=status.HTTP_200_OK)

@api_view(['POST'])
def book_Now(request):
    client_id = authentication1(request.META['HTTP_AUTHORIZATION'])
    lists = []
    book_strt_date = request.data['startdate']
    booked_end_date = request.data['enddate']
    book_date_form = datetime.datetime.strptime(book_strt_date, '%Y-%m-%d')
    booked_end_date_form = datetime.datetime.strptime(booked_end_date, '%Y-%m-%d')
    book = BookingCottage.objects.all()

    delta = booked_end_date_form - book_date_form
    for i in range(delta.days):
        next_date = book_date_form + timedelta(days=i)
        # pdb.set_trace()
        booking_records = book.filter(startdate__lte=next_date, enddate__gte=next_date)
        if not booking_records:
            print "available"
            book = BookingCottage()
            book.client_id = client_id
            book.startdate = book_date_form
            book.enddate = booked_end_date_form
            book.status = 'booked'
            book.save()
            return Response("available", status=status.HTTP_200_OK)
        else:
            print "not available"
            message = "Dates Unavailable"
            return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
def bookingdetails(request):
    print "booking details", request.data
    client_id = authentication1(request.META['HTTP_AUTHORIZATION'])
    lists = []
    book_strt_date = request.data['startdate']
    booked_end_date = request.data['enddate']
    book_date_form = datetime.datetime.strptime(book_strt_date, '%Y-%m-%d')
    booked_end_date_form = datetime.datetime.strptime(booked_end_date, '%Y-%m-%d')
    book = BookingCottage.objects.all()

    delta = booked_end_date_form - book_date_form
    for i in range(delta.days):
        next_date = book_date_form + timedelta(days=i)
        # pdb.set_trace()
        booking_records = book.filter(startdate__lte=next_date, enddate__gte=next_date)
        if not booking_records:
            print "available"
            request.data['status'] = 'booked'
            request.data['client_id'] = client_id
            request.data['paymentstatus'] = 'paid'
            book = BookingCottage(**request.data)
            # book.client_id = client_id
            # book.startdate = book_date_form
            # book.enddate = booked_end_date_form
            # book.status = 'booked'
            book.save()
            return Response("available", status=status.HTTP_200_OK)
        else:
            print "not available"
            message = "Dates Unavailable"
            return Response(message, status=status.HTTP_200_OK)



@api_view(['POST'])
def updateCustomPrice(request):
    try:
        id = request.data['id']
        customprice = BookingPrice.objects.filter(id = id)
        if customprice:
            customprice.update(startdate=request.data['startdate'], enddate=request.data['enddate'], price=request.data['price'])
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def deletePrice(request):
    try:
        id = request.data['id']
        deleteprice = BookingPrice.objects.filter(id = id).delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def blockDates(request):
    try:
        print "block dates", request.data
        client_id = authentication1(request.META['HTTP_AUTHORIZATION'])
        print "after client id"
        block_strt_date = request.data['startdate']
        block_end_date = request.data['enddate']
        block_date_form = datetime.datetime.strptime(block_strt_date, '%Y-%m-%d')
        block_end_date_form = datetime.datetime.strptime(block_end_date, '%Y-%m-%d')
        block = BookingCottage.objects.all()
        delta = block_end_date_form - block_date_form
        for i in range(delta.days):
            next_date = block_date_form + timedelta(days=i+1)
            # pdb.set_trace()
            blocked_records = block.filter(startdate__lte=next_date, enddate__gte=next_date)
            if not blocked_records:
                print "blocking"
                block = BookingCottage()
                block.client_id = client_id
                block.startdate = block_strt_date
                block.enddate = block_end_date
                block.status = 'blocked'
                block.save()
                return Response(status=status.HTTP_200_OK)
            else:
                print "not available"
                message = "Dates Unavailable"
                return Response(message, status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def blockeddates(request):
    blocked = BookingCottage.objects.filter(status = 'blocked').order_by('startdate')
    serializable_obj = BookingCottageSerializer(blocked,many=True)
    data = {'serializable_obj':serializable_obj.data}
    return Response(data,status=status.HTTP_200_OK)


@api_view(['POST'])
def deleteblockeddates(request):
    try:
        id = request.data['id']
        deleteblocked = BookingCottage.objects.filter(id = id).delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print e
        return Response(status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def getcurrentuserdetails(request):
#     try:
#         client_id = authentication1(request.META['HTTP_AUTHORIZATION'])
#         detail = Users.objects.filter(user_id=client_id)
#         if detail:


@api_view(['POST'])
def getbookings(request):
    print "data", request.data
    gettoken = request.META['HTTP_AUTHORIZATION']
    print "token at get bookings", gettoken
    fromtokentable = Token.objects.get(token=gettoken)
    fromuserstable = Users.objects.get(id=fromtokentable.user_id)
    print "after token", request.data
    min = request.data['min']
    max = request.data['max']
    print "after min max"
    list = []
    filterindividualrecord = BookingCottage.objects.filter(status='booked',
                                                       client_id = fromtokentable.user_id).order_by('id')[min:max]
    filterrecord = BookingCottage.objects.filter(status='booked').order_by('id')[min:max]
    count = BookingCottage.objects.filter(status='booked').count()
    individualcount = BookingCottage.objects.filter(status='booked', client_id = fromtokentable.user_id).count()
    print "before condition"
    if fromuserstable.role == 'admin':
        for i in filterrecord:
            serializer = BookingSerializer(i)
            fullserializer = serializer.data
            fullserializer.update({'role': 'admin'})
            fullserializer.update({'totalcount': count})
            list.append(fullserializer)
    elif fromuserstable.role == 'public':
        for i in filterindividualrecord:
            serializer = BookingSerializer(i)
            fullserializer = serializer.data
            fullserializer.update({'role': 'public'})
            fullserializer.update({'totalcount': individualcount})
            list.append(fullserializer)
    data = {"bookings": list}
    return Response(data)


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


@api_view(['GET'])
def getDates(request):
    cottagetable = BookingCottage.objects.all()
    list = []
    if cottagetable:
        for i in cottagetable:
            if i.status=='booked':
                d1 = i.startdate
                d2 = i.enddate - timedelta(days=1)
                for dt in daterange(d1, d2):
                    list.append(dt)
                    print (dt)
            elif i.status == 'blocked':
                d1 = i.startdate
                d2 = i.enddate
                for dt in daterange(d1, d2):
                    list.append(dt)
                    print (dt)
    data = {"dates": list}
    return Response(data)


@api_view(['GET'])
def getDates2(request):
    cottagetable = BookingCottage.objects.all()
    list = []
    if cottagetable:
        for i in cottagetable:
            if i.status=='booked':
                d1 = i.startdate + timedelta(days=1)
                d2 = i.enddate
                for dt in daterange(d1, d2):
                    list.append(dt)
                    print (dt)
            elif i.status=='blocked':
                d1 = i.startdate
                d2 = i.enddate
                for dt in daterange(d1, d2):
                    list.append(dt.strftime("%Y-%m-%d"))
                    print (dt.strftime("%Y-%m-%d"))
    data = {"dates": list}
    return Response(data)


@api_view(['GET'])
def getcategory(request):
    cat=Category.objects.all()
    li=[]
    if cat:
        for i in cat:
            li.append(i.type)
    return Response({'data':li})


@api_view(['POST'])
def savecategory(request):
    print "category----------------------------",request.data
    cat=Category()
    cat.type=request.data['type']
    cat.save()
    return Response({'data':'success'})