from django.urls import path
from .admin_api import AccessRulesListView, AccessRuleDetailView

app_name = 'admin_api'

urlpatterns = [
    path('access-rules/', AccessRulesListView.as_view(), name='access_rules_list'),
    path('access-rules/<int:pk>/', AccessRuleDetailView.as_view(), name='access_rule_detail'),
]
