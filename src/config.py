"""Configuration loading for ADIF.

Two rules this module exists to enforce:

NFR-6 — every threshold, weight, stage toggle and path lives in one YAML file.
Nothing else under ``src/`` may hardcode a tunable value.

D11 (decisions.md) — matching thresholds and confidence bands are deliberately
unset until they are derived by grid search on scratch schemas. This module
represents "unset" as ``None`` and raises :class:`UnsetTunable` when such a
value is read, so an un-tuned prototype fails loudly instead of quietly running
on an invented default and producing a number that looks like a result.

``extra="forbid"`` is set on every model: a typo in the frozen config file is a
provenance problem, not a silently ignored key.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AdifConfig",
    "UnsetTunable",
    "load_config",
    "require",
]

DEFAULT_CONFIG_PATH = Path("config/default.yaml")


class UnsetTunable(RuntimeError):
    """Raised when a tunable that has not yet been empirically derived is read.

    See decisions.md D11. This is not a bug to work around by supplying a
    default — it means the grid search has not been run yet.
    """


def require(value: Any | None, name: str) -> Any:
    """Return ``value``, or raise :class:`UnsetTunable` if it is ``None``.

    Args:
        value: The tunable read from configuration.
        name: Dotted config path, used in the error message.

    Raises:
        UnsetTunable: If ``value`` is ``None``.
    """
    if value is None:
        raise UnsetTunable(
            f"Config value '{name}' is unset. Per decisions.md D11 it must be "
            f"derived by grid search on scratch schemas before use — do not "
            f"substitute a default."
        )
    return value


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Paths(_Strict):
    cdm_schema: Path
    cdm_context: Path
    cdm_provenance: Path
    alias_vocabulary: Path
    adid_grammar: Path
    embedding_cache: Path
    upload_store: Path
    template_db: Path
    run_records: Path
    heldout_dir: Path


class Ingestion(_Strict):
    max_file_size_mb: int = Field(gt=0)
    max_rows: int = Field(gt=0)
    sample_values_per_column: int = Field(gt=0)
    encodings: list[str]
    csv_delimiters: list[str]


class Analysis(_Strict):
    type_inference_agreement: float = Field(gt=0, le=1)
    date_formats: list[str]
    boolean_true: list[str]
    boolean_false: list[str]


class Normalisation(_Strict):
    case_fold: bool
    strip_separators: list[str]
    split_camel_case: bool
    collapse_whitespace: bool
    stopwords: list[str]
    abbreviations: dict[str, str]


class AliasStage(_Strict):
    enabled: bool


class FuzzyStage(_Strict):
    enabled: bool
    threshold: float | None
    top_k: int = Field(gt=0)
    scorers: list[str]
    combine: Literal["max", "weighted_mean"]
    partial_min_length: int = Field(ge=0)
    partial_min_length_ratio: float = Field(ge=0, le=1)


class SemanticStage(_Strict):
    enabled: bool
    threshold: float | None
    top_k: int = Field(gt=0)
    model: str
    model_revision: str | None


class ValueStage(_Strict):
    enabled: bool
    threshold: float | None
    top_k: int = Field(gt=0)
    signatures: Path


class Stages(_Strict):
    alias: AliasStage
    fuzzy: FuzzyStage
    semantic: SemanticStage
    value: ValueStage


class Matching(_Strict):
    arbitration: Literal["cascade", "parallel"]
    stage_order: list[str]
    stages: Stages


class ConfidenceBands(_Strict):
    auto_accept: float | None
    review: float | None
    reject: float | None


class Confidence(_Strict):
    calibration: Literal["platt", "isotonic", "binned"] | None
    bands: ConfidenceBands


class Determinism(_Strict):
    random_seed: int
    torch_num_threads: int = Field(gt=0)


class Runtime(_Strict):
    offline: bool


class AdifConfig(_Strict):
    """The whole tunable surface of the system, loaded from one file."""

    version: str
    paths: Paths
    ingestion: Ingestion
    analysis: Analysis
    normalisation: Normalisation
    matching: Matching
    confidence: Confidence
    determinism: Determinism
    runtime: Runtime

    source_path: Path | None = None
    source_sha256: str | None = None

    def enabled_stages(self) -> list[str]:
        """Return configured stage order, filtered to stages that are enabled.

        Used by the ablation harness (M14) to record which conditions a run
        actually exercised, rather than trusting the config file name.
        """
        toggles = {
            "alias": self.matching.stages.alias.enabled,
            "fuzzy": self.matching.stages.fuzzy.enabled,
            "semantic": self.matching.stages.semantic.enabled,
            "value": self.matching.stages.value.enabled,
        }
        return [s for s in self.matching.stage_order if toggles.get(s, False)]

    def unset_matching_thresholds(self) -> list[str]:
        """Thresholds required by *enabled* stages that are still unset.

        Narrower than :meth:`unset_tunables` on purpose. Running the cascade
        needs the thresholds of the stages it will execute — it does not need
        the confidence bands, which are a downstream presentation concern. A
        guard that demands everything blocks work that is legitimately ready.
        """
        pending: list[str] = []
        enabled = set(self.enabled_stages())
        for stage in ("fuzzy", "semantic", "value"):
            if stage in enabled and getattr(self.matching.stages, stage).threshold is None:
                pending.append(f"matching.stages.{stage}.threshold")
        return pending

    def unset_tunables(self) -> list[str]:
        """List every tunable still awaiting empirical derivation (D11).

        Surfaced by ``/health`` so the build state is visible without reading
        the config file.
        """
        pending: list[str] = []
        if self.matching.stages.fuzzy.threshold is None:
            pending.append("matching.stages.fuzzy.threshold")
        if self.matching.stages.semantic.threshold is None:
            pending.append("matching.stages.semantic.threshold")
        if self.matching.stages.value.threshold is None:
            pending.append("matching.stages.value.threshold")
        if self.confidence.calibration is None:
            pending.append("confidence.calibration")
        for band in ("auto_accept", "review", "reject"):
            if getattr(self.confidence.bands, band) is None:
                pending.append(f"confidence.bands.{band}")
        return pending


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> AdifConfig:
    """Load and validate the ADIF configuration file.

    Args:
        path: Path to the YAML config. Defaults to ``config/default.yaml``.

    Returns:
        A validated :class:`AdifConfig` carrying the file's SHA-256, so any run
        record can name the exact config that produced it (FR-14.5).

    Raises:
        FileNotFoundError: If the config file does not exist.
        pydantic.ValidationError: On unknown keys or wrong types.
    """
    path = Path(path)
    raw_bytes = path.read_bytes()
    data = yaml.safe_load(raw_bytes)
    cfg = AdifConfig.model_validate(data)
    cfg.source_path = path
    cfg.source_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    return cfg
