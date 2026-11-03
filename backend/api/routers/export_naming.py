"""Preview deterministic filenames before a batch export is written."""

from fastapi import APIRouter

from schemas.export_naming import (
    DEFAULT_EXPORT_NAME_FIELDS,
    ExportNamingOptions,
    ExportNamingPreviewRequest,
    ExportNamingPreviewResponse,
)
from services.export_naming import build_export_names


router = APIRouter(prefix="/export-naming", tags=["export-naming"])


@router.post("/preview", response_model=ExportNamingPreviewResponse)
def preview_export_names(
    request: ExportNamingPreviewRequest,
) -> ExportNamingPreviewResponse:
    options = request.options
    if request.standard_names and options is None:
        # Compatibility for clients that predate structured naming options.
        options = ExportNamingOptions(fields=list(DEFAULT_EXPORT_NAME_FIELDS))

    return ExportNamingPreviewResponse(
        filenames=build_export_names(
            request.records,
            options,
            audio_format=request.audio_format,
        )
    )
