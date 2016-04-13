from django.contrib.auth.models import User
from rest_framework import serializers
from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('gender', 'age')


class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()
    # profile_id = serializers.ReadOnlyField(source='profile.id')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',
                  'profile')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
        # Overwrite to create profile during create process
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
        user = instance
        user.email = validated_data['email']
        user.password = validated_data['password']
        user.username = validated_data['username']
        profile_data = validated_data.pop('profile')
        user.profile.gender = profile_data['gender']
        user.profile.age = profile_data['age']
        user.profile.phone_number = profile_data['phone_number']
        user.profile.wants_texts = profile_data['wants_texts']
        user.profile.save()

        return user
