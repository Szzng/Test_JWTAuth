from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

UserModel = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(style={"input_type": "password"})
    password2 = serializers.CharField(style={"input_type": "password"})
    write_only_fields = (
        "password1",
        "password2",
    )

    def validate_email(self, email):
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError(
                _(email + " : 이미 가입된 이메일 주소입니다."),
            )
        validate_email(email)
        return email

    def validate_password1(self, password):
        min_length = 8
        if len(password) < min_length:
            raise ValidationError(_("비밀번호는 최소 {0}자 이상으로 만들어주세요.").format(min_length))
        validate_password(password)
        return password

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise ValidationError(_("두 비밀번호가 일치하지 않습니다."))
        return data

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self):
        data = self.get_cleaned_data()
        user = UserModel.objects.create_user(
            email=data["email"], password=data["password1"]
        )
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def validate(self, data):
        email = data["email"]
        password = data["password"]
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _("이메일 주소와 비밀번호를 입력해주세요.")
            raise ValidationError(msg)

        if not user:
            msg = _("일치하는 회원을 찾을 수 없습니다.")
            raise ValidationError(msg)

        if not user.is_active:
            msg = _("정지된 회원 계정입니다.")
            raise ValidationError(msg)

        data["user"] = user
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "email", "nickname", "is_active")
        read_only_fields = (
            "id",
            "email",
            "is_active",
        )


class JWTSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    access_token_expiration = serializers.DateTimeField()
    refresh_token_expiration = serializers.DateTimeField()

    def get_user(self, obj):
        user_data = UserDetailSerializer(obj["user"], context=self.context).data
        return user_data
