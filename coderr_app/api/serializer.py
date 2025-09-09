from rest_framework import serializers
from coderr_app.models import Offer


class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description']