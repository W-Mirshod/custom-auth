from django.urls import path
from .views import ProductsListView, ShopsListView, OrdersListView

app_name = 'mock_business'

urlpatterns = [
    path('products/', ProductsListView.as_view(), name='products'),
    path('shops/', ShopsListView.as_view(), name='shops'),
    path('orders/', OrdersListView.as_view(), name='orders'),
]
