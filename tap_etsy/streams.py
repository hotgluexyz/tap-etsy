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

class ShopListingStream(etsyStream):
    name = "shop_listings"
    path = "/listings"
    pagination = False
    primary_keys = ["listing_id"]
    schema = th.PropertiesList(
        th.Property("transaction_id", th.IntegerType),
        th.Property("listing_id", th.IntegerType),
        th.Property("user_id", th.IntegerType),
        th.Property("shop_id", th.IntegerType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("state", th.StringType),
        th.Property("creation_timestamp", th.IntegerType),
        th.Property("created_timestamp", th.IntegerType),
        th.Property("ending_timestamp", th.IntegerType),
        th.Property("original_creation_timestamp", th.IntegerType),
        th.Property("last_modified_timestamp", th.IntegerType),
        th.Property("updated_timestamp", th.IntegerType),
        th.Property("state_timestamp", th.IntegerType),
        th.Property("quantity", th.IntegerType),
        th.Property("shop_section_id", th.IntegerType),
        th.Property("featured_rank", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("num_favorers", th.IntegerType),
        th.Property("non_taxable", th.BooleanType),
        th.Property("is_taxable", th.BooleanType),
        th.Property("is_customizable", th.BooleanType),
        th.Property("is_personalizable", th.BooleanType),
        th.Property("personalization_is_required", th.BooleanType),
        th.Property("personalization_char_count_max", th.IntegerType),
        th.Property("personalization_instructions", th.StringType),
        th.Property("listing_type", th.StringType),
        th.Property("tags", th.CustomType({"type": ["array", "string"]})),
        th.Property("materials", th.CustomType({"type": ["array", "string"]})),
        th.Property("shipping_profile_id", th.IntegerType),
        th.Property("return_policy_id", th.IntegerType),
        th.Property("processing_min", th.IntegerType),
        th.Property("processing_max", th.IntegerType),
        th.Property("who_made", th.StringType),
        th.Property("when_made", th.StringType),
        th.Property("is_supply", th.BooleanType),
        th.Property("item_weight", th.IntegerType),
        th.Property("item_weight_unit", th.StringType),
        th.Property("item_length", th.IntegerType),
        th.Property("item_width", th.IntegerType),
        th.Property("item_height", th.IntegerType),
        th.Property("item_dimensions_unit", th.StringType),
        th.Property("is_private", th.BooleanType),
        th.Property("style", th.CustomType({"type": ["array", "string"]})),
        th.Property("file_data", th.StringType),
        th.Property("has_variations", th.BooleanType),
        th.Property("should_auto_renew", th.BooleanType),
        th.Property("language", th.StringType),
        th.Property("price", th.CustomType({"type": ["object", "string"]})),
        th.Property("taxonomy_id", th.IntegerType),
        th.Property("shipping_profile", th.CustomType({"type": ["object", "string"]})),
        th.Property("user", th.CustomType({"type": ["object", "string"]})),
        th.Property("price", th.CustomType({"type": ["object", "string"]})),
        th.Property("shop", th.CustomType({"type": ["object", "string"]})),
        th.Property("inventory", th.CustomType({"type": ["object", "string"]})),
        th.Property("images", th.CustomType({"type": ["array", "string"]})),            
        th.Property("videos", th.CustomType({"type": ["array", "string"]})),            
        th.Property("production_partners", th.CustomType({"type": ["array", "string"]})),            
        th.Property("skus", th.CustomType({"type": ["array", "string"]})),            
        th.Property("translations", th.CustomType({"type": ["array", "string"]})),            
        th.Property("views", th.IntegerType),
    ).to_dict()



