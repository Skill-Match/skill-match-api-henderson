from django.contrib.auth.models import User
from rest_framework import serializers
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('gender', 'age', 'wants_texts', 'phone_number')
        extra_kwargs = {
                        'wants_texts': {'required': False},
                        'phone_number': {'required': False}
                        }


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()
    # profile_id = serializers.ReadOnlyField(source='profile.id')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}
        read_only_fields = ('id',)

    # Overwrite to create profile during create process
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            username=validated_data['username'].lower(),
            password=validated_data['password']
        )
        profile_data = validated_data.pop('profile')
        Profile.objects.create(
            user=user,
            gender=profile_data.get('gender'),
            age=profile_data.get('age'),
        )

        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        instance.save()

        profile = instance.profile
        profile_data = validated_data.pop('profile')
        profile.gender = profile_data.get('gender', profile.gender)
        profile.age = profile_data.get('age', profile.age)
        profile.wants_texts = profile_data.get('wants_texts', profile.wants_texts)
        profile.phone_number = profile_data.get('phone_number', profile.phone_number)

        profile.save()

        return instance
