# -----------------------------------------------------------------------------
#  EnvComparer Parser - Crafted with ♥ by codesaksham
#  A premium developer utility to align, parse, and compare environment lists.
#  Copyright (c) 2026 codesaksham. All rights reserved.
# -----------------------------------------------------------------------------

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Set

@dataclass(frozen=True)
class EnvDiffItem:
    """Represents the difference details for a single environment variable key."""
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    status: str  # 'match', 'mismatch', 'missing_left', 'missing_right'
    is_safe: bool = False
    left_duplicates: Optional[List[str]] = None
    right_duplicates: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return asdict(self)


class EnvParser:
    """Handles standard parsing of .env formats, including quotes and comments."""

    # Pattern matches standard KEY=VALUE or KEY: VALUE format.
    # Ignores export prefixes and leading spaces.
    ENV_PATTERN = re.compile(
        r'^(?:export\s+)?([a-zA-Z0-9_\-\.]+)\s*[=:]\s*(.*)$', 
        re.IGNORECASE
    )

    @classmethod
    def parse(cls, content: str) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        """
        Parses environment variable list string into a dictionary of final values
        and a dictionary tracking all encountered values for each key (to detect duplicates).
        
        Handles comment lines, blank lines, quotes, and trailing comments safely.
        """
        env_dict: Dict[str, str] = {}
        all_values: Dict[str, List[str]] = {}
        
        if not content:
            return env_dict, all_values

        for line in content.splitlines():
            line_stripped = line.strip()
            
            # Skip empty lines and comment lines
            if not line_stripped or line_stripped.startswith('#'):
                continue

            match = cls.ENV_PATTERN.match(line_stripped)
            if not match:
                continue

            key = match.group(1).strip()
            raw_value = match.group(2).strip()

            # Handle quoted values and strip comments from non-quoted values
            value = cls._cleanup_value(raw_value)
            
            env_dict[key] = value
            if key not in all_values:
                all_values[key] = []
            all_values[key].append(value)

        # Filter all_values to keep only keys that have duplicate definitions (len > 1)
        duplicate_dict = {k: v for k, v in all_values.items() if len(v) > 1}

        return env_dict, duplicate_dict

    @classmethod
    def _cleanup_value(cls, raw_value: str) -> str:
        """Helper to resolve quotes and remove trailing comments from value parts."""
        # Check double quotes
        if raw_value.startswith('"') and raw_value.endswith('"'):
            return raw_value[1:-1]
        
        # Check single quotes
        if raw_value.startswith("'") and raw_value.endswith("'"):
            return raw_value[1:-1]

        # Handle inline trailing comments (e.g. KEY=VAL # comment)
        comment_idx = raw_value.find('#')
        if comment_idx != -1:
            before_comment = raw_value[:comment_idx]
            if not before_comment or before_comment[-1].isspace():
                return before_comment.strip()

        return raw_value


class EnvComparer:
    """Compares two parsed environment dictionaries and produces statistics and differences."""

    @classmethod
    def compare(
        cls, 
        left_dict: Dict[str, str], 
        right_dict: Dict[str, str],
        left_duplicates: Dict[str, List[str]] = None,
        right_duplicates: Dict[str, List[str]] = None,
        safe_keys: Optional[Set[str]] = None
    ) -> Tuple[List[EnvDiffItem], dict]:
        """
        Compares left and right dicts.
        Returns a sorted list of differences and summary statistics.
        If a key is found in safe_keys, it is marked as safe.
        """
        diff_items: List[EnvDiffItem] = []
        all_keys = sorted(list(set(left_dict.keys()) | set(right_dict.keys())))
        safe_keys_set = safe_keys if safe_keys else set()

        matches_count = 0
        mismatches_count = 0
        missing_left_count = 0
        missing_right_count = 0
        safe_count = 0

        for key in all_keys:
            left_val = left_dict.get(key)
            right_val = right_dict.get(key)
            
            left_dups = left_duplicates.get(key) if left_duplicates else None
            right_dups = right_duplicates.get(key) if right_duplicates else None
            
            is_safe = key in safe_keys_set

            if left_val is not None and right_val is not None:
                if left_val == right_val:
                    status = 'match'
                    matches_count += 1
                else:
                    status = 'mismatch'
                    if is_safe:
                        safe_count += 1
                    else:
                        mismatches_count += 1
            elif left_val is not None:
                status = 'missing_right'
                if is_safe:
                    safe_count += 1
                else:
                    missing_right_count += 1
            else:
                status = 'missing_left'
                if is_safe:
                    safe_count += 1
                else:
                    missing_left_count += 1

            diff_items.append(
                EnvDiffItem(
                    key=key,
                    left_value=left_val,
                    right_value=right_val,
                    status=status,
                    is_safe=is_safe,
                    left_duplicates=left_dups,
                    right_duplicates=right_dups
                )
            )

        stats = {
            "total_left": len(left_dict),
            "total_right": len(right_dict),
            "matches": matches_count,
            "mismatches": mismatches_count,
            "missing_left": missing_left_count,
            "missing_right": missing_right_count,
            "safe": safe_count,
            "left_duplicates_count": len(left_duplicates) if left_duplicates else 0,
            "right_duplicates_count": len(right_duplicates) if right_duplicates else 0,
            "has_mismatches_or_missing": (mismatches_count + missing_left_count + missing_right_count) > 0
        }

        return diff_items, stats
