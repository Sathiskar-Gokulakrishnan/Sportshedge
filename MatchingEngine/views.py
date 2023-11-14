from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from MatchingEngine.models import User, OrderBook, Transaction, TransactionSerializer, OrderBookSerializer
from datetime import datetime
from django.db import transaction

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@transaction.atomic
def placeOrder(request):
    logger.info("placing order in process")
    try:
        if request.method != 'POST':
            logger.info(f"invalid request method found {request.method}")
            response = {
                "code" : 400,
                "message" : "invalidRequest",
                "data" : {}
            }
            return JsonResponse(response)

        form_data = request.POST
        userId = form_data.get("userId")
        script = form_data.get("script")  # IOCL, INFY
        side = form_data.get("side")  # Sell / Buy
        price = float(form_data.get("price"))  # Price
        quantity = float(form_data.get("quantity")) # Number of quantity ordered

        if None in [script, side, price, quantity, userId]:
            logger.info(f"invalid request params")
            response = {
                "code": 400,
                "message": "invalidRequest",
                "data": {}
            }
            return JsonResponse(response)


        """
        1. checking and try to match order in orders already in order table
        2. create new order in table
        """
        print(f"order type => {side}")
        status = "Processing"
        if side == 'BUY':
            # Try to found exact match orders
            orders = OrderBook.objects.filter(script=script, side= 'SELL', price=price, remaining_quantity__gte=quantity, status='Pending').order_by('quantity')
            if len(orders) > 0:
                for order in orders:
                    print(f"order mathcing found {order}")
                    if quantity <= 0:
                        break
                    elif quantity == float(order.remaining_quantity):
                        OrderBook.objects.filter(id=order.id).update(filled_quantity=float(order.filled_quantity) + quantity,
                                                                     remaining_quantity=0, status="Completed")
                        transaction = Transaction()
                        transaction.quantity = quantity
                        transaction.price = order.price
                        transaction.buyer_id = User(userId)
                        transaction.seller_id = User(order.user_id)
                        transaction.price = order.price
                        transaction.script = order.script
                        transaction.save()
                        status = "Completed"
                        break
                    elif quantity < float(order.remaining_quantity):
                        filledQuantity = quantity
                        quantity = float(order.remaining_quantity) - quantity
                        OrderBook.objects.filter(id=order.id).update(filled_quantity=float(order.filled_quantity) + filledQuantity,
                                                                     remaining_quantity=quantity)
                        transaction = Transaction()
                        transaction.quantity = filledQuantity
                        transaction.price = order.price
                        transaction.buyer_id = User(userId)
                        transaction.seller_id = User(order.user_id)
                        transaction.price = order.price
                        transaction.script = order.script
                        transaction.save()
                        break
            else:
                print("new buy order added")
                # need to mark remaining stocks as pending
                order = OrderBook()
                order.user_id = userId
                order.script = script
                order.side = side
                order.price = price
                order.quantity = order.remaining_quantity = quantity
                order.filled_quantity = 0
                order.created_at = datetime.utcnow()
                order.updated_at = datetime.utcnow()
                order.save()
                status = "Pending"

        elif side == 'SELL':
            # Try to found exact match orders
            orders = OrderBook.objects.filter(script=script, side='BUY', price=price, remaining_quantity__lte=quantity,
                                              status='Pending').order_by('quantity')
            if len(orders) > 0:
                for order in orders:
                    print(f"order mathcing found {order}")
                    if quantity <= 0:
                        break
                    elif quantity == float(order.remaining_quantity):
                        OrderBook.objects.filter(id=order.id).update(
                            filled_quantity=float(order.filled_quantity) + quantity,
                            remaining_quantity=0, status="Completed")
                        transaction = Transaction()
                        transaction.quantity = quantity
                        transaction.price = order.price
                        transaction.buyer_id = User(userId)
                        transaction.seller_id = User(order.user_id)
                        transaction.price = order.price
                        transaction.script = order.script
                        transaction.save()
                        status = "Completed"
                        break
                    elif quantity > float(order.remaining_quantity):
                        filledQuantity = float(order.remaining_quantity)
                        quantity = quantity - filledQuantity
                        OrderBook.objects.filter(id=order.id).update(
                            filled_quantity=float(order.filled_quantity) + filledQuantity,
                            remaining_quantity=0, status="Completed")
                        transaction = Transaction()
                        transaction.quantity = filledQuantity
                        transaction.price = order.price
                        transaction.buyer_id = User(userId)
                        transaction.seller_id = User(order.user_id)
                        transaction.price = order.price
                        transaction.script = order.script
                        transaction.save()
            else:
                print("new buy order added")
                # need to mark remaining stocks as pending
                order = OrderBook()
                order.user_id = userId
                order.script = script
                order.side = side
                order.price = price
                order.quantity = order.remaining_quantity = quantity
                order.filled_quantity = 0
                order.created_at = datetime.utcnow()
                order.updated_at = datetime.utcnow()
                order.save()
                status = "Pending"
        orderId = 1
        logger.info(f"order successfully marked {orderId}")
        response = {
            "code": 200,
            "message": "success",
            "data": {
                "orderId" : orderId,
                "status" : status
            }
        }
        return JsonResponse(response)
    except Exception as err:
        logger.error(f"error while place order {err}")
        response = {
            "code" : 500,
            "message" : "internalServerError",
            "data" : {}
        }
        return JsonResponse(response)

@csrf_exempt
def getAllOrder(request):
    try:
        data = OrderBookSerializer(OrderBook.objects.all(), many = True).data
        print(data)
        return JsonResponse(data, safe=False)
    except Exception as err:
        logger.error(f"error while get all orders {err}")
        response = {
            "code": 500,
            "message": "internalServerError",
            "data": {}
        }
        return JsonResponse(response)

def getAllTransactions(request):
    try:
        data = TransactionSerializer(Transaction.objects.all(), many=True).data
        print(data)
        return JsonResponse(data, safe=False)
    except Exception as err:
        logger.error(f"error while get all transactions {err}")
        response = {
            "code": 500,
            "message": "internalServerError",
            "data": {}
        }
        return JsonResponse(response)

def getOrderStatus(request):
    try:
        if request.method != 'POST':
            logger.info(f"invalid request method found {request.method}")
            response = {
                "code": 400,
                "message": "invalidRequest",
                "data": {}
            }
            return JsonResponse(response)

        form_data = request.POST
        obj = OrderBook.objects.get(pk=form_data.id)

        if obj is None or len(obj) == 0:
            response = {
                "code": 400,
                "message": "notFound",
                "data": {
                }
            }

        response = {
            "code" : 200,
            "message" : "success",
            "data" : {
                "orderId" : obj.id,
                "status" : obj.status
            }
        }
    except Exception as err:
        logger.error(f"error while get order status {err}")
        response = {
            "code": 500,
            "message": "internalServerError",
            "data": {}
        }
        return JsonResponse(response)

    return JsonResponse(response)


@csrf_exempt
@transaction.atomic
def createUser(request):
    try:
        if request.method != 'POST':
            logger.info(f"invalid request method found {request.method}")
            response = {
                "code": 400,
                "message": "invalidRequest",
                "data": {}
            }
            return JsonResponse(response)
        form_data = request.POST
        name = form_data.get("name")
        print(f"name => {name}")
        user = User()
        user.name = name
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        user.save()

        response = {
            "code" : 200,
            "message" : "success",
            "data" : {
                "name" : name
            }
        }

        return JsonResponse(response)

    except Exception as err:
        logger.error(f"error while create user {err}")
        response = {
            "code": 500,
            "message": "internalServerError",
            "data": {
            }
        }
        return JsonResponse(response)
    

