import graphene
import graphene_django_optimizer as gql_optimizer
from django.db.models import QuerySet

from ...core.permissions import ProductPermissions
from ...warehouse import models
from ..core.fields import FilterInputConnectionField
from ..decorators import permission_required
from ..utils import sort_queryset
from .filters import StockFilterInput, WarehouseFilterInput
from .mutations import (
    WarehouseCreate,
    WarehouseDelete,
    WarehouseShippingZoneAssign,
    WarehouseShippingZoneUnassign,
    WarehouseUpdate,
)
from .sorters import WarehouseSortField, WarehouseSortingInput
from .types import Stock, Warehouse


def sort_warehouses(qs: QuerySet, sort_by: WarehouseSortingInput) -> QuerySet:
    if sort_by:
        return sort_queryset(qs, sort_by, WarehouseSortField)
    return qs.order_by("name")


class WarehouseQueries(graphene.ObjectType):
    warehouse = graphene.Field(
        Warehouse,
        description="Look up a warehouse by ID.",
        id=graphene.Argument(
            graphene.ID, description="ID of an warehouse", required=True
        ),
    )
    warehouses = FilterInputConnectionField(
        Warehouse,
        description="List of warehouses.",
        filter=WarehouseFilterInput(),
        sort_by=WarehouseSortingInput(),
    )

    @permission_required(ProductPermissions.MANAGE_PRODUCTS)
    def resolve_warehouse(self, info, **data):
        warehouse_pk = data.get("id")
        warehouse = graphene.Node.get_node_from_global_id(info, warehouse_pk, Warehouse)
        return warehouse

    @permission_required(ProductPermissions.MANAGE_PRODUCTS)
    def resolve_warehouses(self, info, sort_by=None, **kwargs):
        qs = models.Warehouse.objects.all()
        qs = sort_warehouses(qs, sort_by)
        return gql_optimizer.query(qs, info)


class WarehouseMutations(graphene.ObjectType):
    create_warehouse = WarehouseCreate.Field()
    update_warehouse = WarehouseUpdate.Field()
    delete_warehouse = WarehouseDelete.Field()
    assign_warehouse_shipping_zone = WarehouseShippingZoneAssign.Field()
    unassign_warehouse_shipping_zone = WarehouseShippingZoneUnassign.Field()


class StockQueries(graphene.ObjectType):
    stock = graphene.Field(
        Stock,
        description="Look up a stock by ID",
        id=graphene.ID(required=True, description="ID of an warehouse"),
    )
    stocks = FilterInputConnectionField(
        Stock, description="List of stocks.", filter=StockFilterInput()
    )

    @permission_required(ProductPermissions.MANAGE_PRODUCTS)
    def resolve_stock(self, info, **kwargs):
        stock_id = kwargs.get("id")
        stock = graphene.Node.get_node_from_global_id(info, stock_id, Stock)
        return stock

    @permission_required(ProductPermissions.MANAGE_PRODUCTS)
    def resolve_stocks(self, info, **data):
        qs = models.Stock.objects.all()
        return gql_optimizer.query(qs, info)
