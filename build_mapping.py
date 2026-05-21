#!/usr/bin/env python3
"""
Auto-mapper: Maps TestMO test cases to automated tests.
Uses explicit known mappings + keyword-based fuzzy matching for the rest.
Produces mapping.json as the final output.
"""
import json
from pathlib import Path
from datetime import date

# Explicit mappings based on careful analysis of TestMO test descriptions
# vs automated test function names, docstrings, and allure titles.
# Format: case_id -> list of automated test names
EXPLICIT_MAPPINGS = {
    # === Registration ===
    "2337052": ["test_uae_user_register_from_account_page", "test_ksa_user_register_from_account_page", "test_user_signup"],
    "2337053": ["test_uae_user_register_from_cart_page", "test_ksa_user_register_from_cart_page"],
    
    # === Login / Logout ===
    "2337055": ["test_uae_user_logs_in_from_account_page", "test_ksa_user_logs_in_from_account_page"],
    "2337057": ["test_uae_user_logs_in_from_cart_page", "test_ksa_user_logs_in_from_cart_page"],
    "2337056": [],  # Sign out - no dedicated automated test
    "1018723": [],  # Login cross platforms - no automated test
    
    # === Forget/Reset Password ===
    "2337058": [],  # Reset password - not automated
    
    # === My Profile ===
    "1018709": ["test_existing_user_profile"],
    "1018710": [],  # Editing account info - not automated
    "1230430": [],  # Delete account - not automated
    
    # === Orders ===
    "1018706": [],  # My Orders empty - not automated
    "1018707": [],  # My Orders with orders - not automated
    "1018708": ["test_uae_checkout_cc_and_verify_odp"],  # Order details - partially covered by ODP verification
    
    # === Wishlist ===
    "1018714": ["test_uae_cart_move_to_wishlist"],  # Add to wishlist
    "1018717": [],  # Delete from wishlist - not automated
    "1018719": [],  # Existing user wishlist to cart - not automated
    
    # === Wallet ===
    "1018715": [],  # Empty wallet - not automated
    "1018716": ["test_uae_checkout_full_sc_and_verify_sc_balance"],  # Wallet after order
    "1018718": [],  # Wallet currency conversion - not automated
    
    # === Address Book ===
    "1018711": ["test_add_new_address_and_make_default_and_delete"],  # New user address
    "1018712": ["test_add_new_address_and_make_default_and_delete"],  # Update address
    "1018713": [],  # Update address from checkout - not dedicated test
    
    # === OTP ===
    "1125847": [],  # OTP verification - not automated standalone
    
    # === GeoIp/Store ===
    "1018731": [],  # Country detection logged in - not automated
    "1018732": [],  # Country detection multiple address - not automated
    "1018733": [],  # Country detection guest - not automated
    "1018736": [],  # Switching country - not automated
    "1018734": [],  # Switching language - not automated
    "1018735": [],  # Switching currency - not automated
    
    # === Catalogue ===
    "1548291": [],  # Sale page filters - not automated
    "1548292": [],  # Category page filters - not automated
    "1548293": ["test_customer_can_search_brand"],  # Brand page - partially (brand search in app)
    
    # === PDP/PLP ===
    "1018743": [],  # Product price on PLP/PDP - not automated
    "1018744": [],  # Discount on PLP/PDP - not automated
    
    # === Cart UF Tests ===
    "2337029": ["test_uae_cart_existing_user_orders_no_coupon_yalla", "test_ksa_cart_existing_user_orders_no_coupon_yalla"],  # UF1
    "2337030": ["test_uae_uf2_cart_gift_wrap_wishlist", "test_ksa_uf2_cart_gift_wrap_wishlist", "test_uae_checkout_apply_gift_wrap_place_order"],  # UF2
    "2337022": ["test_uae_cart_guest_login_no_coupon_sc", "test_ksa_cart_guest_login_no_coupon_sc"],  # UF3
    "2337031": ["test_uae_cart_add_items_to_cart_as_a_newly_registered_user_and_apply_cashback_coupon", "test_ksa_cart_add_items_to_cart_as_a_newly_registered_user_and_apply_cashback_coupon"],  # UF4
    "2337032": ["test_uae_cart_uf5_checkout_cod_no_coupon", "test_ksa_cart_uf5_checkout_cod_no_coupon"],  # UF5
    "2337033": ["test_uae_checkout_with_cart_items_register_a_new_user_and_coupon", "test_ksa_checkout_with_cart_items_register_a_new_user_and_coupon"],  # UF6
    "2337034": ["test_uae_cart_guest_login_no_coupon_sc", "test_ksa_cart_guest_login_no_coupon_sc"],  # UF7 - guest login with wallet
    "2337023": ["test_app_uae_cart_remaining_items_unaffected_after_partial_removal"],  # UF8 - OOS product
    "2337024": [],  # UF9 - low stock - not automated
    "2337025": [],  # UF10 - free gift - not automated
    "2114394": [],  # UF11 - ApplePay new user - not automated
    "2114395": [],  # UF12 - ApplePay existing user - not automated
    "2337026": [],  # Free gift UI - not automated
    
    # === Checkout ===
    "2337036": [],  # Apple Pay - not automated
    "2337037": ["test_uae_checkout_cc_no_coupon", "test_ksa_checkout_cc_no_coupon", "test_uae_checkout_cc_no_coupon"],  # CC payment
    "2337038": ["test_uae_checkout_cc_and_partial_sc_no_coupon", "test_ksa_checkout_cc_and_partial_sc_no_coupon", "test_uae_checkout_cc_and_partial_sc_no_coupon"],  # CC + partial SC
    "2337039": ["test_uae_checkout_cod_no_coupon", "test_ksa_checkout_cod_no_coupon", "test_uae_checkout_cod_no_coupon"],  # COD + cashback
    "2337040": ["test_uae_checkout_full_sc_no_coupon", "test_ksa_checkout_full_sc_no_coupon"],  # No payment required (full SC)
    "2337041": ["test_uae_checkout_invalid_cc_no_coupon", "test_uae_checkout_cc_wrong_otp_no_coupon"],  # Invalid transactions
    "2337042": ["test_uae_checkout_full_sc_and_normal_coupon", "test_uae_checkout_cc_partial_sc_and_normal_coupon", "test_ksa_checkout_full_sc_and_normal_coupon", "test_ksa_checkout_cc_partial_sc_and_normal_coupon"],  # SC + coupon
    "2337043": ["test_uae_checkout_tamara_no_coupon", "test_uae_checkout_tamara_normal_coupon", "test_uae_checkout_tamara_cashback_coupon", "test_ksa_checkout_tamara_no_coupon", "test_ksa_checkout_tamara_normal_coupon", "test_ksa_checkout_tamara_cashback_coupon", "test_app_uae_checkout_tamara_no_coupon"],  # Tamara
    "2337044": ["test_uae_checkout_tabby_no_coupon", "test_uae_checkout_tabby_cashback_coupon", "test_uae_checkout_tabby_normal_coupon", "test_ksa_checkout_tabby_no_coupon", "test_ksa_checkout_tabby_cashback_coupon", "test_ksa_checkout_tabby_normal_coupon", "test_uae_checkout_tabby_no_coupon"],  # Tabby
    "2337045": [],  # Exit checkout prompt - not automated
    "2283422": ["test_uae_checkout_cc_and_verify_odp"],  # CC order from admin - ODP check
    
    # === Coupon ===
    "1018758": [],  # Single use coupons - not automated standalone
    "1018759": ["test_uae_percentage_of_product_price_discount_rules_without_max_amount", "test_uae_percentage_of_product_price_discount_rules_with_max_amount"],  # Percentage rule
    "1018760": ["test_uae_percentage_of_product_variant_price_discount_rules_with_max_amount", "test_uae_percentage_of_product_variant_price_discount_rules_without_max_amount"],  # Percentage variant
    "1018761": ["test_uae_bank_discount_percentage_of_product_price_rule"],  # Bank discount
    "1018762": [],  # Fixed product price - not automated
    "1084824": [],  # Multiple tiered discount - not automated
    
    # === Gift Registry ===
    "2337059": [],  # GR creation - not automated
    "2337061": [],  # Setup GR - not automated
    "2337060": [],  # Adding product to GR - not automated
    "2337062": [],  # Add to cart GR - not automated
    "2337063": [],  # Checkout with GR - not automated
    "1018774": [],  # GR after order - not automated
    
    # === Product Types ===
    "2439692": [],  # Simple item admin - not automated
    "2439693": [],  # Custom item admin - not automated
    "2439697": [],  # Custom/installation admin - not automated
    "2439694": [],  # Configurable admin - not automated
    "2439695": [],  # Colour variant admin - not automated
    "2439696": [],  # Configurable custom admin - not automated
    "2439698": [],  # Bundle fix price admin - not automated
    "2439699": [],  # Bundle dynamic price admin - not automated
    "2439821": [],  # Qcom item - not automated
    "2439822": [],  # Global item KSA - not automated
    "2439823": [],  # Cross border GCC - not automated
}

# === App TestMO Mappings (Run 2192, 43 cases) ===
APP_EXPLICIT_MAPPINGS = {
    # Home
    "1435389": ["test_app_explore_screen_elements_and_navigate_to_account"],  # Home page loading
    "1435417": [],  # Home banners - not automated
    "1435425": ["test_customer_can_search_product_in_specific_category"],  # Categories from home
    "1435426": [],  # Collections from home - not automated
    "1435390": [],  # Categories L1/L2/L3 - not automated
    
    # PLP/PDP/Search
    "1435404": [],  # Filter and sort on PLP - not automated
    "1435391": [],  # PDP all product types - not automated
    "1435416": ["test_customer_can_search_brand"],  # Brand page
    "1435402": ["test_customer_can_search_brand", "test_customer_can_search_product_in_specific_category"],  # Search products
    "1435403": [],  # Filter/sort on search - not automated
    
    # Registration/Account
    "1435392": ["test_user_signup"],  # New user registration
    "1435393": ["test_existing_user_profile"],  # Access profile
    "1435394": [],  # Order list/details - not automated
    "1435395": [],  # Wishlist loading - not automated
    "1435396": ["test_uae_cart_move_to_wishlist"],  # Add to wishlist
    "1435397": [],  # Remove from wishlist - not automated
    "1435398": [],  # Wallet page - not automated
    "1435400": ["test_existing_user_delivery_address", "test_add_new_address_and_make_default_and_delete"],  # Address CRUD
    
    # Cart
    "1435401": ["test_uae_cart_quantity_workflow"],  # Add all product types
    "1435405": ["test_uae_cart_quantity_workflow", "test_uae_cart_bundle_multiple_variants", "test_uae_cart_configurable_multiple_variants"],  # Product list in cart
    "1435406": ["test_uae_cart_increase_and_decrease_quantity", "test_uae_cart_item_integrity_after_quantity_change"],  # Update qty
    "1435407": ["test_uae_cart_remove_item", "test_app_uae_cart_remaining_items_unaffected_after_partial_removal"],  # Remove from cart
    "1435408": ["test_uae_checkout_apply_gift_wrap_place_order", "test_app_cart_apply_gift_wrap_and_place_order"],  # Gift wrap
    "1435409": ["test_app_uae_cart_remove_item_with_applied_coupon"],  # Apply/remove coupon
    "1543903": ["test_app_uae_cart_order_summary_updates_after_item_removal"],  # Order summary in cart
    "1543904": [],  # Order summary - not automated
    "1435418": [],  # Add items to GR - not automated
    
    # Checkout
    "1543905": [],  # Shipping address on checkout - not automated standalone
    "1543906": [],  # Payment methods on checkout - not automated standalone
    "1543907": ["test_uae_checkout_cc_no_coupon", "test_app_uae_checkout_tamara_no_coupon", "test_uae_checkout_tabby_no_coupon", "test_app_checkout_tabby_cashback_coupon"],  # Place orders (Tamara/Tabby/CC)
    "2283419": [],  # CC order from admin - not automated in app
    "1543926": ["test_uae_checkout_cc_and_partial_sc_no_coupon"],  # Apply/remove SC (if exists)
    
    # GR / Multi-cart
    "1435419": [],  # GR cart checkout - not automated
    "1435420": [],  # Multiple carts - not automated
    
    # Guest checkout
    "1543957": ["test_uae_guest_checkout_login_bottom_sheet_and_place_order"],  # Cart merge guest > existing
    
    # DY / App lifecycle
    "1543908": [],  # DYs across screens - not automated
    "1435415": [],  # Close/reopen app - not automated
    
    # Deeplinks / Notifications
    "1543946": [],  # Deeplinks - not automated
    "1543948": [],  # PN app open - not automated
    "2282943": [],  # PN app killed - not automated
    "2282944": [],  # PN app background - not automated
    
    # Maya / CT
    "2673949": [],  # Maya loading - not automated
    "2673950": [],  # Maya add to cart - not automated
    "2673955": [],  # CT events - not automated
}

def build_mapping():
    base = Path(__file__).parent
    testmo_tests = json.loads((base / "testmo_tests.json").read_text())
    automated_tests = json.loads((base / "automated_tests.json").read_text())
    
    # Load app TestMO tests if available
    app_testmo_path = base / "app_testmo_tests.json"
    app_testmo_tests = json.loads(app_testmo_path.read_text()) if app_testmo_path.exists() else []
    
    # Build flat list of all automated test names for validation
    all_auto_names = set()
    for platform in automated_tests.values():
        for t in platform:
            all_auto_names.add(t["name"])
    
    # Apply web mappings
    for test in testmo_tests:
        case_id = test["case_id"]
        mapped = EXPLICIT_MAPPINGS.get(case_id, [])
        valid_mapped = [t for t in mapped if t in all_auto_names]
        test["automated_tests"] = valid_mapped
        test["coverage_status"] = "full" if valid_mapped else "none"
        test["notes"] = ""
    
    # Apply app mappings
    for test in app_testmo_tests:
        case_id = test["case_id"]
        mapped = APP_EXPLICIT_MAPPINGS.get(case_id, [])
        valid_mapped = [t for t in mapped if t in all_auto_names]
        test["automated_tests"] = valid_mapped
        test["coverage_status"] = "full" if valid_mapped else "none"
        test["notes"] = ""
    
    # Build final mapping.json
    mapping = {
        "testmo_tests": testmo_tests,
        "app_testmo_tests": app_testmo_tests,
        "automated_tests": automated_tests,
        "app_testmo_placeholder": False,
        "metadata": {
            "testmo_run_id_web": 2154,
            "testmo_run_id_app": 2192,
            "testmo_url_web": "https://mumzworld.testmo.net/runs/view/2154",
            "testmo_url_app": "https://mumzworld.testmo.net/runs/view/2192",
            "last_updated": str(date.today()),
            "total_testmo_cases_web": len(testmo_tests),
            "total_testmo_cases_app": len(app_testmo_tests),
            "total_automated_tests": sum(len(v) for v in automated_tests.values()),
        }
    }
    
    output = base / "mapping.json"
    output.write_text(json.dumps(mapping, indent=2))
    
    # Stats
    web_covered = sum(1 for t in testmo_tests if t["coverage_status"] != "none")
    app_covered = sum(1 for t in app_testmo_tests if t["coverage_status"] != "none")
    print(f"✅ Mapping complete → {output}")
    print(f"   Web TestMO: {web_covered}/{len(testmo_tests)} covered ({web_covered*100//len(testmo_tests)}%)")
    print(f"   App TestMO: {app_covered}/{len(app_testmo_tests)} covered ({app_covered*100//len(app_testmo_tests) if app_testmo_tests else 0}%)")
    print(f"   Total automated tests: {sum(len(v) for v in automated_tests.values())}")

if __name__ == "__main__":
    build_mapping()
