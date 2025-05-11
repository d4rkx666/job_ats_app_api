from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.security import get_current_user
from app.services.log_saver import setError
from app.services.stripe_service import stripe
from app.services.user_actions_manager import update_user_stripe, set_subscription
from app.core.config import settings
from app.models.schemas import CreateSubscriptionRequest
from app.services.user_actions_manager import getUserData


router = APIRouter()

@router.post("/create-subscription")
async def create_subcription(request: CreateSubscriptionRequest, user: dict = Depends(get_current_user)):

   # Response INIT
   response = {
      "success": True,
      "type_error": "",
      "subscription_id": None
   }

   try:

      validate_user_data = await getUserData(user["uid"])

      # Create or retrieve customer
      customers = stripe.Customer.list(email=validate_user_data["email"]).data
      customer = customers[0] if customers else stripe.Customer.create(
         email=validate_user_data["email"],
         payment_method=request.payment_method_id,
         invoice_settings={"default_payment_method": request.payment_method_id},
      )
      

      # Create subscription with trial
      subscription = stripe.Subscription.create(
         customer=customer.id,
         items=[{
               'price': "price_1RIgfP4EcbVoOhTGHpizvb6E",
         }],
         trial_period_days=7,
         payment_behavior="default_incomplete",
      )

      await update_user_stripe(validate_user_data["user_ref"],customer.id)
   
      response.update({
         "subscription_id": subscription.id
      })
      return response
   
   except stripe.error.StripeError as e:
      response.update({
            "success": False,
            "type_error": str(e)
      })
      return response
   except Exception as e:
      print(f"Unexpected error: {e}")
      response.update({
         "success": False,
         "type_error": "An unexpected error occurred"
      })
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
      print("Invoice was created successfully")
      pass
   elif event.type == "customer.subscription.created":
      print("New subscription created")
      subscription = event.data.object
      customer_id = subscription.get("customer")

      try:
         customer = stripe.Customer.retrieve(customer_id)
         email = customer.email 

         await set_subscription(email, True)  # Custom function to handle subscription status
      except stripe.error.StripeError as e:
         print(f"Error retrieving customer: {e}")
         setError(f"Subscription didn't created. Create it manually for this customer: {customer_id}")
      pass
   elif event.type == "customer.subscription.deleted":
      print("user canceled the subscription")
      pass

   return {"status": "success"}