from django.urls import path
from .views import RegisterView, StoreView, getUserStoreDetail, VehicleView, RouteView, calculateRoute, calculatePSORoute, getUserId, calculateManual
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

store_list = StoreView.as_view({
    'get': 'list',
    'post': 'create'
})

vehicle_list = VehicleView.as_view({
    'get': 'list',
})

vehicle_detail = VehicleView.as_view({
    'get': 'retrieve',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

route_get = RouteView.as_view({
    'get': 'list',
})

route_post = RouteView.as_view({
    'post': 'create',
})


urlpatterns = [
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', RegisterView.as_view(), name="sign_up"),
    path('store', store_list, name="store"),
    path('store/<int:id>', getUserStoreDetail, name="store_detail"),
    path('vehicle', vehicle_list, name="vehicle_list"),
    path('vehicle/<int:user_id>', vehicle_detail, name="vehicle_detail"),
    path('route', route_get, name="route"),
    path('route/<int:user_id>', route_get, name="route_user"),
    path('create/<str:type>', route_post, name="route-detail"),
    path('calculate_route/<int:id>', calculateRoute, name="da_route_calculate"),
    path('calculate_pso/<int:id>', calculatePSORoute, name="pso_route_calculate"),
    path('get_user_id', getUserId, name="get_user_id"),
    path('calculate_manual/<int:id>', calculateManual,
         name="manual_route_calculate")
]
