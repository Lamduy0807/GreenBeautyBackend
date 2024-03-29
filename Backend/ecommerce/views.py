from django.db.models import query
from django.shortcuts import render
from rest_framework import exceptions, generics, serializers
from rest_framework import permissions
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.db import connection
import pandas as pd
import sklearn as sk
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


# khúc này mới thêm 4 dòng
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import filters


# Create your views here.
class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class=RegisterSerializer
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user= User.objects.get(email=user_data['email'])
        token=RefreshToken.for_user(user).access_token

        current_site=get_current_site(request).domain
        realtivelink = reverse('email-verify')
        
        absurl='http://'+current_site+realtivelink+"?token="+ str(token)
        email_body='Hi '+ user.email+ ' Use link below to verify your email \n' + absurl
        data={'email_body':email_body,'to_email':user.email,'email_subject':'Verify your email'}
        Util.send_email(data)
        return Response(user_data,status= status.HTTP_201_CREATED)

class VerifyEmail(generics.GenericAPIView):
    def get(self,request):
        token= request.GET.get('token')
        try:
            payload=jwt.decode(token,settings.SECRET_KEY,algorithms='HS256')
            user=User.objects.get(id=payload['user_id'])

            if not user.is_verified:
                user.is_verified=True
                user.save()
            return Response({'email':'Successfully activated'},status= status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as indentifier:
            return Response({'email':'Activation expired'},status= status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as indentifier:
            return Response({'email':'Invalid token'},status= status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializers
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK )

class RequestPasswordResetEmail(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class=ResetPasswordViaEmailSerializer
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id) )
            token = PasswordResetTokenGenerator().make_token(user)

            current_site=get_current_site(request=request).domain
            realtivelink = reverse('password-reset',kwargs={'uidb64':uidb64,'token':token})
                
            absurl='http://'+current_site+realtivelink
            email_body='Hi, \nUse link below to reset your password \n' + absurl
            data={'email_body':email_body,'to_email':user.email,'email_subject':'Reset your password'}
            Util.send_email(data)
        return Response({'successfully':'check your email to reset your password'},status=status.HTTP_200_OK)

class PasswordTokenCheckAPIView(generics.GenericAPIView):
    def get(self, request, uidb64,token):
        try:
            id= smart_str(urlsafe_base64_decode(uidb64))
            user= User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({'error':'token is not valid, please check the new one'},status=status.HTTP_401_UNAUTHORIZED)
            return Response({'sucess':True, 'message':'Credential Valid','uidb64':uidb64, 'token':token},status=status.HTTP_200_OK)


        except DjangoUnicodeDecodeError as indentifier:
            return Response({'error':'token is not valid, please check the new one'},status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):

    queryset = User.objects.all()
    serializer_class=ResetPassWordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response({'sucess':True, 'message':'Password is reset successfully'},status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer 
    permission_classes  = [IsAuthenticated,]
class UploadViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UploadAvtSerializer

class ProductViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.action == 'add-rating':
            return [permissions.IsAuthenticated(),]
        return [permissions.AllowAny(),]

    @action(methods=['post'], detail=True, url_path='add-rating')
    def add_Rating(self, request, pk):
        ratingcomment = request.data.get('comment')
        ratingpoint = request.data.get('point')
        img = request.data.get('img')

        if ratingcomment:
            r = Rating.objects.create(ratingcomment=ratingcomment, product = self.get_object(), ratingpoint= ratingpoint, img = img, user = request.user)
            return Response(RatingSerializer(r).data,status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_403_FORBIDDEN)


# Nga Add
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [ 'category','IsActive']
    search_fields = ['name', ]

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['product']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

# Nga Add
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['producttype']

class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

# Nga Add
    # filter_backends = (SearchFilter, OrderingFilter)
    # search_fields = ['id']

class RatingViewSet(generics.GenericAPIView):
    queryset = Rating.objects.all()

    def get(self, request, id, point):
        if(int(point) > 0):
            r = Rating.objects.filter(product = id, ratingpoint = point)
            seri = RatingSerializer(r,many=True)
            return Response(seri.data, status=status.HTTP_200_OK)
        else:
            r = Rating.objects.filter(product = id)
            seri = RatingSerializer(r,many=True)
            return Response(seri.data, status=status.HTTP_200_OK)
    def getuser(self, request,user):
        r = Rating.objects.filter(user = user)
        seri = RatingSerializer(r,many=True)
        return Response(seri.data, status=status.HTTP_200_OK)
class RatingViewSet1(generics.GenericAPIView):
    queryset = Rating.objects.all()

    def get(self, request,user):
        r = Rating.objects.filter(user = user)
        seri = RatingSerializer(r,many=True)
        return Response(seri.data, status=status.HTTP_200_OK)
class LoveListViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = LoveList.objects.all()
    serializer_class = LoveListSerializer

    # Nga Add
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer_id','product_id']

class TagViewSet(viewsets.ModelViewSet):
    queryset = IngredientsTag.objects.all()
    serializer_class = TagSerializer

class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    lookup_field = 'slug'

class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Provinces.objects.all()
    serializer_class = ProvinceSerializer

class DistrictViewSet (viewsets.ModelViewSet):
    queryset = Districts.objects.all()
    serializer_class = DistrictSerializer

class WardViewSet(viewsets.ModelViewSet):
    queryset = Wards.objects.all()
    serializer_class = WardSerializer

class DeliveryViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

# Nga Add
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','defaultAddress']

class OrderViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user','status']

class DetailOrderViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = DetailOrder.objects.all()
    serializer_class = DetailOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order']
    @action (methods=['post'],detail=True,url_path="set-rating", url_name="set-rating")
    def set_rating(self, request, pk):
        try:
            l = DetailOrder.objects.get(pk=pk)
            l.isRating = True
            l.save()
        except DetailOrder.DoesNotExists:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

class CartViewSet(viewsets.ModelViewSet, ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
# Nga Add
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','product']
class BannerViewSet(viewsets.ModelViewSet,ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

def get_product_data():
        cursor = connection.cursor()
        cursor.execute("select ecommerce_user.id as 'user_id', ecommerce_product.id as 'product_id'from doan1db.ecommerce_user, doan1db.ecommerce_product")
        product_user = cursor.fetchall()
        product = pd.DataFrame(product_user, columns=['user_id', 'product_id'])
        return product
def get_rating_data():
        cursor = connection.cursor()
        cursor.execute("Select product_id, AVG(ratingpoint) as rating, user_id from doan1db.ecommerce_rating group by product_id, user_id")
        rating = cursor.fetchall()
        rates = pd.DataFrame(rating, columns=['product_id', 'rating','user_id'])
        return rates

def data_preparetion():
    product = get_product_data()
    rating = get_rating_data()

    data = pd.merge(rating, product, on = ['user_id','product_id'], how = 'outer')
    matrix = data.pivot(columns='product_id',index='user_id',values='rating')
    matrix = matrix.fillna(0)

    return matrix

def SVD(matrix):
    X  = matrix.T
    SVD = TruncatedSVD(n_components=6, random_state=3)

    resultant_matrix = SVD.fit_transform(X)
    return resultant_matrix

class RecommendViewSet(APIView):
    
    @action (methods=['get'],detail=True,url_path="recommend", url_name="recommend")    
    def get(self, request, id):
        matrix = data_preparetion()
        re = SVD(matrix)

        item_sim = np.corrcoef(re)
        
        col_idx = matrix.columns.get_loc(int(id)) 

        corr_specific = item_sim[int(col_idx)]

        dataframe = pd.DataFrame({'corr_specific':corr_specific, 'product_id': matrix.columns})\
        .sort_values('corr_specific', ascending=False)\
        .head(10)

        data_re = dataframe.to_dict('records')
        results = RecommendSerializer(data_re, many=True).data
        return Response(results)


def get_ingredient_data():
        cursor = connection.cursor()
        cursor.execute("SELECT id , Ingredient FROM doan1db.ecommerce_product")
        product_user = cursor.fetchall()
        product = pd.DataFrame(product_user, columns=['id', 'ingredient'])
        return product
def transform_data(product):
        tfidf = TfidfVectorizer(stop_words='english')

#Replace NaN with an empty string
        product['ingredient'] = product['ingredient'].fillna('')

#Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(product['ingredient'])
        consine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        return consine_sim
class RecommendIngredientViewSet(APIView):

    @action (methods=['get'],detail=True,url_path="re", url_name="re")    
    def get(self, request, id):
        product = get_ingredient_data()
        cosine_sim = transform_data(product)

        indices = pd.Series(product.index, index=product['id']).drop_duplicates()
        idx = indices[int(id)]
        
        sim_scores = list(enumerate(cosine_sim[idx]))

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:11]

        product_indices = [i[0] for i in sim_scores]

        pro_id = product['id'].iloc[product_indices]
        data = pd.DataFrame(columns=["id"])
        data['id'] = pro_id
        data = data.to_dict('records')
        results = RecommendIngredientSerializer(data, many=True).data

        return Response(results)