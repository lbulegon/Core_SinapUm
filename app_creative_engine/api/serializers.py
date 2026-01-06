"""
Serializers DRF para Creative Engine API
"""
from rest_framework import serializers


class GenerateCreativeSerializer(serializers.Serializer):
    """Serializer para gerar criativo"""
    product_id = serializers.CharField(max_length=128)
    shopper_id = serializers.CharField(max_length=128)
    channel = serializers.ChoiceField(choices=["status", "group", "private"])
    locale = serializers.CharField(max_length=10, default="pt-BR", required=False)
    tone = serializers.ChoiceField(
        choices=["direto", "elegante", "popular", "premium", "urgente"],
        default="direto",
        required=False
    )
    audience_hint = serializers.CharField(max_length=200, required=False, allow_blank=True)
    time_of_day = serializers.ChoiceField(
        choices=["morning", "afternoon", "night"],
        required=False,
        allow_null=True
    )
    stock_level = serializers.ChoiceField(
        choices=["low", "normal", "high"],
        required=False,
        allow_null=True
    )
    price_sensitivity = serializers.ChoiceField(
        choices=["low", "medium", "high"],
        required=False,
        allow_null=True
    )
    campaign_tag = serializers.CharField(max_length=100, required=False, allow_blank=True)


class GenerateVariantsSerializer(serializers.Serializer):
    """Serializer para gerar variantes"""
    creative_id = serializers.CharField(max_length=128)
    strategies = serializers.ListField(
        child=serializers.ChoiceField(choices=["price", "benefit", "urgency", "scarcity", "social_proof"]),
        min_length=1
    )
    channel = serializers.ChoiceField(choices=["status", "group", "private"])
    locale = serializers.CharField(max_length=10, default="pt-BR", required=False)
    tone = serializers.ChoiceField(
        choices=["direto", "elegante", "popular", "premium", "urgente"],
        default="direto",
        required=False
    )


class AdaptCreativeSerializer(serializers.Serializer):
    """Serializer para adaptar criativo"""
    variant_id = serializers.CharField(max_length=128)
    channel = serializers.ChoiceField(choices=["status", "group", "private"])
    locale = serializers.CharField(max_length=10, default="pt-BR", required=False)
    tone = serializers.ChoiceField(
        choices=["direto", "elegante", "popular", "premium", "urgente"],
        default="direto",
        required=False
    )


class PerformanceEventSerializer(serializers.Serializer):
    """Serializer para registrar performance"""
    variant_id = serializers.CharField(max_length=128)
    creative_id = serializers.CharField(max_length=128, required=False)
    product_id = serializers.CharField(max_length=128)
    shopper_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    type = serializers.ChoiceField(
        choices=["VIEWED", "RESPONDED", "INTERESTED", "ORDERED", "CONVERTED", "IGNORED"]
    )
    data = serializers.DictField(required=False, default=dict)
    correlation_id = serializers.UUIDField(required=False, allow_null=True)


class RecommendNextSerializer(serializers.Serializer):
    """Serializer para recomendar próximo criativo"""
    shopper_id = serializers.CharField(max_length=128)
    product_id = serializers.CharField(max_length=128)
    channel = serializers.ChoiceField(choices=["status", "group", "private"])
    locale = serializers.CharField(max_length=10, default="pt-BR", required=False)
    tone = serializers.ChoiceField(
        choices=["direto", "elegante", "popular", "premium", "urgente"],
        default="direto",
        required=False
    )
