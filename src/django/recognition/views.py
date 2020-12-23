from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from .decrypt import decryption
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import cv2
import numpy
import re
from .services.cropping.aruco import kbs, work_list


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes([SessionAuthentication, BasicAuthentication])
def login(request):
    auth = request.data.get("auth")
    image = request.data.get("image")
    kbs_exsist = re.search('kpi', (str(image).split('.'))[0])
    work_exsist = re.search('worker_list', (str(image).split('.'))[0])
    image_name = (str(image).split('.'))[0]
    img = cv2.imdecode(numpy.fromstring(request.data.get('image').read(), numpy.uint8), cv2.IMREAD_UNCHANGED)
    if kbs_exsist:
        kbs(img, image_name)
    if work_exsist:
        work_list(img, image_name)
    username = (decryption(auth).split(',')[0]).replace(' ', '')
    password = (decryption(auth).split(',')[1]).replace(' ', '')
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    return Response({'GOOD': 'Вы ec!'},
                    status=HTTP_200_OK)



# @csrf_exempt
# @api_view(["GET"])
# def sample_api(request):
#     data = {'sample_data': 123}
#     return Response(data, status=HTTP_200_OK)

