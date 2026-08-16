from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_taxonomy_migration_ledger import (  # noqa: E402
    entity_ledger,
    entity_mapping_stats,
    lineage_link_accepted,
    portable_path,
    record_route_matches,
    route_similarity,
)


def route(
    route_id: str,
    *,
    model_id: str = "model_1",
    model_name: str = "Model One",
    configuration_id: str = "config_1",
    label: str = "RNA input route",
    source: str = "ranked genes",
    family: str = "text_native_token_stream",
    subtype: str = "serialized_biological_context_or_ordered_profile",
) -> dict[str, object]:
    return {
        "record_id": "record_1",
        "study_id": "study_1",
        "route_id": route_id,
        "configuration_id": configuration_id,
        "model_id": model_id,
        "model_name": model_name,
        "route_label": label,
        "lifecycle_phase": "inference",
        "source_object_normalized": source,
        "source_modality_normalized": "transcriptomics",
        "carrier_family": family,
        "carrier_subtype": subtype,
        "fusion_topology": "token_sequence_or_serialized_context",
        "text_role": "biological_payload",
        "model_visible_form_verbatim": "ranked gene tokens",
        "transformation_chain_normalized": ["rank genes", "serialize genes"],
        "task_or_configuration_verbatim": "cell annotation",
        "evidence_quote": "genes ranked by expression",
        "title": "Example paper",
    }


class TaxonomyMigrationLedgerTests(unittest.TestCase):
    def test_repository_paths_are_portable(self) -> None:
        self.assertEqual(
            portable_path(ROOT / "scripts/build_taxonomy_migration_ledger.py"),
            "scripts/build_taxonomy_migration_ledger.py",
        )

    def test_reworded_route_with_same_structural_core_is_linked(self) -> None:
        old = route("old")
        current = route(
            "current",
            label="Serialized expression profile for cell annotation",
            source="expression-ranked gene list",
        )
        score, components = route_similarity(old, current)
        self.assertTrue(lineage_link_accepted(score, components, old, current))
        result = record_route_matches("record_1", [old], [current])
        self.assertEqual(len(result["primary"]), 1)
        self.assertFalse(result["old_unmatched"])
        self.assertFalse(result["current_unmatched"])

    def test_unrelated_routes_are_not_forced_by_assignment(self) -> None:
        old = route("old")
        current = route(
            "current",
            model_id="model_2",
            model_name="Vision Decoder",
            configuration_id="config_2",
            label="Histology diffusion state",
            source="whole slide image",
            family="geometric_or_diffusion_state_carrier",
            subtype="diffusion_or_flow_state",
        )
        current.update(
            {
                "lifecycle_phase": "pretraining",
                "source_modality_normalized": "histology/slide image",
                "fusion_topology": "side_or_generative_conditioning",
                "text_role": "no_text_on_this_route",
                "model_visible_form_verbatim": "noisy latent image",
                "transformation_chain_normalized": ["encode image", "add noise"],
                "task_or_configuration_verbatim": "image generation",
                "evidence_quote": "diffusion latent",
            }
        )
        result = record_route_matches("record_1", [old], [current])
        self.assertFalse(result["primary"])
        self.assertEqual([row["route_id"] for row in result["old_unmatched"]], ["old"])
        self.assertEqual(
            [row["route_id"] for row in result["current_unmatched"]], ["current"]
        )

    def test_entity_ledger_preserves_stable_ids_and_route_supported_renames(self) -> None:
        old = [route("old")]
        current = [route("current")]
        primary = record_route_matches("record_1", old, current)["primary"]
        stable = entity_ledger("model", old, current, primary)
        self.assertEqual(stable[0]["mapping_status"], "stable_id")

        renamed = route("renamed", model_id="model_2", model_name="Model One v2")
        renamed_primary = record_route_matches("record_1", old, [renamed])["primary"]
        ledger = entity_ledger("model", old, [renamed], renamed_primary)
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["mapping_status"], "route_supported_mapping")
        stats = entity_mapping_stats("model", ledger, old, [renamed])
        self.assertEqual(stats["mapping_edges"], 1)
        self.assertEqual(stats["mapped_old_entities"], 1)
        self.assertEqual(stats["mapped_current_entities"], 1)
        self.assertEqual(stats["unmapped_old_entities"], 0)


if __name__ == "__main__":
    unittest.main()
