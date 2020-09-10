from distutils.util import strtobool

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, views, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from dook.api.news.consts import MAX_TAG_COUNT_PER_NEWS
from dook.api.news.exceptions import TagCountPerNewsExceededException
from dook.api.news.management.exceptions import (
    AssigningNewsToInactiveUserException,
    NewsAlreadyAssignedException,
    NewsAlreadyAssignedToRequestedUserException,
)
from dook.api.news.management.filters import ManagementNewsFilter
from dook.api.news.management.serializers import (
    ExpertOpinionExtendedSerializer,
    FactCheckerOpinionExtendedSerializer,
    NewsAssignSerializer,
    NewsImageSerializer,
    NewsSerializer,
    NewsUpdateSerializer,
)
from dook.api.permissions import IsAdmin, IsExpert, IsModerator, IsSpecialist
from dook.core.integrations.storage.client import S3ApiClient
from dook.core.news.models import (
    Domain,
    ExpertOpinion,
    FactCheckerOpinion,
    News,
    NewsDomain,
    NewsTag,
    Tag,
)
from dook.core.users.constants import UserRoleType
from dook.core.users.email_service import (
    send_news_assignment_for_expert,
    send_news_dismissal_for_expert,
)
from dook.core.users.models import User, UserNews


class NewsViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ManagementNewsFilter
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]

    permission_classes = (IsAdmin | IsModerator,)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return NewsUpdateSerializer

        return NewsSerializer

    def get_queryset(self):
        qs = (
            News.objects.with_expert_opinions()
            .with_fact_checker_opinions()
            .with_news_verdict_status()
            .with_is_duplicate()
            .with_assigned_crew_members()
        )

        tags = self.request.query_params.getlist("tags[]")
        if tags:
            qs = qs.filter_by_related_tags(
                tags=[get_object_or_404(Tag, name=name) for name in tags]
            )

        domains = self.request.query_params.getlist("domains[]")
        if domains:
            qs = qs.filter_by_related_domains(
                domains=[get_object_or_404(Domain, name=domain) for domain in domains]
            )

        is_verified_by_expert = self.request.query_params.get("is_verified_by_expert")
        if is_verified_by_expert:
            try:
                qs = qs.verified_by_expert(
                    verified=bool(strtobool(is_verified_by_expert))
                )
            except ValueError:
                pass

        return qs

    def partial_update(self, request, *args, **kwargs):
        update_domains = True
        update_tags = True
        domains = []
        tags = []

        try:
            domains = set(request.data.pop("domains"))
        except KeyError:
            update_domains = False

        try:
            tags = set(request.data.pop("tags"))
        except KeyError:
            update_tags = False

        if len(tags) > MAX_TAG_COUNT_PER_NEWS:
            raise TagCountPerNewsExceededException

        news = self.get_object()

        if update_domains:
            domain_objects = [
                get_object_or_404(Domain.objects.all(), pk=domain_pk)
                for domain_pk in domains
            ]
            NewsDomain.objects.filter(news=news).delete()
            for domain in domain_objects:
                NewsDomain.objects.create(news=news, domain=domain)

        if update_tags:
            NewsTag.objects.filter(news=news).delete()
            tag_objects = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]
            for tag in tag_objects:
                NewsTag.objects.create(news=news, tag=tag)

        super().partial_update(request, args, kwargs)

        return Response(NewsSerializer(instance=news).data, status=status.HTTP_200_OK)


class ExpertOpinionDetailView(generics.UpdateAPIView):
    http_method_names = ["put"]
    serializer_class = ExpertOpinionExtendedSerializer
    queryset = ExpertOpinion.objects.all()

    permission_classes = (IsAdmin | IsModerator | IsExpert | IsSpecialist,)


class FactCheckerOpinionDetailView(generics.UpdateAPIView):
    http_method_names = ["put"]
    permission_classes = (IsAdmin | IsModerator,)
    serializer_class = FactCheckerOpinionExtendedSerializer
    queryset = FactCheckerOpinion.objects.all()


class NewsImageView(generics.UpdateAPIView):
    permission_classes = (IsAdmin | IsModerator,)
    serializer_class = NewsImageSerializer
    queryset = News.objects.all()

    def patch(self, request, pk):
        self.s3_client = S3ApiClient()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news = self.get_object()
        news.attach_screenshot(image=serializer.validated_data["image"])

        return Response(status=status.HTTP_204_NO_CONTENT,)


class NewsAssignView(views.APIView):
    permission_classes = (IsAdmin | IsModerator,)

    def patch(self, request, pk):
        news = get_object_or_404(News.objects.verified_by_expert(verified=False), pk=pk)
        serializer = NewsAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignee = User.objects.get(pk=serializer.data["assignee"])
        replace_assignee = serializer.data.get("replace_assignee")

        if not assignee.is_active:
            raise AssigningNewsToInactiveUserException

        try:
            user_news = UserNews.objects.get(
                news=news, user__role__in=(UserRoleType.EXPERT, UserRoleType.SPECIALIST)
            )

            if user_news.user == assignee:
                raise NewsAlreadyAssignedToRequestedUserException

            if not replace_assignee:
                raise NewsAlreadyAssignedException

            old_assignee = user_news.user
            user_news.delete()
            if old_assignee.allow_subscriptions:
                send_news_dismissal_for_expert(expert=old_assignee, news=news)

        except UserNews.DoesNotExist:
            pass

        UserNews.objects.create(
            news=news, user=assignee, assigned_by_email=request.user.email
        )
        if assignee.allow_subscriptions:
            send_news_assignment_for_expert(expert=assignee, news=news)

        return Response(status=status.HTTP_204_NO_CONTENT)


class NewsDismissView(views.APIView):
    permission_classes = (IsAdmin | IsModerator,)

    def delete(self, request, pk):
        news = get_object_or_404(News.objects.verified_by_expert(verified=False), pk=pk)

        try:
            user_news = UserNews.objects.get(
                news=news, user__role__in=(UserRoleType.EXPERT, UserRoleType.SPECIALIST)
            )

            old_assignee = user_news.user
            user_news.delete()
            if old_assignee.allow_subscriptions:
                send_news_dismissal_for_expert(expert=old_assignee, news=news)

        except UserNews.DoesNotExist:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)
