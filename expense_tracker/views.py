from decimal import *
from expense_tracker.serializers import *
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .models import *
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

@api_view(['GET','POST'])
def users(request):
    if request.method == 'GET':
        id = request.query_params.get('id', None)
        if id is not None:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return HttpResponse(status=404)
            serializer = UserSerializer(user)
            return JsonResponse(serializer.data)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        user_data = JSONParser().parse(request)
        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
def groups(request):
    if request.method == 'GET':
        id = request.query_params.get('id', None)
        if id is not None:
            try:
                group = Group.objects.get(id=id)
            except Group.DoesNotExist:
                return HttpResponse(status=404)
            serializer = GroupSerializer(group)
            return JsonResponse(serializer.data)
        else:
            groups = Group.objects.all()
            serializer = GroupSerializer(groups, many=True)
            return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        group_data = JSONParser().parse(request)
        serializer = GroupSerializer(data=group_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# def addUserToGroup(request, groupID, userID):
def addUserToGroup(request):
        # user_data = JSONParser().parse(request)
        # if 'users' not in user_data:
        #     return JsonResponse("No user data provided", status=status.HTTP_400_BAD_REQUEST)            
        addUser_data = JSONParser().parse(request)
        try:
            user = User.objects.get(id=addUser_data['user_id'])
            userID = user.id
            group = Group.objects.get(id=addUser_data['group_id'])
            groupID=group.id
        except User.DoesNotExist:
            return JsonResponse({"message": "User Not found"}, status=404)
        except Group.DoesNotExist:
            return JsonResponse({"message": "Group Not found"}, status=404)
        except ValueError:
            return JsonResponse({"message": "Error parsing input data"}, status=400)

        if GroupToUser.objects.filter(groupId=group, userId=user).count() > 0:
                return JsonResponse({"message": "User already present in the group"}, status=status.HTTP_201_CREATED)

        obj = GroupToUser.objects.create(groupId=group, userId=user)
        obj.save()

        user_ids = []
        for each in GroupToUser.objects.filter(groupId=groupID):
            user_ids.append(each.userId.id)
        result=dict({'group_id': groupID, 'user_ids': user_ids})
        return JsonResponse(result, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def getUsersInGroup(request, groupID):
        try:
            group = Group.objects.get(id=groupID)
        except Group.DoesNotExist:
            return JsonResponse({"message": "Group Not found"}, status=404)

        user_ids = []
        for each in GroupToUser.objects.filter(groupId=groupID):
            user_ids.append(each.userId.id)
        result=dict({'user_ids': user_ids})
        return JsonResponse(result, status=status.HTTP_200_OK)

@api_view(['POST'])
def expenses(request):
        expense_data = JSONParser().parse(request)
        expenseRatios = expense_data.pop("usersExpenseMap")
        serializer = ExpenseSerializer(data=expense_data)
        if serializer.is_valid():
            if sum(expenseRatios.values())!=expense_data['amount']:
                error_map = {"usersExpenseMap": "Sum of all user expense Map amounts should equal total expense amount."}
                return JsonResponse(error_map, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            exp_db_obj = Expense.objects.get(id=serializer.data['id'])
            for userId, userAmount in expenseRatios.items():
                # Update Expense TO User Table
                usr_db_obj = User.objects.get(id=userId)
                userAmount = Decimal(userAmount)
                obj = ExpenseToUsers.objects.create(expenseId=exp_db_obj,userId=usr_db_obj, userAmount=userAmount)
                obj.save()
                # Update Balances need to be settled
                if not updateBalance(usr_db_obj, exp_db_obj.payeeId, userAmount):
                    error_map = {
                        "error": "Some issue occurred updating the balances, please try again."
                    }
                    return JsonResponse(error_map, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def updateBalance(sender, receiver, amount):
    try:
        # if sender and receiver are same, do nothing
        if(sender.id==receiver.id):
            return True
        reverseCount = Balance.objects.filter(sender=receiver, receiver=sender).count()
        if reverseCount == 1:
            # temp = receiver
            # sender = receiver
            # receiver = temp
            amount=-amount
            obj = Balance.objects.get(sender=receiver, receiver=sender)
            if ((obj.amount+amount)==0): 
                obj.delete()
            else:
                obj.amount = obj.amount+amount
                obj.save()
                # obj.update(amount=obj.amount+amount)
            return True

        if Balance.objects.filter(sender=sender, receiver=receiver).count() == 1:
            obj = Balance.objects.get(sender=sender, receiver=receiver)
            if ((obj.amount+amount)==0): 
                obj.delete()
            else:
                obj.amount = obj.amount+amount
                obj.save()
                # obj.update(amount=obj.amount+amount)
        else:
            obj = Balance.objects.create(sender=sender, receiver=receiver,amount=amount)
            obj.save()
    except Exception:
        return False
    return True

@api_view(['POST'])
# def payAmount(request, groupID, senderUserID, receiverUserID, amount):
def payAmount(request):
    pay_data = JSONParser().parse(request)
    try:
        sender = User.objects.get(id=pay_data['sender_id'])
        receiver = User.objects.get(id=pay_data['receiver_id'])
        amount = Decimal(pay_data['amount'])
    except User.DoesNotExist:
        return HttpResponse("Given User doesn't exist",status=404)
    except ValueError:
        return HttpResponse("Amount should be upto two decimal places",status=400)

    if updateBalance(receiver, sender, amount):
        success_message = sender.name + " paid " + receiver.name + " Rs " + str(amount) + " successfully."
        print(success_message)
        return JsonResponse({"message":success_message})
    else:
        error_map = {
            "error": "Some issue occurred updating the balances, please try again."
        }
        return JsonResponse(error_map, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def settlements(request, groupID, userID):
    try:
        user = User.objects.get(id=userID)
    except User.DoesNotExist:
        return HttpResponse("Given User doesn't exist",status=404)
    result = dict()
    sendingBalances = Balance.objects.filter(sender=user)
    receivingBalances = Balance.objects.filter(receiver=user)
    toReceiveFromUsers = dict()
    toPayUsers = dict()
    result['user_id']=userID

    if (sendingBalances.count() > 0):
        for balance in sendingBalances:
            if balance.amount >= 0:
                toPayUsers[str(balance.receiver)] = balance.amount
            else:
                toReceiveFromUsers[str(balance.sender)] = -1*balance.amount
        result["AmountToBePaid"] = toPayUsers
    if(receivingBalances.count() > 0):
        for balance in receivingBalances:
            if balance.amount >=0:
                toReceiveFromUsers[str(balance.sender)] = balance.amount
            else:
                toPayUsers[str(balance.sender)] = -1*balance.amount
        result["AmountToBeReceived"] = toReceiveFromUsers
    return JsonResponse(result, status=status.HTTP_200_OK) 