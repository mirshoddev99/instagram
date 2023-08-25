class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get("userinput", None)
        if check_user_input_type(user_input) == "email":
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_input_type(user_input) == "phone":
            user = self.get_user(phone_number=user_input)
            username = user_input
        elif check_user_input_type(user_input) == "username":
            username = user_input
        else:
            data = {"success": False, "message": "You must enter email, phone number or username!"}
            raise ValidationError(data)

        # check status of a user
        current_user = User.objects.filter(username__iexact=username).first()  # None
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

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "message": "No active account found"
                }
            )
        return users.first()