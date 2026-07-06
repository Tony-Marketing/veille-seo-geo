"""Tests for Google Search Console SQLAlchemy models."""

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    GscCoverageSnapshot,
    GscImportRun,
    GscIndexingInspection,
    GscOAuthCredential,
    GscPerformanceDaily,
    GscProperty,
    GscSitemap,
)


def test_gsc_models_persist_core_entities(db_session: Session) -> None:
    """GSC models can be persisted with their expected fields."""

    credential = GscOAuthCredential(
        provider="google",
        scopes=["scope"],
        encrypted_access_token="encrypted-access",
        encrypted_refresh_token="encrypted-refresh",
        token_expires_at=datetime.now(UTC),
        status="ACTIVE",
    )
    db_session.add(credential)

    gsc_property = GscProperty(site_url="https://example.com/", property_type="url_prefix", is_verified=True)
    db_session.add(gsc_property)
    db_session.commit()
    db_session.refresh(gsc_property)

    import_run = GscImportRun(property_id=gsc_property.id, status="COMPLETED", import_type="full", rows_imported=4)
    db_session.add(import_run)
    db_session.commit()
    db_session.refresh(import_run)

    performance = GscPerformanceDaily(
        property_id=gsc_property.id,
        import_run_id=import_run.id,
        date=date(2026, 7, 1),
        page="https://example.com/",
        query="example",
        device="DESKTOP",
        country="FRA",
        search_type="web",
        clicks=10,
        impressions=100,
        ctr=0.1,
        position=3.2,
    )
    coverage = GscCoverageSnapshot(
        property_id=gsc_property.id,
        import_run_id=import_run.id,
        date=date(2026, 7, 1),
        category="indexed",
        state="valid",
        pages_count=12,
    )
    indexing = GscIndexingInspection(
        property_id=gsc_property.id,
        import_run_id=import_run.id,
        inspected_url="https://example.com/",
        coverage_state="Submitted and indexed",
        indexing_state="INDEXING_ALLOWED",
        verdict="PASS",
        inspected_at=datetime.now(UTC),
    )
    sitemap = GscSitemap(
        property_id=gsc_property.id,
        import_run_id=import_run.id,
        sitemap_url="https://example.com/sitemap.xml",
        errors=0,
        warnings=0,
    )
    db_session.add_all([performance, coverage, indexing, sitemap])
    db_session.commit()
    db_session.refresh(gsc_property)

    assert credential.id is not None
    assert gsc_property.import_runs == [import_run]
    assert performance.clicks == 10
    assert coverage.pages_count == 12
    assert indexing.verdict == "PASS"
    assert sitemap.sitemap_url.endswith("sitemap.xml")
