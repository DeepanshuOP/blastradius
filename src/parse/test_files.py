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

def resolve_test_file(test_id: TestId, repo_root: Path, _tree_cache: Optional[set[str]] = None) -> FileResolution:
    """Resolve a canonical test ID to a repository-relative source path.
    
    Source roots are DISCOVERED by querying the git tree at HEAD. We avoid hardcoding
    roots like src/test/java by looking for files matching the relative path suffixes.
    """
    if _tree_cache is None:
        try:
            tree = _get_git_tree(repo_root)
        except subprocess.CalledProcessError:
            tree = set()
    else:
        tree = _tree_cache
        
    if test_id.lang in ("java", "kotlin", "groovy", "scala"):
        if not test_id.class_name:
            return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
            
        # Handle nested classes: Outer$Inner lives in Outer
        base_class = test_id.class_name.split('$')[0]
        
        candidates = []
        confidence = 1.0
        
        if '.' in test_id.class_name:
            # Fully qualified path
            rel_path = base_class.replace('.', '/')
            for ext in ['.java', '.kt', '.groovy', '.scala']:
                target_suffix = f"/{rel_path}{ext}"
                for line in tree:
                    if line.endswith(target_suffix) or line == f"{rel_path}{ext}":
                        candidates.append(line)
        else:
            # Unqualified bare class name
            for ext in ['.java', '.kt', '.groovy', '.scala']:
                target_filename = f"{base_class}{ext}"
                target_suffix = f"/{target_filename}"
                for line in tree:
                    if line.endswith(target_suffix) or line == target_filename:
                        candidates.append(line)
            confidence = 0.5  # lower confidence for unqualified
            
        candidates = list(set(candidates))
        
        if len(candidates) == 1:
            return FileResolution(path=candidates[0], status="exact", candidates_considered=1, confidence=confidence)
        elif len(candidates) > 1:
            return FileResolution(path=None, status="ambiguous", candidates_considered=len(candidates), confidence=0.0)
        else:
            if not ('.' in test_id.class_name):
                return FileResolution(path=None, status="not_found", candidates_considered=0, confidence=0.0)
            else:
                return FileResolution(path=None, status="not_found", candidates_considered=0, confidence=0.0)

            
    elif test_id.lang == "python":
        if not test_id.path:
            return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
            
        candidates = []
        target_suffix = f"/{test_id.path}"
        for line in tree:
            if line.endswith(target_suffix) or line == test_id.path:
                candidates.append(line)
                
        candidates = list(set(candidates))
        
        if len(candidates) == 1:
            return FileResolution(path=candidates[0], status="exact", candidates_considered=1, confidence=1.0)
        elif len(candidates) > 1:
            return FileResolution(path=None, status="ambiguous", candidates_considered=len(candidates), confidence=0.0)
        else:
            return FileResolution(path=None, status="not_found", candidates_considered=0, confidence=0.0)
            
    return FileResolution(path=None, status="unqualified", candidates_considered=0, confidence=0.0)
