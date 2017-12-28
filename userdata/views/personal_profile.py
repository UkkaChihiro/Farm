# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.contrib.sessions.models import Session
from django.contrib.auth import login, password_validation

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from datetime import datetime

from core.models import CountryNumberphone, Language
from core.tools import token_renew, avatar_personal_upload
from userdata.models import ClassProductForProfile
from catalog.models import GroupForProfile, CategoryForProfile, SubcategoryForProfile, TypeProductForProfile, Category, \
    Group

from rest_framework.status import HTTP_200_OK


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dashboard_personal(request):
    user = request.user

    try:
        birthday = user.profile.birthday.strftime('%Y-%m-%d')#.strftime('%d.%m.%Y')
    except AttributeError:
        birthday = False

    if user.profile.avatar and hasattr(user.profile.avatar, 'url'):
        avatar = user.profile.avatar.url
    else:
        avatar = None

    try:
        password_updated = user.profile.password_updated.strftime('%Y-%m-%d')#.strftime('%d.%m.%Y')
    except AttributeError:
        user.profile.password_updated = user.date_joined
        user.profile.save()
        password_updated = user.profile.password_updated.strftime('%Y-%m-%d')#.strftime('%d.%m.%Y')

    out_vars = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.profile.middle_name,
        "gender": user.profile.gender,  # (1, 'not set'),(2, 'male'),(3, 'female'),
        "birthday": birthday,
        "language": user.profile.language.id,
        "avatar": avatar,
        "email": user.email,
        "confirmed_email": user.profile.confirmed_email,
        "code_number_phone": user.profile.code_num_phone.id if user.profile.code_num_phone else False,
        "code_phone_value": '+%s' % user.profile.code_num_phone.code if user.profile.code_num_phone else '',
        "number_phone": user.profile.number_phone,
        "password_updated": password_updated,
        "addition_receiver": user.profile.addition_receiver if user.profile.addition_receiver else '',
        "receiver_phonenumber": user.profile.receiver_phonenumber if user.profile.receiver_phonenumber else '',
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_password(request):
    """
    :param request:
    {
        "old_password": "",
        "new_password": {"first": "", "second": ""}
    }
    :return: {"token": token}
    """
    user = request.user
    old_password = request.data.get("old_password", False)
    new_password = request.data.get("new_password", False)

    if not old_password or not new_password:
        return Response({'error': 'Empty passwords'}, status=400)
    if type(old_password) != str:
        return Response({'error': 'Incorrect type old_password (need str)'}, status=400)
    if type(new_password) != dict:
        return Response({'error': 'Incorrect type new_password (need dict)'}, status=400)
    if not user.check_password(old_password):
        return Response({'error': 'Wrong old password'}, status=400)

    new_password_f = new_password.get("first", False)
    new_password_s = new_password.get("second", False)

    if not new_password_f or not new_password_s:
        return Response({'error': 'Empty one of new passwords'}, status=400)
    if new_password_f != new_password_s:
        return Response({'error': 'New passwords are different'}, status=400)
    if type(new_password_f) != str:
        return Response({'error': 'Incorrect type passwords in new_password (need str)'}, status=400)

    try:
        password_validation.validate_password(new_password_f)
    except ValidationError as e:
        return Response({'error': e}, status=400)

    user.set_password(new_password_f)
    user.save()

    user.profile.password_updated = datetime.now()
    user.profile.save()

    [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(user.id)]

    token = token_renew(user)

    login(request, user)

    return Response({"token": token})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def set_numberphone(request):
    """
    :param request: {"code_id": int, "numberphone": int}
    :return:
    {'status': 'Numberphone deleted'}
    {'status': 'Saved new numberphone'}
    """
    profile = request.user.profile
    code_id = request.data.get('code_id', False)
    num = request.data.get('numberphone', False)

    if not code_id or not num:
        profile.code_num_phone = None
        profile.number_phone = None
        profile.confirmed_phone = False
        profile.save()

        return Response({'status': 'Numberphone deleted'})

    if code_id and num:
        try:
            code = CountryNumberphone.objects.get(id=code_id)
        except CountryNumberphone.DoesNotExist:
            return Response({'error': 'incorrect code id'}, status=400)
        profile.code_num_phone= code
        profile.number_phone = int(num)
        profile.confirmed_phone = False
        profile.save()

        return Response({'status': 'Saved new numberphone'})


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_personal_notifications(request):
    profile = request.user.profile

    out_vars = {
        'personal_offers_email': profile.personal_offers_email,
        'newsletter_email': profile.newsletter_email,
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def set_personal_notifications(request):
    """
    :param request:
    {
        "personal_offers_email": false,
        "newsletter_email": false
    }
    :return:
    """
    profile = request.user.profile

    personal_offers_email = request.data.get('personal_offers_email', False)
    newsletter_email = request.data.get('newsletter_email', False)

    profile.personal_offers_email = personal_offers_email
    profile.newsletter_email = newsletter_email

    profile.save()

    out_vars = {
        'personal_offers_email': personal_offers_email,
        'newsletter_email': newsletter_email,
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def update_profile_global_filter(request):
    """
    :param request:
    {
        "class_list": [1, 3, 8]
    }
    :return:
        status 200
    """
    profile = request.user.profile
    profile_filters = request.data.get('class_list')

    correct = []
    incorrect = []

    classes = [c[0] for c in ClassProductForProfile.CLASS_PROD]
    for c in profile_filters:
        correct.append(c) if c in classes else incorrect.append(c)

    ClassProductForProfile.objects.filter(profile=profile).delete()
    for c in correct:
        ClassProductForProfile.objects.create(
            name=c,
            profile=profile
        )

    msg = '.'
    if incorrect:
        msg = ', except: {0}.'.format(incorrect)
    return Response({'answer': 'Classes added for profile: {0}{1}'.format(correct, msg)})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_group_product(request):
    """
    :param request:
    {
        "group": 1
    }
    :return:
    """
    profile = request.user.profile
    group = request.data.get('group')

    g, create = GroupForProfile.objects.get_or_create(profile=profile, group_id=group)
    g.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def delete_profile_group_product(request):
    """
    :param request:
    {
        "group": 1
    }
    :return:
    """
    profile = request.user.profile
    group = request.data.get('group')

    g = GroupForProfile.objects.filter(profile=profile, group_id=group)
    g.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_category_product(request):
    """
    :param request:
    {
        "category": 1
    }
    :return:
    """
    profile = request.user.profile
    category = request.data.get('category')

    g, create = CategoryForProfile.objects.get_or_create(profile=profile, category_id=category)
    g.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def delete_profile_category_product(request):
    """
    :param request:
    {
        "category": 1
    }
    :return:
    """
    profile = request.user.profile
    category = request.data.get('category')

    g = CategoryForProfile.objects.filter(profile=profile, category_id=category)
    g.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_subcategory_product(request):
    """
    :param request:
    {
        "subcategory": 1
    }
    :return:
    """
    profile = request.user.profile
    subcategory = request.data.get('subcategory')

    g, create = SubcategoryForProfile.objects.get_or_create(profile=profile, subcategory_id=subcategory)
    g.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def delete_profile_subcategory_product(request):
    """
    :param request:
    {
        "subcategory": 1
    }
    :return:
    """
    profile = request.user.profile
    subcategory = request.data.get('subcategory')

    g = SubcategoryForProfile.objects.filter(profile=profile, subcategory_id=subcategory)
    g.delete()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_personal_profile(request):
    """
    :param request:
    {
        "first_name": "",
        "last_name": "",
        "middle_name": "",
        "gender": 1,
        "birthday": "09.10.1967",
        "addition_receiver": "",
        "receiver_phonenumber": ""
    }
    :return:
    """
    user = request.user
    first_name = request.data.get("first_name", False)
    last_name = request.data.get("last_name", False)
    middle_name = request.data.get("middle_name", False)
    gender = request.data.get("gender", False)
    birthday = request.data.get("birthday", False)
    addition_receiver = request.data.get("addition_receiver", False)
    receiver_phonenumber = request.data.get("receiver_phonenumber", False)

    if not first_name:
        return Response({'error': 'Empty first name'}, status=400)
    if type(first_name) != str:
        return Response({'error': 'Incorrect type first_name (need str)'}, status=400)
    if not last_name:
        return Response({'error': 'Empty last name'}, status=400)
    if type(last_name) != str:
        return Response({'error': 'Incorrect type last_name (need str)'}, status=400)

    user.first_name = first_name
    user.last_name = last_name
    user.save()

    try:
        gender = int(gender)
    except ValueError:
        return Response({'error': 'Incorrect type gender (need int)'}, status=400)

    if gender not in [1, 2, 3]:
        gender = 1

    if birthday:
        try:
            birthday = datetime.strptime(birthday, '%Y-%m-%d')#, '%d.%m.%Y')
        except ValueError:
            return Response({'error': 'Incorrect birthday format'}, status=400)
        else:
            user.profile.birthday = birthday

    user.profile.gender = gender
    if middle_name and type(middle_name) != str:
        return Response({'error': 'Incorrect type middle_name (need str)'}, status=400)
    user.profile.middle_name = middle_name

    user.profile.save()

    out_vars = {
        'first_name': first_name,
        'last_name': last_name,
        'middle_name': middle_name,
        'gender': gender,
        'birthday': birthday,
        'addition_receiver': addition_receiver,
        'receiver_phonenumber': receiver_phonenumber
    }

    return Response(out_vars)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_personal_settings(request):
    """
    :return:
    {
    "class_product_for_profile": [{"class_product":},{"class_product":}],
    "type_product_for_profile": [{"type_product":},{"type_product":}]
    }
    """
    profile = request.user.profile

    class_product_for_profile = ClassProductForProfile.objects.filter(profile=profile)
    class_for_profile = [{"class_product": class_product.name} for class_product in class_product_for_profile]

    type_product_for_profile = TypeProductForProfile.objects.filter(profile=profile)
    type_for_profile = [{"type_product": type_product.name} for type_product in type_product_for_profile]

    return Response({"class_product_for_profile": class_for_profile,
                     "type_product_for_profile":type_for_profile
                     })


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_personal_language(request):
    """
    :param request:
    {
        "language": id
    }
    :return:
    """
    profile = request.user.profile
    language = request.data.get('language', 0)

    if type(language) != int:
        return Response({'error': 'Incorrect type language (need int)'}, status=400)

    l = Language.objects.filter(id=language).first()
    if not l:
        return Response({'error': 'Incorrect language id'}, status=400)

    profile.language = l
    profile.save()

    out_vars = {
        'language': {'id': l.id, 'name': l.name}
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_personal_avatar(request):
    """
    :param request:
    {
        "avatar": ""
    }
    :return:
    """
    profile = request.user.profile
    avatar = request.data.get('avatar', False)
    profile.avatar.delete(False)

    if avatar:
        avatar = avatar_personal_upload(avatar, profile.id)
        profile.avatar = avatar
    else:
        return Response({"error": "Empty avatar"}, status=400)

    profile.save()

    out_vars = {
        'avatar': profile.avatar.url
    }

    return Response(out_vars)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_group(request):
    profile = request.user.profile
    group = request.data.get('group')

    gr = Group.objects.filter(id=group).first()
    if gr:
        g, create = GroupForProfile.object.get_or_create(profile=profile, group=group)
        g.save()
    else:
        return Response({"error": "Group does not exist"}, status=404)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_category(request):
    profile = request.user.profile
    category = request.data.get('category')

    ca = Category.objects.filter(id=category).first()
    if ca:
        g, create = CategoryForProfile.object.get_or_create(profile=profile, category=category)
        g.save()
    else:
        return Response({"error": "Category does not exist"}, status=404)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_profile_subcategory(request):
    profile = request.user.profile
    subcategory = request.data.get('subcategory')

    g, create = SubcategoryForProfile.object.get_or_create(profile=profile, subcategory=subcategory)
    g.save()

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_profile_class(request):
    '''
    :param request:
     {"class_product": int}
    :return:
        status 200
    '''
    profile = request.user.profile
    class_product = request.data.get('class_product')
    count_class = ClassProductForProfile.CLASS_PROD[-1][0]

    if not class_product:
        return Response({"error": "Enter class"}, status=400)

    if 0 < class_product <= count_class:
        class_for_profile, create = ClassProductForProfile.objects.get_or_create(
            name=class_product,
            profile=profile
        )
        if create:
            class_for_profile.save()
        else:
            return Response({"error": "User already has this class"})
    else:
        return Response({"error": "Not a valid class"}, status=404)

    return Response(HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def dell_profile_class(request):
    '''
    :param request:
     {"class_product": int}
    :return:
        status 200
    '''
    profile = request.user.profile
    class_product = request.data.get('class_product')
    count_class = ClassProductForProfile.CLASS_PROD[-1][0]

    if not class_product:
        return Response({"error": "Enter class"}, status=400)

    if 0 < class_product <= count_class:
        class_for_profile = ClassProductForProfile.objects.get(name=class_product, profile=profile)
        class_for_profile.delete()
    else:
        return Response({"error": "Invalid class"}, status=404)

    return Response(HTTP_200_OK)