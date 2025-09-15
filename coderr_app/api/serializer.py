from django.db.models import Min
from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail
from django.contrib.auth.models import User

# --- CREATE and UPDATE SERIALIZERS ---

class OfferDetailItemNestedSerializer(serializers.ModelSerializer):
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
        extra_kwargs = {
            'offer_type': {'required': True}
        }


class OfferSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)
    details = OfferDetailItemNestedSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.instance is None:
            details = attrs.get('details')
            if not details or len(details) != 3:
                raise serializers.ValidationError(
                    "Exactly 3 details must be provided.")
            required = {'basic', 'standard', 'premium'}
            types = [d.get('offer_type') for d in details]
            if set(types) != required or len(types) != len(set(types)):
                raise serializers.ValidationError(
                    "Each offer_type (basic, standard, premium) must appear exactly once."
                )
        else:
            details = attrs.get('details')
            if details:
                types = [d.get('offer_type') for d in details]
                if len(types) != len(set(types)):
                    raise serializers.ValidationError(
                        "Duplicate offer_type values are not allowed."
                    )
        return attrs

    def create(self, validated_data):
        detail_data = validated_data.pop('details')

        offer = Offer.objects.create(**validated_data)
        for detail in detail_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer
    
    def update(self, instance, validated_data):
        detail_data = validated_data.pop('details', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if detail_data:
            for detail in detail_data:
                try:
                    single_detail = instance.details.get(offer_type=detail['offer_type'])
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Detail with offer_type '{detail['offer_type']}' does not exist."
                    )
                for attr, value in detail.items():
                    if attr == 'offer_type':
                        continue
                    setattr(single_detail, attr, value)
                single_detail.save()

        return instance

# --- LIST and DETAIL SERIALIZERS ---

class OfferListUserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class OfferListDetailNestedSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail', lookup_field='pk'
    )

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']
        read_only_fields = ['id', 'url']

class OfferListSerializer(OfferSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_detail = OfferListUserNestedSerializer(source='user', read_only=True)
    details = OfferListDetailNestedSerializer(many=True, read_only=True)

    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_detail']
        read_only_fields = ['id']

    def get_min_price(self, obj):
        return obj.details.aggregate(min_price=Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(
            min_delivery_time=Min('delivery_time_in_days')
        )['min_delivery_time']
    
class OfferDetailSerializer(OfferListSerializer):

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']
        read_only_fields = ['id']




class OfferDetailItemSerializer(serializers.ModelSerializer):
    pass
