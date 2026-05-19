"""OJS v1.0 — Smart wearable domain (sub-vertical discriminator).

Activated when product_type == "smart_wearable". Covers smart rings
(Oura, Ultrahuman, RingConn), smart bracelets, and smart-watch features
that are NOT covered by traditional WatchModule.

Note: Apple Watch / Samsung Galaxy Watch use both WatchModule AND SmartModule.
Per Google Product Taxonomy, smart watches sit under Jewelry > Watches (201).
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import Field

from ._common import OJSBaseModel


class SmartFeature(str, Enum):
    """Smart features (multi-valued)."""

    HEART_RATE = "heart_rate"
    HRV = "hrv"  # heart rate variability
    SPO2 = "spo2"  # blood oxygen
    ECG = "ecg"  # electrocardiogram
    SLEEP_TRACKING = "sleep_tracking"
    ACTIVITY_TRACKING = "activity_tracking"
    GPS = "gps"
    NFC_PAYMENT = "nfc_payment"
    CELLULAR_LTE = "cellular_lte"
    BLOOD_PRESSURE = "blood_pressure"
    SKIN_TEMPERATURE = "skin_temperature"
    BODY_BATTERY = "body_battery"  # Garmin term
    STRESS_TRACKING = "stress_tracking"
    MENSTRUAL_CYCLE = "menstrual_cycle"
    FALL_DETECTION = "fall_detection"
    CRASH_DETECTION = "crash_detection"
    EMERGENCY_SOS = "emergency_sos"
    SMART_NOTIFICATIONS = "smart_notifications"
    VOICE_ASSISTANT = "voice_assistant"
    CAMERA = "camera"
    SPEAKER = "speaker"
    MICROPHONE = "microphone"
    OTHER = "other"


class Connectivity(str, Enum):
    """Wireless connectivity standards."""

    BLUETOOTH_LE = "bluetooth_le"
    BLUETOOTH_CLASSIC = "bluetooth_classic"
    WIFI = "wifi"
    NFC = "nfc"
    UWB = "uwb"  # ultra-wideband (Apple U1/U2)
    LTE_CAT_M1 = "lte_cat_m1"
    LTE_CAT_NB1 = "lte_cat_nb1"
    GPS = "gps"
    GLONASS = "glonass"
    GALILEO = "galileo"


class WaterProofRating(str, Enum):
    """IP / ATM ingress protection ratings for electronics."""

    IPX4 = "ipx4"  # splash
    IPX5 = "ipx5"
    IPX6 = "ipx6"
    IPX7 = "ipx7"  # 1m for 30 min
    IPX8 = "ipx8"  # >1m, mfr-specified
    IP67 = "ip67"
    IP68 = "ip68"
    ATM_3 = "3atm"  # 30m static (splash only)
    ATM_5 = "5atm"  # 50m static (swim)
    ATM_10 = "10atm"  # 100m
    ATM_20 = "20atm"
    NOT_WATERPROOF = "not_waterproof"


class SmartModule(OJSBaseModel):
    """Smart device specifications.

    Required when product_type='smart_wearable'. For Apple Watch /
    Galaxy Watch, also populate WatchModule.
    """

    features: list[SmartFeature] = Field(
        min_length=1, description="Smart features available"
    )
    operating_system: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None, description="OS (e.g. 'watchOS 11', 'Wear OS 4', 'Oura OS')"
    )
    app_required: Optional[bool] = Field(
        default=None, description="Companion smartphone app required"
    )
    app_ios_compatible: Optional[bool] = None
    app_android_compatible: Optional[bool] = None
    minimum_ios_version: Optional[Annotated[str, Field(max_length=20)]] = None
    minimum_android_version: Optional[Annotated[str, Field(max_length=20)]] = None

    battery_life_hours: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Battery life under typical use (hours)"
    )
    battery_life_days: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Battery life in days (preferred for smart rings)"
    )
    charging_method: Optional[Annotated[str, Field(max_length=50)]] = Field(
        default=None,
        description="Charging method (e.g. 'magnetic_puck', 'usb_c', 'wireless_qi')",
    )
    charge_time_minutes: Optional[Annotated[int, Field(gt=0)]] = None

    connectivity: list[Connectivity] = Field(
        default_factory=list, description="Wireless standards supported"
    )
    sensor_count: Optional[Annotated[int, Field(ge=0)]] = None
    sensors: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list,
        description="Sensor names (e.g. 'PPG', 'gyroscope', 'accelerometer', 'thermometer')",
    )

    waterproof_rating: Optional[WaterProofRating] = None
    fda_cleared: Optional[bool] = Field(
        default=None, description="Has FDA clearance for medical claims"
    )
    fda_clearance_numbers: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list, description="FDA 510(k) clearance numbers if any"
    )
    ce_certified: Optional[bool] = None

    subscription_required: Optional[bool] = Field(
        default=None,
        description="Premium subscription required for full features (e.g. Oura ring)",
    )
    subscription_monthly_usd: Optional[Annotated[float, Field(ge=0)]] = None

    data_export_supported: Optional[bool] = None
    data_export_formats: list[Annotated[str, Field(max_length=20)]] = Field(
        default_factory=list, description="Export formats (csv, json, hl7-fhir, etc.)"
    )

    weight_grams: Optional[Annotated[float, Field(gt=0)]] = Field(
        default=None, description="Device weight in grams (important for smart rings)"
    )
