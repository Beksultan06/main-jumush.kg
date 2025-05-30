from rest_framework import serializers
from .models import User
import re, uuid
from apps.users.utils import set_reset_code, send_reset_code
from core.passport_classifier.utils import predict_passport_photo
from apps.users.utils import generate_code, get_reset_code, delete_reset_code 


class UserSerializer(serializers.ModelSerializer):
    executor_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'role',
            'is_verified', 'replies_balance',
            'executor_balance',  
            'date_joined', 'is_active'
        ]
        read_only_fields = [
            'is_verified', 'replies_balance', 'executor_balance',
            'date_joined', 'is_active'
        ]

    def get_executor_balance(self, obj):
        if obj.role == "исполнитель":
            return obj.executor_balance
        return None  



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    passport_photo_with_face = serializers.ImageField(required=False)
    passport_front = serializers.ImageField(required=False)
    passport_back = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "username", 'email', "region", 'password', 'phone', 'role',
            'passport_photo_with_face', 'passport_front', 'passport_back'
        ]

    def validate_phone(self, value):
        pattern = r'^\+996\d{9}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Формат номера должен быть: +996XXXXXXXXX")
        return value

    def validate(self, data):
        role = data.get("role")

        if role and isinstance(role, str) and role.lower() == "исполнитель":
            if not data.get("passport_photo_with_face") or not data.get("passport_front") or not data.get("passport_back"):
                raise serializers.ValidationError({
                    "passport_photo_with_face": "Обязательно загрузите фото с паспортом.",
                    "passport_front": "Обязательно загрузите переднюю сторону паспорта.",
                    "passport_back": "Обязательно загрузите обратную сторону паспорта.",
                })
            if not predict_passport_photo(data["passport_photo_with_face"], expected_type='face'):
                raise serializers.ValidationError({
                    "passport_photo_with_face": "Фото с паспортом не соответствует требованиям."
                })

            if not predict_passport_photo(data["passport_front"], expected_type='front'):
                raise serializers.ValidationError({
                    "passport_front": "Передняя сторона паспорта не распознана."
                })

            if not predict_passport_photo(data["passport_back"], expected_type='back'):
                raise serializers.ValidationError({
                    "passport_back": "Задняя сторона паспорта не распознана."
                })

        return data

    def create(self, validated_data):
        if "username" not in validated_data or not validated_data["username"]:
            validated_data["username"] = str(uuid.uuid4())

        role = validated_data.get("role")
        if role and isinstance(role, str) and role.lower() == "исполнитель":
            validated_data["is_verified"] = True

        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
        return value



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Новый пароль должен содержать минимум 8 символов.")
        return value

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        code = generate_code()
        set_reset_code(email, code)
        send_reset_code(email, code)
        return {"detail": "Код отправлен на почту"}


class ConfirmResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')

        if not code.isdigit():
            raise serializers.ValidationError('Код должен содержать только цифры.')

        saved_code = get_reset_code(email)
        if saved_code is None:
            raise serializers.ValidationError('Код истёк или не существует.')
        if saved_code != code:
            raise serializers.ValidationError('Неверный код.')
        return data


    def save(self, **kwargs):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        delete_reset_code(email)
        return user
