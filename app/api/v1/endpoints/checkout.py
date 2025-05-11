from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.security import get_current_user
from app.services.stripe_service import stripe
from app.services.user_actions_manager import update_user_stripe, set_subscription
from app.core.config import settings
from app.models.schemas import CreateSubscriptionRequest
from app.services.user_actions_manager import getUserData


router = APIRouter()

@router.post("/create-session")
async def create_checkout_session(user: dict = Depends(get_current_user)):

   # Response INIT
   response = {
      "success": True,
      "type_error": "",
      "session_id": None
   }

   try:
      
      validate_user_data = await getUserData(user["uid"])

      # Create or retrieve customer
      customers = stripe.Customer.list(email=validate_user_data["email"]).data
      customer = customers[0] if customers else stripe.Customer.create(
         email=validate_user_data["email"]
      )

      session = stripe.checkout.Session.create(
         payment_method_types=['card'],
         line_items=[{
               'price': 'price_1RNK4a4EcbVoOhTGDZ4zPYHT',
               'quantity': 1,
         }],
         mode='subscription',¿
         customer=customer.id,
         success_url=settings.stripe_success_endpoint,
         cancel_url=settings.stripe_cancel_endpoint,
      )

      await update_user_stripe(validate_user_data["user_ref"],customer.id)

      response.update({
         "session_id":session.id
      })

   except Exception as e:
      response.update({
         "success": False,
         "type_error": e
      })
   finally:
      return response


@router.post("/stripe-webhook")
async def handle_webhook(request: Request):
   payload = await request.body()
   sig_header = request.headers.get("stripe-signature")
   event = None
   
   try:
      event = stripe.Webhook.construct_event(
         payload, sig_header, settings.stripe_signing_secret_key
      )
   except ValueError as e:
      raise HTTPException(status_code=400, detail=str(e))
   except stripe.error.SignatureVerificationError as e:
      raise HTTPException(status_code=400, detail=str(e))

   # Handle events
   if event.type == "invoice.payment_succeeded":
      print("New invoice created")
      pass
   elif event.type == "customer.subscription.created":
      print("New subscription created")
      subscription = event.data.object
      customer_id = subscription.get("customer")

      print(f"setting subs to {customer_id}")
      await set_subscription(customer_id, True)
      pass
   elif event.type == "customer.subscription.deleted":
      print("User canceled the subscription")
      pass

   return {"status": "success"}