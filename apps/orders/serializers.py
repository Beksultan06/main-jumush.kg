from rest_framework import serializers
from apps.orders.models import Orders

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'
        read_only_fields = ['created_by', 'executor', 'is_taken']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
