"""Stream type classes for tap-etsy."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_etsy.client import etsyStream

class ShopTransactionStream(etsyStream):
    name = "shop_transactions"
    path = "/transactions"
    pagination = False
    primary_keys = ["transaction_id"]
    schema = th.PropertiesList(
        th.Property("transaction_id", th.IntegerType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("seller_user_id", th.IntegerType),
        th.Property("buyer_user_id", th.IntegerType),
        th.Property("create_timestamp", th.IntegerType),
        th.Property("created_timestamp", th.IntegerType),
        th.Property("paid_timestamp", th.IntegerType),
        th.Property("shipped_timestamp", th.IntegerType),
        th.Property("quantity", th.IntegerType),
        th.Property("listing_image_id", th.IntegerType),
        th.Property("receipt_id", th.IntegerType),
        th.Property("is_digital", th.BooleanType),
        th.Property("file_data", th.StringType),
        th.Property("listing_id", th.IntegerType),
        th.Property("transaction_type", th.StringType),
        th.Property("product_id", th.IntegerType),
        th.Property("sku", th.StringType),
        th.Property("price", th.ObjectType(
            th.Property("amount", th.IntegerType),
            th.Property("divisor", th.IntegerType),
            th.Property("currency_code", th.StringType)
        )),
        th.Property("shipping_cost", th.ObjectType(
            th.Property("amount", th.IntegerType),
            th.Property("divisor", th.IntegerType),
            th.Property("currency_code", th.StringType)
        )),
        th.Property("variations", th.ArrayType(th.ObjectType(
            th.Property("property_id", th.IntegerType),
            th.Property("value_id", th.IntegerType),
            th.Property("formatted_name", th.StringType),
            th.Property("formatted_value", th.StringType)
        ))),
        th.Property("product_data", th.ArrayType(th.ObjectType(
            th.Property("property_id", th.IntegerType),
            th.Property("property_name", th.StringType),
            th.Property("scale_id", th.IntegerType),
            th.Property("scale_name", th.StringType),
            th.Property("value_ids", th.ArrayType(th.IntegerType)),
            th.Property("values", th.ArrayType(th.StringType))
        ))),
        th.Property("shipping_profile_id", th.IntegerType),
        th.Property("min_processing_days", th.IntegerType),
        th.Property("max_processing_days", th.IntegerType),
        th.Property("shipping_method", th.StringType),
        th.Property("shipping_upgrade", th.StringType),
        th.Property("expected_ship_date", th.IntegerType),
        th.Property("buyer_coupon", th.IntegerType),
        th.Property("shop_coupon", th.IntegerType)
    ).to_dict()


