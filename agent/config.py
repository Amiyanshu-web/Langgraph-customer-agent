from typing import Any, Dict, Tuple

import yaml


def load_stage_mapping(path: str = "config/stages.yaml") -> Dict[str, Dict[str, str]]:
    """
    Load stage->ability->server mapping from YAML.
    Returns a dict like: { stage_name: { ability_name: server } }
    """
    with open(path, "r", encoding="utf-8") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)

    mapping: Dict[str, Dict[str, str]] = {}
    for st in cfg.get("stages", []):
        stage_name = st.get("name")
        abilities = st.get("abilities", [])
        mapping[stage_name] = {a.get("name"): a.get("server") for a in abilities}
    return mapping


def load_threshold_and_prompts(path: str = "config/stages.yaml") -> Tuple[int, Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)
    threshold = int(cfg.get("decide_threshold", 90))
    prompts: Dict[str, str] = {}
    for st in cfg.get("stages", []):
        name = st.get("name")
        prompts[name] = st.get("prompt", "")
    return threshold, prompts

