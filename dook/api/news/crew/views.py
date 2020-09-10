from distutils.util import strtobool

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, views
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from dook.api.news.consts import MAX_TAG_COUNT_PER_NEWS
from dook.api.news.crew.filters import ExpertNewsFilter, FactCheckerNewsFilter
from dook.api.news.crew.serializers import (
    ExpertNewsSerializer,
    ExpertNewsTagsUpdateSerializer,
    ExpertOpinionSerializer,
    FactCheckerNewsSerializer,
    FactCheckerOpinionSerializer,
)
from dook.api.news.errors import INVALID_EXPERT_NEWS_TAGS_INPUT
from dook.api.news.exceptions import TagCountPerNewsExceededException
from dook.api.permissions import IsExpert, IsFactChecker, IsModerator, IsSpecialist
from dook.core.news.models import Domain, News, NewsDomain, NewsTag, Tag
from dook.core.users.constants import UserRoleType
from dook.core.users.email_service import send_news_assignment_rejection_for_assignor
from dook.core.users.models import User, UserNews


class ExpertNewsViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = ExpertNewsSerializer
    permission_classes = (IsExpert | IsSpecialist,)
    filterset_class = ExpertNewsFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["reported_at"]
    ordering = ["-reported_at"]
    search_fields = ["text"]

    def get_queryset(self):
        qs = (
            News.objects.with_fact_checker_opinions()
            .with_expert_opinions()
            .with_verdicts()
            .with_is_duplicate()
            .with_is_spam()
            .with_assigned_to_me(user=self.request.user)
            .with_assigned_crew_members()
            .filter(is_published=False)
        )

        is_verified = self.request.query_params.get("is_verified")
        if is_verified:
            try:
                qs = qs.verified_by_expert(verified=bool(strtobool(is_verified)))
            except ValueError:
                pass

        tags = self.request.query_params.getlist("tags[]")
        if tags:
            qs = qs.filter_by_related_tags(
                tags=[get_object_or_404(Tag, name=name) for name in tags]
            )

        if self.request.user.role == UserRoleType.EXPERT:
            domains = self.request.query_params.getlist("domains[]")
            if domains:
                qs = qs.filter_by_related_domains(
                    domains=[get_object_or_404(Domain, name=domain) for domain in domains]
                )

            return qs

        news_ids = NewsDomain.objects.filter(domain=self.request.user.domain).values_list(
            "news", flat=True
        )
        qs = qs.filter(id__in=news_ids)

        assigned_to_me_qs = News.objects.with_assigned_to_me(
            user=self.request.user
        ).filter(is_assigned_to_me=True)

        return qs | assigned_to_me_qs


class ExpertNewsCreateOpinionView(views.APIView):
    lookup_url_kwarg = "pk"
    permission_classes = (IsModerator | IsExpert | IsSpecialist,)

    def post(self, request, pk):
        news_instance = get_object_or_404(
            News.objects.with_fact_checker_opinions().verified_by_expert(verified=False),
            pk=pk,
        )

        serializer = ExpertOpinionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        opinion = news_instance.leave_opinion(
            user=self.request.user, opinion_params=serializer.validated_data
        )

        if news_instance.is_with_verdict():
            news_instance.refresh_from_db()
            news_instance.events.new_verdict()

        serializer = ExpertOpinionSerializer(instance=opinion)
        return Response(serializer.data, status=HTTP_201_CREATED)


class ExpertNewsAssignTagsView(views.APIView):
    lookup_url_kwarg = "pk"
    permission_classes = (IsExpert | IsSpecialist,)

    def patch(self, request, pk):
        news_instance = get_object_or_404(
            News.objects.with_fact_checker_opinions()
            .with_expert_opinions()
            .with_verdicts()
            .with_is_duplicate()
            .with_is_spam()
            .filter(is_published=False)
            .with_assigned_crew_members(),
            pk=pk,
        )

        serializer = ExpertNewsTagsUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError({"detail": INVALID_EXPERT_NEWS_TAGS_INPUT})

        tags = request.data["tags"]
        if len(tags) > MAX_TAG_COUNT_PER_NEWS:
            raise TagCountPerNewsExceededException

        NewsTag.objects.filter(news=news_instance).delete()
        tag_objects = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]
        for tag in tag_objects:
            NewsTag.objects.create(news=news_instance, tag=tag)

        return Response(ExpertNewsSerializer(news_instance).data)


class ExpertNewsDismissAssignmentView(views.APIView):
    lookup_url_kwarg = "pk"
    permission_classes = (IsExpert | IsSpecialist,)

    def patch(self, request, pk):
        news_instance = get_object_or_404(News, pk=pk)

        try:
            user_news = UserNews.objects.get(news=news_instance, user=request.user)

            assignor = User.objects.filter(email=user_news.assigned_by_email).first()
            if user_news.assigned_by_email and assignor and assignor.allow_subscriptions:
                send_news_assignment_rejection_for_assignor(
                    assignee=request.user,
                    news=news_instance,
                    assignor_email=user_news.assigned_by_email,
                )

            user_news.delete()

        except UserNews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FactCheckerNewsViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = FactCheckerNewsSerializer
    permission_classes = (IsFactChecker,)
    filterset_class = FactCheckerNewsFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["assigned_at"]
    ordering = ["-assigned_at"]
    search_fields = ["text"]

    def get_queryset(self):
        qs = (
            News.objects.for_user(self.request.user)
            .with_has_user_opinion(self.request.user)
            .with_assigned_at(self.request.user)
            .with_verdicts()
            .filter(current_verdict__in=["no_verdict", "dispute"])
        )

        tags = self.request.query_params.getlist("tags[]")
        if tags:
            qs = qs.filter_by_related_tags(
                tags=[get_object_or_404(Tag, name=name) for name in tags]
            )

        return qs


class FactCheckerNewsCreateOpinionView(views.APIView):
    lookup_url_kwarg = "pk"
    permission_classes = (IsFactChecker,)

    def post(self, request, pk):
        news_instance = get_object_or_404(
            News.objects.for_user(self.request.user)
            .with_has_user_opinion(self.request.user)
            .with_assigned_at(self.request.user)
            .with_verdicts()
            .filter(current_verdict__in=["no_verdict", "dispute"]),
            pk=pk,
        )

        serializer = FactCheckerOpinionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        opinion = news_instance.leave_opinion(
            user=self.request.user, opinion_params=serializer.validated_data
        )

        if news_instance.is_with_verdict():
            news_instance.refresh_from_db()
            news_instance.events.new_verdict()

        serializer = FactCheckerOpinionSerializer(instance=opinion)
        return Response(serializer.data, status=HTTP_201_CREATED)
