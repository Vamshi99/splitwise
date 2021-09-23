from rest_framework import serializers
from expense_tracker.models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        # fields = ('id', 'name', 'email')


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = "__all__"
        # fields = ('id', 'name', 'description', 'groupId')

class GroupSerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(required=False, many=True)
    class Meta:
        model = Group
        fields = "__all__"
        # fields = ('id', 'name', 'description')

class GroupToUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupToUser
        fields = "__all__"
        