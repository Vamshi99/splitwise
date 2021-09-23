from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=1024)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=5000)

    def __str__(self):
        return self.name


class GroupToUser(models.Model):
    groupId = models.ForeignKey(Group, on_delete=CASCADE)
    userId = models.ForeignKey(User, on_delete=CASCADE)

    class Meta:
        unique_together = ('groupId', 'userId',)

    def __str__(self):
        return "Group: " + self.groupId.name + " => User " + self.userId.name

class Balance(models.Model):
    group = models.ForeignKey(Group, on_delete=CASCADE,default=1)
    sender = models.ForeignKey(User, on_delete=CASCADE, related_name='sending_user')
    receiver = models.ForeignKey(User, on_delete=CASCADE, related_name='receiving_user')
    amount = models.DecimalField(default=0.0,decimal_places=2,max_digits=20)

    class Meta:
        unique_together = ('sender', 'receiver','group',)

class Expense(models.Model):
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=5000)
    groupId = models.ForeignKey(Group, on_delete=CASCADE)
    payeeId = models.ForeignKey(User, on_delete=CASCADE, default=1)
    amount = models.DecimalField(default=0.0,decimal_places=2,max_digits=20)

    def __str__(self):
        return self.name

class ExpenseToUsers(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=CASCADE)
    userId = models.ForeignKey(User, on_delete=CASCADE)
    userAmount = models.DecimalField(default=0.0,decimal_places=2,max_digits=20)

    # def __str__(self):

        # return self.expenseId + " " + self.userId + " " + self.expenseRatio