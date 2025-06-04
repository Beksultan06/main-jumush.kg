from rest_framework import serializers
from apps.orders.models import Orders, Category
from mptt.templatetags.mptt_tags import cache_tree_children

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'
        read_only_fields = ['created_by', 'executor', 'is_taken']   

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


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