from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal
import subprocess
from .test_ids import TestId

@dataclass(frozen=True)
class FileResolution:
    path: Optional[str]
    status: Literal["exact", "ambiguous", "unqualified", "not_found"]
    candidates_considered: int
    confidence: float

def _get_git_tree(repo_root: Path) -> set[str]:
    out = subprocess.check_output(['git', '-C', str(repo_root), 'ls-tree', '-r', 'HEAD', '--name-only'], text=True)
    return set(out.splitlines())

def resolve_test_file(test_id: TestId, repo_root: Path, _tree_cache: Optional[dict[str, list[str]]] = None) -> FileResolution:
    if _tree_cache is None:
        try:
            tree_paths = _get_git_tree(repo_root)
        except subprocess.CalledProcessError:
            tree_paths = set()
        _tree_cache = {}
        for p in tree_paths:
            basename = p.split("/")[-1]
            if basename not in _tree_cache:
                _tree_cache[basename] = []
            _tree_cache[basename].append(p)
            
    if test_id.lang in ("java", "kotlin", "groovy", "scala"):
        if not test_id.class_name:
            return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
            
        base_class = test_id.class_name.split('$')[0]
        
        candidates = []
        confidence = 1.0
        
        if '.' in test_id.class_name:
            rel_path = base_class.replace('.', '/')
            for ext in ['.java', '.kt', '.groovy', '.scala']:
                target_filename = f"{base_class.split('.')[-1]}{ext}"
                target_suffix = f"{rel_path}{ext}"
                
                for p in _tree_cache.get(target_filename, []):
                    if p.endswith("/" + target_suffix) or p == target_suffix:
                        candidates.append(p)
        else:
            for ext in ['.java', '.kt', '.groovy', '.scala']:
                target_filename = f"{base_class}{ext}"
                for p in _tree_cache.get(target_filename, []):
                    candidates.append(p)
            confidence = 0.5
            
        candidates = list(set(candidates))
        
        if len(candidates) == 1:
            return FileResolution(path=candidates[0], status="exact", candidates_considered=1, confidence=confidence)
        elif len(candidates) > 1:
            return FileResolution(path=None, status="ambiguous", candidates_considered=len(candidates), confidence=0.0)
        else:
            return FileResolution(path=None, status="not_found", candidates_considered=0, confidence=0.0)
            
    elif test_id.lang == "python":
        if not test_id.path:
            return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
            
        candidates = []
        target_filename = test_id.path.split("/")[-1]
        for p in _tree_cache.get(target_filename, []):
            if p.endswith("/" + test_id.path) or p == test_id.path:
                candidates.append(p)
                
        candidates = list(set(candidates))
        
        if len(candidates) == 1:
            return FileResolution(path=candidates[0], status="exact", candidates_considered=1, confidence=1.0)
        elif len(candidates) > 1:
            return FileResolution(path=None, status="ambiguous", candidates_considered=len(candidates), confidence=0.0)
        else:
            return FileResolution(path=None, status="not_found", candidates_considered=0, confidence=0.0)
            
    return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
