"""
Serializers for the alert APIs.
"""
from rest_framework import serializers
from core.models import Alert, Symbol
from decimal import Decimal


class SymbolFieldSerializer(serializers.Field):
    def to_representation(self, instance) -> str:
        # This function is for the direction: Instance -> Dict
        # If you only need this, use a ReadOnlyField, or SerializerField
        return str(instance)

    def to_internal_value(self, data) -> Symbol:
        # This function is for the direction: Dict -> Instance
        # Here you can manipulate the data if you need to.
        return data


class PriceFieldSerializer(serializers.Field):
    def to_representation(self, instance) -> str:
        return str("{:f}".format(instance.normalize()))

    def to_internal_value(self, data) -> Decimal:
        return Decimal(data)


class SymbolSerializer(serializers.ModelSerializer):
    """Serializer for symbols"""

    last_price = PriceFieldSerializer() 

    class Meta:
        model = Symbol
        fields = [
            'id',
            'name',
            'last_price',
        ]
        read_only_fileds = ['id']
    

class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alerts"""

    symbol = SymbolFieldSerializer()
    price = PriceFieldSerializer()

    class Meta:
        model = Alert
        fields = [
            'id',
            'title',
            'symbol',
            'price',
            'condition',
            'is_active',
        ]
        read_only_fileds = ['id']

    def validate_symbol(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError(
                'The symbol has to be a Char field.')
        if value.upper() != value:
            raise serializers.ValidationError(
                'The symbol has to be in upper case.')

        return value

    def create(self, validated_data):
        """Override create method."""
        symbol_obj, _ = Symbol.objects.get_or_create(
            name=validated_data['symbol'])
        validated_data['symbol'] = symbol_obj
        validated_data['is_active'] = True
        alert = Alert.objects.create(**validated_data)
        return alert

    def update(self, instance, validated_data):
        """Override update method"""

        # make/get Symbol object from string-data
        symbol = validated_data.pop('symbol', None)
        if symbol:
            symbol_obj, _ = Symbol.objects.get_or_create(name=symbol)
            validated_data['symbol'] = symbol_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance