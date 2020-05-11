from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from dook.api.admin.permissions import IsAdmin
from dook.api.admin.serializers import (
    ExpertListSerializer,
    ExpertOpinionExtendedSerializer,
    FactCheckerListSerializer,
    FactCheckerOpinionExtendedSerializer,
    InvitationListSerializer,
    NewsDetailSerializer,
    NewsImageSerializer,
    NewsListSerializer,
    NewsUpdateSerializer,
    SensitiveKeywordManagementSerializer,
    UserDetailSerializer,
)
from dook.api.news.filters import AdminNewsFilter
from dook.api.users.filters import AdminUsersFilter
from dook.core.integrations.storage.client import S3ApiClient
from dook.core.news.models import (
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    SensitiveKeyword,
)
from dook.core.users.models import Invitation, User


class ExpertListView(generics.ListAPIView):
    permission_classes = (IsAdmin,)

    model = User
    serializer_class = ExpertListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering = ["-name"]
    search_fields = ["name", "email"]
    filterset_class = AdminUsersFilter

    def get_queryset(self):
        return self.model.objects.experts_with_opinions_count().with_assigned_news_count()


class FactCheckerListView(generics.ListAPIView):
    permission_classes = (IsAdmin,)

    model = User
    serializer_class = FactCheckerListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering = ["-name"]
    search_fields = ["name", "email"]
    filterset_class = AdminUsersFilter

    def get_queryset(self):
        return (
            self.model.objects.fact_checkers_with_opinions_count().with_assigned_news_count()
        )


class InvitationListView(generics.ListAPIView):
    permission_classes = (IsAdmin,)
    queryset = Invitation.objects.all()
    serializer_class = InvitationListSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAdmin,)
    serializer_class = UserDetailSerializer

    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(pk=self.kwargs["pk"])


class NewsListView(generics.ListAPIView):
    permission_classes = (IsAdmin,)
    serializer_class = NewsListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]
    filterset_class = AdminNewsFilter

    model = News

    def get_queryset(self):
        return (
            self.model.objects.prefetch_related("expertopinion")
            .with_news_verdict_status()
            .with_is_duplicate()
        )


class NewsDetailView(generics.RetrieveAPIView, generics.UpdateAPIView):
    http_method_names = ["get", "patch"]
    permission_classes = (IsAdmin,)
    serializer_class = NewsDetailSerializer
    serializer_action__class = {"PATCH": NewsUpdateSerializer}

    def get_serializer_class(self):
        return self.serializer_action__class.get(
            self.request.method, self.serializer_class
        )

    def get_queryset(self, *args, **kwargs):
        return (
            News.objects.filter(pk=self.kwargs["pk"])
            .with_fact_checker_opinions()
            .with_expert_opinions()
        )


class ExpertOpinionDetailView(generics.UpdateAPIView):
    http_method_names = ["put"]
    permission_classes = (IsAdmin,)
    serializer_class = ExpertOpinionExtendedSerializer
    queryset = ExpertOpinion.objects.all()


class FactCheckerOpinionDetailView(generics.UpdateAPIView):
    http_method_names = ["put"]
    permission_classes = (IsAdmin,)
    serializer_class = FactCheckerOpinionExtendedSerializer
    queryset = FactCheckerOpinion.objects.all()


class SensitiveKeywordListView(generics.ListCreateAPIView):
    permission_classes = (IsAdmin,)
    serializer_class = SensitiveKeywordManagementSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering = ["-name"]
    search_fields = ["name"]
    queryset = SensitiveKeyword.objects.all()


class SensitiveKeywordDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdmin,)
    serializer_class = SensitiveKeywordManagementSerializer
    queryset = SensitiveKeyword.objects.all()


class NewsImageView(generics.UpdateAPIView):
    permission_classes = (IsAdmin,)
    serializer_class = NewsImageSerializer
    queryset = News.objects.all()

    def patch(self, request, pk):
        self.s3_client = S3ApiClient()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news = self.get_object()
        news.attach_screenshot(image=serializer.validated_data["image"])

        return Response(status=status.HTTP_204_NO_CONTENT,)
