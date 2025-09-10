from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    revisions = serializers.IntegerField(min_value=0)
    delivery_time_in_days = serializers.IntegerField(min_value=1)
    price = serializers.IntegerField(min_value=0)
    features = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]
        read_only_fields = ['id']


class OfferSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.instance is None:
            details = attrs.get('details')
            if not details or len(details) != 3:
                raise serializers.ValidationError("Exactly 3 details must be provided.")
            required = {'basic', 'standard', 'premium'}
            types = [d.get('offer_type') for d in details]
            if set(types) != required or len(types) != len(set(types)):
                raise serializers.ValidationError(
                    "Each offer_type (basic, standard, premium) must appear exactly once."
                )
        else:
            # PRÜFUNG BEI UPDATES DEAKTIVIERT
            pass
            # if 'details' in attrs:
            #     details = attrs['details']
            #     if len(details) != 3:
            #         raise serializers.ValidationError("Exactly 3 details must be provided.")
            #     required = {'basic', 'standard', 'premium'}
            #     types = [d.get('offer_type') for d in details]
            #     if set(types) != required or len(types) != len(set(types)):
            #         raise serializers.ValidationError(
            #             "Each offer_type (basic, standard, premium) must appear exactly once."
            #         )
        return attrs

    def create(self, validated_data):
        detail_data = validated_data.pop('details')

        offer = Offer.objects.create(**validated_data)
        for detail in detail_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer
