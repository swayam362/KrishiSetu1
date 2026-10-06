"""
KrushiSetu Modular Transportation & Logistics Estimation Engine
Computes reliable transit distance, vehicle suitability, multi-trip requirements,
and accurate transport costs while strictly validating inputs and preserving location privacy.
"""

import os
import math
import logging
from typing import Dict, Any, List, Optional
from backend.utils.location_privacy import mask_location_for_public

logger = logging.getLogger("krushisetu.transportation")

# Calibrated Vehicle Types for Agricultural Freight in India
SUPPORTED_VEHICLES = {
    "mini_truck": {
        "id": "mini_truck",
        "name": "Mini Truck / 3-Wheeler (e.g. Tata Ace)",
        "capacity_kg": 1000.0,
        "base_rate_per_km": 22.0,
        "min_charge": 500.0,
        "handling_charge_per_trip": 200.0,
        "avg_speed_kmh": 35.0,
        "suitable_crops": ["Vegetables", "Fruits", "Spices", "Flowers", "Tomato", "Onion"]
    },
    "pickup": {
        "id": "pickup",
        "name": "Pickup Truck (e.g. Bolero Maxi Truck)",
        "capacity_kg": 2500.0,
        "base_rate_per_km": 32.0,
        "min_charge": 900.0,
        "handling_charge_per_trip": 350.0,
        "avg_speed_kmh": 40.0,
        "suitable_crops": ["All Commodities", "Vegetables", "Grains", "Tomato", "Potato", "Onion"]
    },
    "medium_truck": {
        "id": "medium_truck",
        "name": "Medium Truck 14ft–19ft (e.g. Eicher / 6-Tonne)",
        "capacity_kg": 6000.0,
        "base_rate_per_km": 48.0,
        "min_charge": 1800.0,
        "handling_charge_per_trip": 600.0,
        "avg_speed_kmh": 45.0,
        "suitable_crops": ["Grains", "Oilseeds", "Cotton", "Pulses", "Bulk Produce", "Wheat", "Rice", "Soybean"]
    },
    "heavy_truck": {
        "id": "heavy_truck",
        "name": "Heavy Multi-Axle Truck (e.g. 10-Wheeler / 16-Tonne)",
        "capacity_kg": 16000.0,
        "base_rate_per_km": 72.0,
        "min_charge": 3500.0,
        "handling_charge_per_trip": 1000.0,
        "avg_speed_kmh": 48.0,
        "suitable_crops": ["Bulk Grains", "Cotton Bales", "Interstate Mandi Hauls", "Wheat", "Soybean", "Rice"]
    },
    "reefer": {
        "id": "reefer",
        "name": "Cold-Chain Reefer Truck (Temperature Controlled)",
        "capacity_kg": 5000.0,
        "base_rate_per_km": 60.0,
        "min_charge": 2500.0,
        "handling_charge_per_trip": 500.0,
        "avg_speed_kmh": 45.0,
        "suitable_crops": ["Perishables", "Tomato", "Dairy", "Grapes", "Strawberries", "Exotic Greens"],
        "cooling_surcharge_percent": 15.0
    }
}

# Major Agricultural Mandi Hub Coordinates (Lat, Lon)
KNOWN_MANDI_COORDINATES = {
    "pune": (18.5204, 73.8567),
    "mumbai": (19.0760, 72.8777),
    "nashik": (19.9975, 73.7898),
    "lasalgaon": (20.1458, 74.2289),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "guntur": (16.3067, 80.4365),
    "surat": (21.1702, 72.8311),
    "ahmedabad": (23.0225, 72.5714),
    "karnal": (29.6857, 76.9905),
    "ludhiana": (30.9010, 75.8573),
    "lucknow": (26.8467, 80.9462),
    "bangalore": (12.9716, 77.5946),
    "jaipur": (26.9124, 75.7873),
    "hyderabad": (17.3850, 78.4867),
    "kolhapur": (16.7050, 74.2433),
    "solapur": (17.6599, 75.9064),
    "aurangabad": (19.8762, 75.3433),
    "delhi": (28.7041, 77.1025)
}


class TransportationEngine:
    """
    Core Transportation and Logistics Service.
    Integrates distance matrix calculation, vehicle capacity auto-sizing,
    and server-side cost calibration.
    """

    def __init__(self):
        # Backend-only Maps / Routing API Key
        self.maps_api_key = os.getenv("MAPS_API_KEY", "")

    def get_supported_vehicles(self) -> List[Dict[str, Any]]:
        """Return list of supported vehicle types and calibrated baseline rates."""
        return list(SUPPORTED_VEHICLES.values())

    def calculate_distance(self, origin: str, destination: str) -> Dict[str, Any]:
        """
        Calculate road transit distance and estimated driving duration.
        Modular: Uses external routing API if configured; otherwise computes calibrated
        haversine road distance across Indian agricultural trade corridors.
        """
        org_clean = (origin or "Pune").strip().lower()
        dst_clean = (destination or "Mumbai").strip().lower()

        # Check for same-city / local transit
        if org_clean == dst_clean:
            return {
                "distance_km": 15.0,
                "transit_hours": 0.8,
                "calculation_method": "intra_district_default"
            }

        # Match known mandi coordinates or find substring match
        coord_org = self._lookup_coords(org_clean, default=(18.5204, 73.8567))
        coord_dst = self._lookup_coords(dst_clean, default=(19.0760, 72.8777))

        # External Map API Integration (Backend Only)
        if self.maps_api_key:
            try:
                import requests
                # Example Google Distance Matrix / OSRM endpoint with backend key
                url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={coord_org[0]},{coord_org[1]}&destinations={coord_dst[0]},{coord_dst[1]}&key={self.maps_api_key}"
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    rows = data.get("rows", [{}])
                    elements = rows[0].get("elements", [{}]) if rows else [{}]
                    if elements and elements[0].get("status") == "OK":
                        dist_m = elements[0]["distance"]["value"]
                        dur_s = elements[0]["duration"]["value"]
                        return {
                            "distance_km": round(dist_m / 1000.0, 1),
                            "transit_hours": round(dur_s / 3600.0, 1),
                            "calculation_method": "live_maps_api"
                        }
            except Exception as e:
                logger.warning(f"External Maps API call failed: {e}. Falling back to internal distance model.")

        # Resilient Geodesic Road Calculation (Haversine + Indian highway road factor 1.28)
        lat1, lon1 = math.radians(coord_org[0]), math.radians(coord_org[1])
        lat2, lon2 = math.radians(coord_dst[0]), math.radians(coord_dst[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        straight_dist_km = 6371.0 * c

        # 1.28 Road winding & ghat terrain multiplier for Indian rural freight
        road_km = max(10.0, round(straight_dist_km * 1.28, 1))
        transit_hrs = round(road_km / 42.0, 1)

        return {
            "distance_km": road_km,
            "transit_hours": max(0.5, transit_hrs),
            "calculation_method": "agro_corridor_matrix"
        }

    def _lookup_coords(self, place_str: str, default: tuple) -> tuple:
        """Lookup coordinates by full name or substring."""
        for name, coords in KNOWN_MANDI_COORDINATES.items():
            if name in place_str or place_str in name:
                return coords
        return default

    def recommend_vehicle(self, quantity_kg: float, requires_cold_storage: bool = False) -> str:
        """Auto-recommend the most cost-effective vehicle based on cargo payload."""
        if requires_cold_storage:
            return "reefer"
        if quantity_kg <= 1000.0:
            return "mini_truck"
        elif quantity_kg <= 2500.0:
            return "pickup"
        elif quantity_kg <= 6000.0:
            return "medium_truck"
        else:
            return "heavy_truck"

    def estimate_transportation_cost(
        self,
        farmer_location: Any,
        buyer_location: Any,
        quantity_kg: float,
        vehicle_type: Optional[str] = None,
        custom_rate_per_km: Optional[float] = None,
        requires_cold_storage: bool = False
    ) -> Dict[str, Any]:
        """
        End-to-end Transportation Estimation with server-side validation and calibration.
        Never blindly trusts frontend distance or pricing.
        """
        # 1. Validate & Sanitize Quantity
        try:
            qty = float(quantity_kg)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a valid positive number.")

        if qty <= 0:
            raise ValueError("Quantity must be greater than 0 kg.")
        if qty > 100000.0:
            raise ValueError("Quantity exceeds maximum single-order capacity (100,000 kg).")

        # 2. Location Privacy Sanitization
        farmer_masked = mask_location_for_public(farmer_location)
        buyer_masked = mask_location_for_public(buyer_location)

        origin_str = str(farmer_location.get("district") if isinstance(farmer_location, dict) else farmer_location)
        dest_str = str(buyer_location.get("district") if isinstance(buyer_location, dict) else buyer_location)

        # 3. Compute Server-Verified Distance
        dist_info = self.calculate_distance(origin_str, dest_str)
        distance_km = dist_info["distance_km"]

        # 4. Determine Suitable Vehicle & Validate Capacity
        veh_key = (vehicle_type or "").strip().lower()
        if veh_key not in SUPPORTED_VEHICLES:
            veh_key = self.recommend_vehicle(qty, requires_cold_storage=requires_cold_storage)

        veh_config = SUPPORTED_VEHICLES[veh_key]
        capacity = veh_config["capacity_kg"]

        # Calculate number of trips needed
        trips = max(1, math.ceil(qty / capacity))
        is_multi_trip = trips > 1

        # 5. Rate Calibration & Bounds Enforcement (Backend Security)
        calibrated_rate = veh_config["base_rate_per_km"]
        if custom_rate_per_km is not None:
            try:
                c_rate = float(custom_rate_per_km)
                # Calibrate within safe boundaries (cannot be negative or ridiculously off-market)
                min_rate = calibrated_rate * 0.70
                max_rate = calibrated_rate * 2.50
                if min_rate <= c_rate <= max_rate:
                    calibrated_rate = c_rate
            except (ValueError, TypeError):
                pass  # Use calibrated_rate

        # 6. Cost Breakdown Computation
        base_freight = distance_km * calibrated_rate * trips
        base_freight = max(veh_config["min_charge"] * trips, base_freight)

        handling_cost = veh_config["handling_charge_per_trip"] * trips
        
        # Toll & Highway fees (estimated ~ ₹1.2 per km for trips > 40km)
        toll_allowance = round(max(0.0, (distance_km - 40.0) * 1.20 * trips), 2)

        # Cold chain cooling surcharge
        cooling_surcharge = 0.0
        if veh_key == "reefer" or requires_cold_storage:
            cooling_pct = veh_config.get("cooling_surcharge_percent", 15.0)
            cooling_surcharge = round(base_freight * (cooling_pct / 100.0), 2)

        total_cost = round(base_freight + handling_cost + toll_allowance + cooling_surcharge, 2)
        cost_per_kg = round(total_cost / qty, 2)
        cost_per_quintal = round(cost_per_kg * 100.0, 2)

        # Transit time
        transit_hours = round(dist_info["transit_hours"] * (1.1 if is_multi_trip else 1.0), 1)

        return {
            "success": True,
            "origin": farmer_masked["display_location"],
            "destination": buyer_masked["display_location"],
            "distance_km": distance_km,
            "transit_hours": transit_hours,
            "quantity_kg": qty,
            "vehicle_type": {
                "id": veh_config["id"],
                "name": veh_config["name"],
                "capacity_kg": capacity,
                "rate_per_km": round(calibrated_rate, 2),
                "is_recommended": (veh_key == self.recommend_vehicle(qty, requires_cold_storage))
            },
            "trips_required": trips,
            "cost_breakdown": {
                "base_freight": round(base_freight, 2),
                "handling_and_loading": round(handling_cost, 2),
                "toll_and_permits": toll_allowance,
                "cold_storage_surcharge": cooling_surcharge,
                "total_estimated_transport_cost": total_cost,
                "effective_cost_per_kg": cost_per_kg,
                "effective_cost_per_quintal": cost_per_quintal
            },
            "location_privacy": {
                "origin_anonymized": farmer_masked["display_location"],
                "destination_anonymized": buyer_masked["display_location"],
                "notice": "Exact farm gate coordinates are withheld for privacy and only shared upon confirmed dispatch."
            },
            "formula": "Total Transport Cost = (Distance × Rate × Trips) + Handling + Toll + Cold Storage Surcharge"
        }


# Global instance
_transportation_engine = None

def get_transportation_engine() -> TransportationEngine:
    global _transportation_engine
    if _transportation_engine is None:
        _transportation_engine = TransportationEngine()
    return _transportation_engine
