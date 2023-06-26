from rest_framework import serializers
from .models import User, Store, Vehicle, Route, RouteDetail


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'],
                                   name=validated_data['name'],
                                   password=validated_data['password']
                                   )
        user.set_password(validated_data['password'])
        user.save()
        return user


class StoreSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=200)
    # latitude = serializers.DecimalField(
    #     max_digits=10, decimal_places=6)
    # longitude = serializers.DecimalField(
    #     max_digits=10, decimal_places=6)
    # tw_start = serializers.IntegerField()
    # tw_end = serializers.IntegerField()
    # googleMap = serializers.CharField(max_length=300)
    # location = serializers.CharField(max_length=500)

    class Meta:
        model = Store
        fields = ('id', 'user_id', 'name', 'latitude',
                  'longitude', 'tw_start', 'tw_end', 'googleMap', 'location')


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'user_id', 'capacity', 'speed')
        lookup_field = "user_id"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RouteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteDetail
        fields = '__all__'
