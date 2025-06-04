from rest_framework import serializers
from .models import User, UserRegion, UserSubRegion
import re, uuid
from apps.users.utils import set_reset_code, send_reset_code
from apps.users.utils import generate_code, get_reset_code, delete_reset_code


class UserRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegion
        fields = ['id', 'title']


class UserSubRegionSerializer(serializers.ModelSerializer):
    region = UserRegionSerializer(read_only=True)

    class Meta:
        model = UserSubRegion
        fields = ['id', 'title', 'region']


class UserSerializer(serializers.ModelSerializer):
    executor_balance = serializers.SerializerMethodField()
    region = UserRegionSerializer(read_only=True)
    subregion = UserSubRegionSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'role',
            'is_verified', 'replies_balance',
            'executor_balance', 'region', 'subregion',
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
    
    # Добавляем region только для валидации и передачи
    region = serializers.PrimaryKeyRelatedField(
        queryset=UserRegion.objects.all(), write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "region", "subregion", "password",
            "phone", "role", "passport_photo_with_face",
            "passport_front", "passport_back"
        ]
        extra_kwargs = {
            "subregion": {"required": True},
        }

    def validate_phone(self, value):
        pattern = r'^\+996\d{9}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Формат номера должен быть: +996XXXXXXXXX")
        return value

    def validate(self, data):
        role = data.get("role")

        # Проверка, чтобы subregion соответствовал выбранному региону
        region = data.get("region")
        subregion = data.get("subregion")

        if subregion and region and subregion.region != region:
            raise serializers.ValidationError({
                "subregion": "Этот подрегион не относится к выбранному региону."
            })

        if role and isinstance(role, str) and role.lower() == "исполнитель":
            if not data.get("passport_photo_with_face") or not data.get("passport_front") or not data.get("passport_back"):
                raise serializers.ValidationError({
                    "passport_photo_with_face": "Обязательно загрузите фото с паспортом.",
                    "passport_front": "Обязательно загрузите переднюю сторону паспорта.",
                    "passport_back": "Обязательно загрузите обратную сторону паспорта.",
                })

        return data

    def create(self, validated_data):
        validated_data.pop("region", None)  # region не нужен при создании User

        if not validated_data.get("username"):
            validated_data["username"] = str(uuid.uuid4())

        user = User.objects.create_user(**validated_data)

        role = validated_data.get("role")
        if role and role.lower() == "исполнитель":
            from core.passport_classifier.tasks import validate_passport_images_task
            validate_passport_images_task.delay(
                user.id,
                user.passport_photo_with_face.path,
                user.passport_front.path,
                user.passport_back.path,
            )

        return user

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
