
from django.urls import path

from .views import PendingDocumentsView, VerifyOwnerKYC

urlpatterns = [
    path(
        "admin_document_view/",
        PendingDocumentsView.as_view(),
        name="admin_document"
    ),

    path(
        "verify-owner/<int:user_id>/",
        VerifyOwnerKYC.as_view(),
        name="verify_owner"
    ),
]