"""Preview deterministic ordering of voice-catalog entries."""

from fastapi import APIRouter

from schemas.voice_catalog_ordering import (
    VoiceCatalogOrderOptions,
    VoiceCatalogOrderRequest,
    VoiceCatalogOrderResponse,
)
from services.voice_catalog_ordering import order_voice_catalog


router = APIRouter(prefix="/voices/catalog", tags=["voices"])


@router.post("/order-preview", response_model=VoiceCatalogOrderResponse)
def preview_voice_catalog_order(
    request: VoiceCatalogOrderRequest,
) -> VoiceCatalogOrderResponse:
    options = request.options
    if request.sort_by_name and options is None:
        # Compatibility with clients that predate field precedence options.
        options = VoiceCatalogOrderOptions(fields=["name"])

    return VoiceCatalogOrderResponse(
        voices=order_voice_catalog(request.voices, options)
    )
