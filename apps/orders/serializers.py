from rest_framework import serializers
from apps.orders.models import Orders, Category, OrderImage


class OrderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderImage
        fields = ['id', 'image']


class OrderSerializer(serializers.ModelSerializer):
    images = OrderImageSerializer(many=True, write_only=True, required=False)
    image_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Orders
        fields = [
            'id', 'title', 'description', 'created_at', 'created_by',
            'executor', 'is_taken', 'is_paid', 'region', 'type_orders',
            'price_for_executor', 'budget', 'deadline', 'contact_phone',
            'latitude', 'longitude', 'images', 'image_urls'
        ]
        read_only_fields = ['created_by', 'executor', 'is_taken', 'image_urls']

    def get_image_urls(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(image.image.url) for image in obj.images.all()] if request else []

    def validate_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Можно загрузить не более 5 изображений.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['created_by'] = self.context['request'].user
        order = super().create(validated_data)

        for image_data in images_data:
            OrderImage.objects.create(order=order, image=image_data['image'])

        return order

class RecursiveCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if hasattr(obj, 'children'):
            children = obj.children.all()
            return RecursiveCategorySerializer(children, many=True).data
        return []


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'parent', 'children']

    def get_children(self, obj):
        return RecursiveCategorySerializer(obj.children.all(), many=True).data
