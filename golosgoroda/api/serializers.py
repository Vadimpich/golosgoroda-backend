from django.contrib.auth.models import User
from rest_framework import serializers

from votings.models import Object, Voting, VotingObject


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = '__all__'


class VotingObjectSerializer(serializers.ModelSerializer):
    object = ObjectSerializer(read_only=True)

    class Meta:
        model = VotingObject
        fields = ['object', 'votes_count']


class VotingEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = ['title', 'voting_date']


class VotingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    total_votes = serializers.ReadOnlyField(source='total_votes')

    class Meta:
        model = Voting
        fields = ['id', 'title', 'status', 'created_at', 'formed_at',
                  'completed_at', 'voting_date', 'total_votes',
                  'user', 'moderator']

    def get_user(self, obj):
        return obj.user.username

    def get_moderator(self, obj):
        return obj.moderator.username


class VotingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    objects = VotingObjectSerializer(source='votingobject_set', many=True,
                                     read_only=True)

    class Meta:
        model = Voting
        fields = ['id', 'title', 'status', 'created_at', 'formed_at',
                  'completed_at', 'voting_date', 'total_votes',
                  'user', 'moderator', 'objects']

    def get_user(self, obj):
        return obj.user.username

    def get_moderator(self, obj):
        return obj.moderator.username


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
