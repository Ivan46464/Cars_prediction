import pickle

import numpy as np
from charset_normalizer.utils import any_specified_encoding
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.shortcuts import render
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from cars_project.serializers import CreateUserSerializer
from ultralytics import YOLO


# Create your views here.
class RegisterUser(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])
            token = Token.objects.create(user=user)
            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(APIView):

    def post(self, request):
        user = get_object_or_404(User, username=request.data.get('username'))
        if not user.check_password(request.data.get('password')):
            return Response({"details": "Incorrect username or password"}, status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        serializer = CreateUserSerializer(instance=user)
        print(token)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

class LogoutUser(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': "Successful logout"}, status=status.HTTP_200_OK)

class Predict_damage(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'file' not in request.data:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.data['file']
        file_path = default_storage.save(f'tmp/{uploaded_file.name}', uploaded_file)
        try:
            model = YOLO('Models/best.pt')
            results = model(file_path, conf=0.25)
            names = {
                0:'Damage', 1:'Major-Dent', 2:'Minor-Dent', 3:'Scratch'
            }
            answers = []
            for r in results:
                for box in r.boxes:
                    if box.cls.item() in names.keys():
                        answers.append(names[box.cls.item()])

            def most_frequent(List):
                return max(set(List), key=List.count)
            if not len(answers)==0:
                answer=most_frequent(answers)
            else:
                answer="Not found"
            default_storage.delete(file_path)
            print(answers)

            return Response({'results': answer}, status=status.HTTP_200_OK)

        except Exception as e:
            default_storage.delete(file_path)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


with open("Models/car_price_model.pkl", "rb") as f:
    model_data = pickle.load(f)

model = model_data['model']
scaler = model_data['scaler']
poly = model_data['poly']
class PredictCarPriceAPIView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Get input data from the request
        try:
            car_model = int(request.data.get('car_model'))
            year = int(request.data.get('year'))
            mileage = int(request.data.get('mileage'))
            condition = int(request.data.get('condition'))
        except (TypeError, ValueError) as e:
            return Response({"error": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)

        # Preprocess input
        X_input = np.array([[car_model, year, mileage, condition]])
        X_scaled = scaler.transform(X_input)
        X_poly = poly.transform(X_scaled)

        # Predict price
        predicted_price = model.predict(X_poly)[0]
        return Response({"predicted_price": round(predicted_price, 2)}, status=status.HTTP_200_OK)

import pickle
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from ultralytics import YOLO



class CombinedPredictionAPIView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Check for uploaded image
        if 'file' not in request.data:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.data['file']
        file_path = default_storage.save(f'tmp/{uploaded_file.name}', uploaded_file)

        try:
            # Step 1: Predict car condition using the image
            damage_model = YOLO('Models/best.pt')
            results = damage_model(file_path, conf=0.25)
            names = {0: 'Damage', 1: 'Major-Dent', 2: 'Minor-Dent', 3: 'Scratch'}
            answers = []
            for r in results:
                for box in r.boxes:
                    if box.cls.item() in names.keys():
                        answers.append(names[box.cls.item()])

            # Determine the most frequent result
            def most_frequent(List):
                return max(set(List), key=List.count)

            if answers:
                condition_result = most_frequent(answers)
            else:
                condition_result = "Not found"

            # Map condition result to numerical condition input
            if condition_result in ['Not found', 'Scratch']:
                condition = 3  # Excellent
            elif condition_result in ['Minor-Dent', 'Major-Dent']:
                condition = 2  # Good
            elif condition_result == 'Damage':
                condition = 1  # Fair
            else:
                condition = 3  # Default to Excellent

            # Step 2: Predict car price
            try:
                car_model = int(request.data.get('car_model'))
                year = int(request.data.get('year'))
                mileage = int(request.data.get('mileage'))
            except (TypeError, ValueError) as e:
                return Response({"error": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)

            # Preprocess input for price prediction
            X_input = np.array([[car_model, year, mileage, condition]])
            X_scaled = scaler.transform(X_input)
            X_poly = poly.transform(X_scaled)

            predicted_price = model.predict(X_poly)[0]

            # Clean up uploaded file
            default_storage.delete(file_path)

            return Response({
                "condition_result": condition_result,
                "predicted_price": round(predicted_price, 2)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Clean up uploaded file in case of error
            default_storage.delete(file_path)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
