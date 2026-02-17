#!/usr/bin/env python3
"""
Convert ComfyUI API-format workflows to Web UI format.

API format: { "node_id": { "class_type": ..., "inputs": {...} } }
Web UI format: { "nodes": [...], "links": [...], "version": 0.4, ... }

The Web UI format includes node positions and a links array needed for rendering.
"""

import json
import sys
import os
from pathlib import Path
from typing import Any


def convert_api_to_webui(api_workflow: dict[str, Any]) -> dict[str, Any]:
    """Convert API format workflow to Web UI format."""

    nodes = []
    links = []
    link_id = 1

    # Sort node IDs for consistent layout
    node_ids = sorted(api_workflow.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    # Create node ID to index mapping
    node_id_to_idx = {nid: idx for idx, nid in enumerate(node_ids)}

    # Grid layout parameters
    GRID_X = 300
    GRID_Y = 150
    COLS = 3

    for idx, node_id in enumerate(node_ids):
        node_data = api_workflow[node_id]
        class_type = node_data.get("class_type", "Unknown")
        inputs = node_data.get("inputs", {})
        meta = node_data.get("_meta", {})

        # Calculate grid position
        col = idx % COLS
        row = idx // COLS
        pos_x = 50 + col * GRID_X
        pos_y = 50 + row * GRID_Y

        # Separate widget values from links
        widget_values = []
        node_inputs = []
        node_outputs = []

        # Track which inputs are links vs widget values
        input_slot = 0
        for input_name, input_value in inputs.items():
            if isinstance(input_value, list) and len(input_value) == 2:
                # This is a link: [source_node_id, output_slot]
                source_node_id = str(input_value[0])
                source_slot = input_value[1]

                if source_node_id in node_id_to_idx:
                    # Create link: [link_id, source_node, source_slot, target_node, target_slot, type]
                    links.append([
                        link_id,
                        int(source_node_id),
                        source_slot,
                        int(node_id),
                        input_slot,
                        "*"  # Type is usually determined by the node, use wildcard
                    ])
                    node_inputs.append({
                        "name": input_name,
                        "type": "*",
                        "link": link_id
                    })
                    link_id += 1
                else:
                    # Source node not found, treat as widget value
                    widget_values.append(input_value)
                input_slot += 1
            else:
                # This is a widget value
                widget_values.append(input_value)

        # Build node entry
        node_entry = {
            "id": int(node_id),
            "type": class_type,
            "pos": [pos_x, pos_y],
            "size": {"0": 250, "1": 100},
            "flags": {},
            "order": idx,
            "mode": 0,
            "inputs": node_inputs if node_inputs else None,
            "outputs": None,  # Will be inferred by ComfyUI
            "properties": {},
            "widgets_values": widget_values if widget_values else None
        }

        # Add title from meta if available
        if meta.get("title"):
            node_entry["title"] = meta["title"]

        # Clean up None values
        node_entry = {k: v for k, v in node_entry.items() if v is not None}

        nodes.append(node_entry)

    # Build Web UI format
    webui_workflow = {
        "last_node_id": max(int(nid) for nid in node_ids) if node_ids else 0,
        "last_link_id": link_id - 1,
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {
            "ds": {
                "scale": 1,
                "offset": [0, 0]
            }
        },
        "version": 0.4
    }

    return webui_workflow


def process_file(input_path: Path, output_path: Path) -> bool:
    """Convert a single workflow file."""
    try:
        with open(input_path, 'r') as f:
            api_workflow = json.load(f)

        # Skip if already in Web UI format (has "nodes" key)
        if "nodes" in api_workflow:
            print(f"  Skipping {input_path.name} (already Web UI format)")
            return False

        webui_workflow = convert_api_to_webui(api_workflow)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(webui_workflow, f, indent=2)

        print(f"  Converted: {input_path.name} -> {output_path.name}")
        return True

    except Exception as e:
        print(f"  Error converting {input_path}: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_to_webui.py <input_dir> [output_dir]")
        print("  If output_dir is omitted, writes .webui.json files alongside originals")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    converted = 0
    skipped = 0

    for json_file in input_dir.rglob("*.json"):
        # Skip already-converted files
        if json_file.name.endswith(".webui.json"):
            continue
        # Skip this script's own file
        if json_file.name == "convert_to_webui.py":
            continue

        if output_dir:
            # Preserve directory structure in output
            rel_path = json_file.relative_to(input_dir)
            out_file = output_dir / rel_path
        else:
            # Write alongside original with .webui.json extension
            out_file = json_file.with_suffix(".webui.json")

        if process_file(json_file, out_file):
            converted += 1
        else:
            skipped += 1

    print(f"\nDone: {converted} converted, {skipped} skipped")


if __name__ == "__main__":
    main()
