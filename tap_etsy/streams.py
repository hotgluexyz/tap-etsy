"""Stream type classes for tap-etsy."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from singer_sdk import typing as th  # JSON Schema typing helpers
import requests

from tap_etsy.client import etsyStream

class ShopTransactionStream(etsyStream):
    name = "shop_transactions"
    path = "/shop_id/transactions"
    paginated_stream = True
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
        th.Property("buyer_coupon", th.NumberType),
        th.Property("shop_coupon", th.NumberType)
    ).to_dict()
class ShopListingStream(etsyStream):
    name = "shop_listings"
    path = "/shop_id/listings"
    paginated_stream = True
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
class ShopReceiptStream(etsyStream):
    name = "shop_receipts"
    path = "/shop_id/receipts"
    primary_keys = ["receipt_id"]
    replication_key = "updated_timestamp"
    schema = th.PropertiesList(
        th.Property("transaction_id", th.IntegerType),
        th.Property("receipt_id", th.IntegerType),
        th.Property("receipt_type", th.IntegerType),
        th.Property("seller_user_id", th.IntegerType),
        th.Property("seller_email", th.StringType),
        th.Property("buyer_user_id", th.IntegerType),
        th.Property("buyer_email", th.StringType),
        th.Property("name", th.StringType),
        th.Property("first_line", th.StringType),
        th.Property("second_line", th.StringType),
        th.Property("city", th.StringType),
        th.Property("state", th.StringType),
        th.Property("zip", th.StringType),
        th.Property("status", th.StringType),
        th.Property("formatted_address", th.StringType),
        th.Property("country_iso", th.StringType),
        th.Property("payment_method", th.StringType),
        th.Property("payment_email", th.StringType),
        th.Property("message_from_seller", th.StringType),
        th.Property("message_from_buyer", th.StringType),
        th.Property("message_from_payment", th.StringType),
        th.Property("is_paid", th.BooleanType),
        th.Property("is_shipped", th.BooleanType),
        th.Property("create_timestamp", th.IntegerType),
        th.Property("created_timestamp", th.IntegerType),
        th.Property("update_timestamp", th.IntegerType),
        th.Property("updated_timestamp", th.DateTimeType),
        th.Property("is_gift", th.BooleanType),
        th.Property("gift_message", th.StringType),
        th.Property("grandtotal", th.CustomType({"type": ["object", "string"]})),
        th.Property("subtotal", th.CustomType({"type": ["object", "string"]})),
        th.Property("total_price", th.CustomType({"type": ["object", "string"]})),
        th.Property("total_vat_cost", th.CustomType({"type": ["object", "string"]})),
        th.Property("total_tax_cost", th.CustomType({"type": ["object", "string"]})),
        th.Property("total_shipping_cost", th.CustomType({"type": ["object", "string"]})),
        th.Property("discount_amt", th.CustomType({"type": ["object", "string"]})),
        th.Property("gift_wrap_price", th.CustomType({"type": ["object", "string"]})),
        th.Property("shipments", th.CustomType({"type": ["array", "string"]})),
        th.Property("transactions", th.CustomType({"type": ["array", "string"]})),
        th.Property("refunds", th.CustomType({"type": ["array", "string"]})),
    ).to_dict()



class ShippingProfileStream(etsyStream):
    name = "shipping_profiles"
    path = "/shop_id/shipping-profiles"
    primary_keys = ["shipping_profile_id"]
    paginated_stream = False
    schema = th.PropertiesList(
        th.Property("shipping_profile_id", th.IntegerType),
        th.Property("title", th.StringType),
        th.Property("user_id", th.IntegerType),
        th.Property("min_processing_days", th.IntegerType),
        th.Property("max_processing_days", th.IntegerType),
        th.Property("processing_days_display_label", th.StringType),
        th.Property("origin_country_iso", th.StringType),
        th.Property("is_deleted", th.BooleanType),
        th.Property("shipping_profile_destinations", th.ArrayType(
            th.ObjectType(
                th.Property("shipping_profile_destination_id", th.IntegerType),
                th.Property("shipping_profile_id", th.IntegerType),
                th.Property("origin_country_iso", th.StringType),
                th.Property("destination_country_iso", th.StringType),
                th.Property("destination_region", th.StringType),
                th.Property("primary_cost", th.ObjectType(
                    th.Property("amount", th.IntegerType),
                    th.Property("divisor", th.IntegerType),
                    th.Property("currency_code", th.StringType),
                )),
                th.Property("secondary_cost", th.ObjectType(
                    th.Property("amount", th.IntegerType),
                    th.Property("divisor", th.IntegerType),
                    th.Property("currency_code", th.StringType),
                )),
                th.Property("shipping_carrier_id", th.IntegerType),
                th.Property("mail_class", th.StringType),
                th.Property("min_delivery_days", th.IntegerType),
                th.Property("max_delivery_days", th.IntegerType),
            )
        )),
        th.Property("shipping_profile_upgrades", th.ArrayType(
            th.ObjectType(
                th.Property("shipping_profile_id", th.IntegerType),
                th.Property("upgrade_id", th.IntegerType),
                th.Property("upgrade_name", th.StringType),
                th.Property("type", th.IntegerType),
                th.Property("rank", th.IntegerType),
                th.Property("language", th.StringType),
                th.Property("price", th.ObjectType(
                    th.Property("amount", th.IntegerType),
                    th.Property("divisor", th.IntegerType),
                    th.Property("currency_code", th.StringType),
                )),
                th.Property("secondary_price", th.ObjectType(
                    th.Property("amount", th.IntegerType),
                    th.Property("divisor", th.IntegerType),
                    th.Property("currency_code", th.StringType),
                )),
                th.Property("shipping_carrier_id", th.IntegerType),
                th.Property("mail_class", th.StringType),
                th.Property("min_delivery_days", th.IntegerType),
                th.Property("max_delivery_days", th.IntegerType),
            )
        )),
        th.Property("origin_postal_code", th.StringType),
        th.Property("profile_type", th.StringType),
        th.Property("domestic_handling_fee", th.NumberType),
        th.Property("international_handling_fee", th.NumberType),
    ).to_dict()

class ShopsStream(etsyStream):
    name = "shops"
    path = ""
    primary_keys = ["shop_id"]
    paginated_stream = True
    schema = th.PropertiesList(
        th.Property("shop_id", th.IntegerType),  # The unique positive non-zero numeric ID for an Etsy Shop.
        th.Property("user_id", th.IntegerType),  # The numeric user ID of the user who owns this shop.
        th.Property("shop_name", th.StringType),  # The shop's name string.
        th.Property("create_date", th.IntegerType),  # The date and time this shop was created, in epoch seconds.
        th.Property("created_timestamp", th.IntegerType),  # The date and time this shop was created, in epoch seconds.
        th.Property("title", th.StringType, required=False),  # Nullable: A brief heading string for the shop's main page.
        th.Property("announcement", th.StringType, required=False),  # Nullable: An announcement string for buyers.
        th.Property("currency_code", th.StringType),  # The ISO code for the shop's currency.
        th.Property("is_vacation", th.BooleanType),  # True if not accepting purchases.
        th.Property("vacation_message", th.StringType, required=False),  # Nullable: Displayed when on vacation.
        th.Property("sale_message", th.StringType, required=False),  # Nullable: Sent to buyers after purchase.
        th.Property("digital_sale_message", th.StringType, required=False),  # Nullable: Sent to digital item buyers.
        th.Property("update_date", th.IntegerType),  # Last update time, in epoch seconds.
        th.Property("updated_timestamp", th.IntegerType),  # Last update time, in epoch seconds.
        th.Property("listing_active_count", th.IntegerType),  # Number of active listings.
        th.Property("digital_listing_count", th.IntegerType),  # Number of digital listings.
        th.Property("login_name", th.StringType),  # Shop owner's login name.
        th.Property("accepts_custom_requests", th.BooleanType),  # True if accepts custom requests.
        th.Property("policy_welcome", th.StringType, required=False),  # Nullable: Policy welcome string.
        th.Property("policy_payment", th.StringType, required=False),  # Nullable: Payment policy string.
        th.Property("policy_shipping", th.StringType, required=False),  # Nullable: Shipping policy string.
        th.Property("policy_refunds", th.StringType, required=False),  # Nullable: Refund policy string.
        th.Property("policy_additional", th.StringType, required=False),  # Nullable: Additional policies string.
        th.Property("policy_seller_info", th.StringType, required=False),  # Nullable: Seller info string.
        th.Property("policy_update_date", th.IntegerType),  # Last shop policies update, in epoch seconds.
        th.Property("policy_has_private_receipt_info", th.BooleanType),  # True if EU receipts display private info.
        th.Property("has_unstructured_policies", th.BooleanType),  # True if displays unstructured policies.
        th.Property("policy_privacy", th.StringType, required=False),  # Nullable: Privacy policy string.
        th.Property("vacation_autoreply", th.StringType, required=False),  # Nullable: Vacation auto reply string.
        th.Property("url", th.StringType),  # URL for the shop.
        th.Property("image_url_760x100", th.StringType, required=False),  # Nullable: Banner image URL.
        th.Property("num_favorers", th.IntegerType),  # Number of users who favorited the shop.
        th.Property("languages", th.ArrayType(th.StringType)),  # List of shop language strings.
        th.Property("icon_url_fullxfull", th.StringType, required=False),  # Nullable: Shop icon URL.
        th.Property("is_using_structured_policies", th.BooleanType),  # True if using structured policies.
        th.Property("has_onboarded_structured_policies", th.BooleanType),  # True if viewed/accepted structured policies onboarding.
        th.Property("include_dispute_form_link", th.BooleanType),  # True if shop policies include EU dispute link.
        th.Property("is_direct_checkout_onboarded", th.BooleanType),  # True if onboarded Etsy direct checkout (deprecated).
        th.Property("is_etsy_payments_onboarded", th.BooleanType),  # True if onboarded Etsy Payments.
        th.Property("is_calculated_eligible", th.BooleanType),  # True if eligible for calculated shipping.
        th.Property("is_opted_in_to_buyer_promise", th.BooleanType),  # True if opted in to buyer promise.
        th.Property("is_shop_us_based", th.BooleanType),  # True if shop is US based.
        th.Property("transaction_sold_count", th.IntegerType),  # Total sales (transactions).
        th.Property("shipping_from_country_iso", th.StringType, required=False),  # Nullable: Shop shipping from country ISO.
        th.Property("shop_location_country_iso", th.StringType, required=False),  # Nullable: Shop country location ISO.
        th.Property("review_count", th.IntegerType, required=False),  # Nullable: Number of shop listing reviews in past year.
        th.Property("review_average", th.NumberType, required=False),  # Nullable: Avg. rating for reviews in past year.
    ).to_dict()

    # need this to set shop_name="". setting it in get_url_params was stripping it in the end from final prepared request because of empty string
    def prepare_request(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> requests.PreparedRequest:
        """Prepare a request object, ensuring shop_name parameter is always included."""
        prepared_request = super().prepare_request(context, next_page_token)
        
        # Ensure shop_name parameter is always included, even if empty
        parsed_url = urlparse(prepared_request.url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        
        # Always set shop_name to empty string (ensure it's included even if empty)
        query_params["shop_name"] = [""]
        
        # Rebuild the URL with the shop_name parameter
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        # Update the prepared request URL
        prepared_request.url = new_url
        
        return prepared_request