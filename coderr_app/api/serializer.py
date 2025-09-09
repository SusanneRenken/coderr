from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']
        read_only_fields = ['id']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, write_only=True)
    details_full = OfferDetailSerializer(
        source='details', many=True, read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'details', 'details_full']
        read_only_fields = ['id']

    def validate(self, attrs):
        details = attrs.get('details', [])
        if len(details) != 3:
            raise serializers.ValidationError(
                "Exactly 3 details must be provided.")

        required_types = {'basic', 'standard', 'premium'}
        types = [detail.get('offer_type') for detail in details]

        if set(types) != required_types or len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Each offer_type (basic, standard, premium) must appear exactly once.")

        return details

    def create(self, validated_data):
        detail_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)

        for detail in detail_data:
            OfferDetail.objects.create(offer=offer, **detail)

        return offer
