import os
from django.conf import settings

from rest_framework.authtoken.models import Token

from random import choice
from string import digits, ascii_letters

import base64
from django.core.files.base import ContentFile


def id_generator(size=25, chars=digits + ascii_letters):
    return ''.join(choice(chars) for _ in range(size))


def file_uploader(f, upload_to):
    format, imgstr = f.split(';base64,')
    ext = format.split('/')[-1]
    f = ContentFile(base64.b64decode(imgstr), name='file.' + ext)

    filename, file_ext = os.path.splitext(f.name)
    filename = id_generator()

    os.makedirs(os.path.join(settings.MEDIA, upload_to), mode=0o777, exist_ok=True)
    path = os.path.join(settings.MEDIA_ROOT, upload_to, filename + file_ext)

    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return os.path.join(upload_to, filename+file_ext)


def file_remover(file_path):
    remove_from = os.path.join(settings.BASE_DIR, file_path[1:])
    try:
        os.remove(remove_from)
        return True
    except:
        print('File not deleted')
        return False


def product_photo_upload(f, prod_id):
    upload_to = os.path.join(settings.PHOTO_PROD_URL, str(prod_id))
    return file_uploader(f, upload_to)


def product_video_upload(f, prod_id):
    upload_to = os.path.join(settings.VIDEO_PROD_URL, str(prod_id))
    return file_uploader(f, upload_to)


def avatar_personal_upload(f, prof_id):
    upload_to = os.path.join(settings.AVATAR_PERSONAL_URL, str(prof_id))
    return file_uploader(f, upload_to)


def avatar_business_upload(f, bprof_id):
    upload_to = os.path.join(settings.AVATAR_BUSINESS_URL, str(bprof_id))
    return file_uploader(f, upload_to)


def photo_business_upload(f, bprof_id):
    upload_to = os.path.join(settings.PHOTO_BUSINESS_URL, str(bprof_id))
    return file_uploader(f, upload_to)


def video_business_upload(f, bprof_id):
    upload_to = os.path.join(settings.VIDEO_BUSINESS_URL, str(bprof_id))
    return file_uploader(f, upload_to)


def about_business_upload(f, bprof_id):
    upload_to = os.path.join(settings.ABOUT_BUSINESS_URL, str(bprof_id))
    return file_uploader(f, upload_to)


def gen_url_with_keys_email(email, param):
    key = ''.join(choice(digits + ascii_letters) for i in range(25))
    data = 'email={0}&key={1}'.format(email, key)
    url = ''.join((
        settings.HOST_CLIENT,
        '/{0}/?'.format(param),
        data
    ))
    return url, key


def token_renew(user_obj):
    try:
        t = Token.objects.get(user=user_obj)
    except Token.DoesNotExist:
        pass
    else:
        t.delete()
    finally:
        t, created = Token.objects.get_or_create(user=user_obj)
        if created: t.save()

    return t.key


def check_img(img):
    try:
        img = img.url
    except ValueError:
        img = False
    return img


def check_list_objects_exists(id, ModelName):
    try:
        class_pr = ModelName.objects.get(id=id)
    except ModelName.DoesNotExist:
        return id

