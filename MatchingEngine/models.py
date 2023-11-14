from django.db import models
from rest_framework import serializers

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateField()  # Created Date
    updated_at = models.DateField()  # Updated Date

class OrderBook(models.Model):
  id = models.BigAutoField(primary_key=True) # Unique Order ID
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  script = models.CharField(max_length=10) # IOCL, INFY
  side = models.CharField(max_length=5) # Sell / Buy
  price = models.DecimalField(decimal_places=4, max_digits = 100) # Price
  quantity = models.DecimalField(decimal_places=4, max_digits = 100) # Number of quantity ordered
  filled_quantity = models.DecimalField(decimal_places=4, max_digits = 100) # Filled Quantity
  remaining_quantity = models.DecimalField(decimal_places=4, max_digits = 100) # Remaining Quantity
  status = models.CharField(max_length=10, default='Pending') # Pending / Completed / Rejected
  created_at = models.DateField() # Created Date
  updated_at = models.DateField() # Updated Date

class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    buyer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_transactions')
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_transactions')
    price = models.DecimalField(decimal_places=4, max_digits = 100)
    quantity = models.DecimalField(decimal_places=4, max_digits = 100)
    script = models.CharField(max_length=10)
    created_at = models.DateField(auto_now=True)

class OrderBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderBook
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'