from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from shared.custom_methods import check_email_or_phone, send_email, send_phone_number, check_user_input_type, get_user
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'photo')


class SignUpSerializer(serializers.ModelSerializer):
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = (
            'auth_type',
            'auth_status'
        )

    def validate(self, attrs):
        data = super().validate(attrs)
        return self.auth_validate(data)

    @staticmethod
    def auth_validate(attrs):
        user_input = str(attrs.get('email_phone_number').lower())
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            attrs = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }

        elif input_type == 'phone':
            attrs = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }

        else:
            attrs = {
                'success': False,
                'message': "You must provide email or phone number"
            }
            raise ValidationError(attrs)
        print(attrs)
        return attrs

    def create(self, validated_data):
        user = super().create(validated_data)
        print("User: ", user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_number(user.username, user.phone_number, code)
        user.save()
        return user

    @staticmethod
    def validate_email_phone_number(value):
        value = value.lower()
        print("validate_email_phone_number method: ", value)
        if value and User.objects.filter(email=value).exists():
            raise ValidationError("This email already in use!")
        elif value and User.objects.filter(phone_number=value).exists():
            raise ValidationError("This phone number already in use!")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data


class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match!")
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    @staticmethod
    def validate_username(username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError("Username must be between 5 and 30 characters")
        if username.isdigit():
            raise ValidationError("This username is entirely numeric")
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get("password", instance.password):
            instance.set_password(validated_data.get("password", instance.password))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("You can not log in because of you have no permission!")
        data = self.user.token()
        data["auth_status"] = self.user.auth_status
        data["success"] = True
        data["message"] = "You have successfully logged in!"
        data['full_name'] = self.user.full_name
        return data

    def auth_validate(self, data):
        user_input = data.get("userinput", None)
        if check_user_input_type(user_input) == "email":
            user = get_user(email__iexact=user_input)
            username = user.username
        elif check_user_input_type(user_input) == "phone":
            user = get_user(phone_number=user_input)
            username = user_input
        elif check_user_input_type(user_input) == "username":
            username = user_input
        else:
            data = {"success": False, "message": "You must enter email, phone number or username!"}
            raise ValidationError(data)

        # check status of a user
        current_user = User.objects.filter(username=username).first()
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError({
                "success": False,
                "message": "You have not signed up entirely!"
            })

        authentication_kwargs = {
            self.username_field: username,
            "password": data["password"]
        }
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                "success": False,
                "message": "Sorry, password or username you entered is incorrect. Please check it out and try again!"
            })


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            data = {"success": False, "message": "Enter your email or phone number"}
            raise ValidationError(data)
        q = Q(email=email_or_phone) | Q(phone_number=email_or_phone)
        user = User.objects.filter(q)
        if not user.exists():
            raise NotFound(detail="no found user")
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError({"success": False, "message": "Passwords do not match!"})
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password = validated_data.get("password")
        instance.set_password(password)
        return super().update(instance, validated_data)
