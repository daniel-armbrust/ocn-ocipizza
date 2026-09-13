from fastapi import APIRouter

from app.routes.cart_routes import router as cart_router
from app.routes.checkout_routes import router as checkout_router
from app.routes.home_routes import router as home_router
from app.routes.pizza_routes import router as pizza_router


router = APIRouter()
router.include_router(home_router)
router.include_router(pizza_router)
router.include_router(cart_router)
router.include_router(checkout_router)

__all__ = ["router"]
