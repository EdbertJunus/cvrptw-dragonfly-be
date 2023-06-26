from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer, StoreSerializer, VehicleSerializer, RouteSerializer, RouteDetailSerializer
from rest_framework.response import Response
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import ParseError
from rest_framework.renderers import JSONRenderer
from .models import Store, Vehicle, Route, RouteDetail
from .permissions import AuthorPermission
import io
from .route_optimize import calculate
from .pso import calculatePSO
from rest_framework_simplejwt.tokens import AccessToken
from .route_optimization_utils import generateGoogleDistMatrix, calculateRouteCost
import time
# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# GET and POST


class StoreView(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [AuthorPermission]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        if (self.request.user.is_superuser):
            return Store.objects.all()
        id = self.request.user.id
        queryset = Store.objects.filter(user_id=id)
        return queryset


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def getUserStoreDetail(request, id):

    try:
        store = Store.objects.get(pk=id)
        # print("Store Awal: ", store)
    except Store.DoesNotExist:
        return JsonResponse({'status': 'Store Does not Exist'}, status=status.HTTP_404_NOT_FOUND)

    user_id = request.user.id
    store = Store.objects.filter(user_id=user_id).filter(id=id)

    if request.user.is_superuser:
        store = Store.objects.filter(id)

    if store.exists():

        store = Store.objects.get(pk=id)

        if request.method == "GET":
            serializer = StoreSerializer(store)
            return JsonResponse(serializer.data)

        if request.method == "PUT":
            data = JSONParser().parse(request)
            serializer = StoreSerializer(store, data=data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        if request.method == "PATCH":
            data = JSONParser().parse(request)
            serializer = StoreSerializer(store, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        if request.method == "DELETE":
            store.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    return JsonResponse({'status': 'No Permission to access store'}, status=status.HTTP_403_FORBIDDEN)


class VehicleView(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [AuthorPermission]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    lookup_field = "user_id"

    def get_queryset(self, **kwargs):
        user_id = self.kwargs['user_id']
        # print('current kwargs ', user_id)
        queryset = Vehicle.objects.filter(user_id=user_id)
        return queryset

    def list(self, request):
        if request.user.is_superuser:
            queryset = Vehicle.objects.all()
            serializer = VehicleSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'No Permission to access store'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, user_id):
        queryset = Vehicle.objects.all()
        creator = request.user.id == user_id

        if request.user.is_superuser or creator:
            vehicle = get_object_or_404(queryset, user_id=user_id)
            serializer = VehicleSerializer(vehicle)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        return JsonResponse({'status': 'No Permission to access store'}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, user_id):
        creator = request.user.id == user_id
        queryset = Vehicle.objects.filter(user_id=user_id)
        if queryset.exists():
            return JsonResponse({'status': 'There already exists vehicle for current user'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = VehicleSerializer(data=data)
        if serializer.is_valid() and creator:
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class RouteView(viewsets.ModelViewSet):
    serializer_class = {
        'route': RouteSerializer,
        'route-detail': RouteDetailSerializer
    }
    permission_class = [AuthorPermission]
    http_method_names = ['get', 'post']

    def list(self, request, user_id="None"):
        route_queryset = Route.objects.all()
        route_detail_queryset = RouteDetail.objects.all()

        creator = request.user.id == user_id

        if creator and user_id != "None":
            route_queryset = Route.objects.filter(user_id=user_id)
            route_id_list = []
            for item in route_queryset:
                route_id_list.append(item.id)
            route_detail_queryset = RouteDetail.objects.filter(
                route_id__in=route_id_list)

        route_serializer = RouteSerializer(route_queryset, many=True)
        route_detail_serializer = RouteDetailSerializer(
            route_detail_queryset, many=True)

        response = {
            'route': route_serializer.data,
            'route-detail': route_detail_serializer.data
        }

        return JsonResponse(response, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        response_message = None
        town_dist_matrix = []
        google_dist_matrix = []
        if self.kwargs['type'] == "route":
            route_serializer = RouteSerializer(data=request.data)
            route_serializer.is_valid(raise_exception=True)
            route_serializer.save()
            response_message = route_serializer.data

        if self.kwargs['type'] == "route-detail":
            route_detail_serializer = RouteDetailSerializer(
                data=request.data, many=True)
            route_detail_serializer.is_valid(raise_exception=True)
            route_detail_serializer.save()
            town_pos = []
            for item in request.data:
                town_pos.append([item['latitude'], item['longitude']])

            town_dist_matrix, google_dist_matrix = generateGoogleDistMatrix(
                town_pos)
            response_message = route_detail_serializer.data

        response = "error" if response_message == None else response_message

        return JsonResponse({"message": response, "distance_matrix": town_dist_matrix, "google_distance_matrix": google_dist_matrix}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculateRoute(request, id):

    start = time.time()

    town_name = []
    town_pos = []
    town_demand = []
    town_tw = []
    vehicle_speed = 0
    vehicle_capacity = 0

    try:
        route = Route.objects.get(pk=id)
    except Route.DoesNotExist:
        return JsonResponse({'status': 'Route Does not Exist'}, status=status.HTTP_404_NOT_FOUND)

    route = Route.objects.filter(pk=id)
    user_id = route.values('user_id')[0]['user_id']
    gasoline_price = route.values('gasoline_price')[0]['gasoline_price']
    vehicle = Vehicle.objects.filter(user_id=user_id)

    vehicle_speed = vehicle.values('speed')[0]['speed']
    vehicle_capacity = vehicle.values('capacity')[0]['capacity']

    route_detail = RouteDetail.objects.filter(route_id=id)

    if route_detail.exists():
        # print(route_detail)
        for item in route_detail:
            town_name.append(item.store_name)
            town_pos.append([item.latitude, item.longitude])
            town_demand.append(item.demand)
            town_tw.append([item.tw_start, item.tw_end])

    town_dist_matrix = request.data['distance_matrix']
    best_dragon, best_cost = calculate(
        town_name, town_pos, town_demand, town_tw, town_dist_matrix, vehicle_speed, vehicle_capacity, gasoline_price)

    response = {
        'result': ' '.join(map(str, best_dragon)),
        'cost':  best_cost
    }

    end = time.time()
    print("calculateRouteDA", end - start)

    return JsonResponse(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculatePSORoute(request, id):
    start = time.time()
    town_name = []
    town_pos = []
    town_demand = []
    town_tw = []
    vehicle_speed = 0
    vehicle_capacity = 0

    try:
        route = Route.objects.get(pk=id)
    except Route.DoesNotExist:
        return JsonResponse({'status': 'Route Does not Exist'}, status=status.HTTP_404_NOT_FOUND)

    route = Route.objects.filter(pk=id)
    user_id = route.values('user_id')[0]['user_id']
    gasoline_price = route.values('gasoline_price')[0]['gasoline_price']
    vehicle = Vehicle.objects.filter(user_id=user_id)

    vehicle_speed = vehicle.values('speed')[0]['speed']
    vehicle_capacity = vehicle.values('capacity')[0]['capacity']

    route_detail = RouteDetail.objects.filter(route_id=id)

    if route_detail.exists():

        for item in route_detail:
            town_name.append(item.store_name)
            town_pos.append([item.latitude, item.longitude])
            town_demand.append(item.demand)
            town_tw.append([item.tw_start, item.tw_end])

    town_dist_matrix = request.data['distance_matrix']
    result, cost = calculatePSO(
        town_name, town_pos, town_demand, town_tw, town_dist_matrix, vehicle_speed, vehicle_capacity, gasoline_price)
    response = {
        'result': ' '.join(map(str, result)),
        'cost':  cost
    }
    end = time.time()
    print("calculateRoutePSO", end - start)
    return JsonResponse(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserId(request):

    response = {
        'user_id': request.user.id
    }
    return JsonResponse(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculateManual(request, id):
    town_name = []
    town_pos = []
    town_demand = []
    town_tw = []
    vehicle_speed = 0
    vehicle_capacity = 0

    try:
        route = Route.objects.get(pk=id)
    except Route.DoesNotExist:
        return JsonResponse({'status': 'Route Does not Exist'}, status=status.HTTP_404_NOT_FOUND)

    route = Route.objects.filter(pk=id)
    user_id = route.values('user_id')[0]['user_id']
    gasoline_price = route.values('gasoline_price')[0]['gasoline_price']
    vehicle = Vehicle.objects.filter(user_id=user_id)

    vehicle_speed = vehicle.values('speed')[0]['speed']
    vehicle_capacity = vehicle.values('capacity')[0]['capacity']

    route_detail = RouteDetail.objects.filter(route_id=id)

    if route_detail.exists():
        for item in route_detail:
            town_name.append(item.store_name)
            town_pos.append([item.latitude, item.longitude])
            town_demand.append(item.demand)
            town_tw.append([item.tw_start, item.tw_end])

    town_dist_matrix = request.data['distance_matrix']
    route_index = list(range(0, len(town_dist_matrix)-1))
    manual_cost = calculateRouteCost(
        route_index, town_dist_matrix, town_tw, vehicle_speed, gasoline_price)

    response = {
        'route_manual': ' '.join(map(str, route_index)),
        'cost_manual':  manual_cost
    }

    return JsonResponse(response, status=status.HTTP_200_OK)
