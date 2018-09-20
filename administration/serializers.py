from rest_framework import serializers

from models import CelebrityDetails, BookingPrice, BookingCottage


class CelebrityDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CelebrityDetails
        fields = "__all__"



class BookingPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingPrice
        fields = "__all__"


class BookingCottageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingCottage
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingCottage
        fields = "__all__"