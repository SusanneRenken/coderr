from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail, Order
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
        instance.description = validated_data.get(
            'description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if detail_data:
            for detail in detail_data:
                try:
                    single_detail = instance.details.get(
                        offer_type=detail['offer_type'])
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

    min_price = serializers.IntegerField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_detail']
        read_only_fields = ['id']


class OfferDetailSerializer(OfferListSerializer):

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
                  'updated_at', 'details', 'min_price', 'min_delivery_time']
        read_only_fields = ['id']

# --- OFFER DETAIL ITEM SERIALIZER ---


class OfferDetailItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']
        read_only_fields = ['id']


# --- ORDER SERIALIZER (Placeholder) ---

class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(
        source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.IntegerField(
        source='offer_detail.price', read_only=True)
    features = serializers.ListField(
        source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(
        source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'status', 'offer_detail_id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_user',
                            'business_user', 'status', 'created_at', 'updated_at']
