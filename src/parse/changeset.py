from dataclasses import dataclass
from typing import List, Optional
import gzip
import json
from pathlib import Path
import re

@dataclass
class ChangedFile:
    filename: str
    status: str
    additions: int
    deletions: int
    previous_filename: Optional[str] = None
    patch: Optional[str] = None

@dataclass
class Changeset:
    repo: str
    pr_number: str
    files: List[ChangedFile]
    
    touches_test_file: bool
    touches_build_config: bool
    touches_ci_config: bool
    is_docs_only: bool
    is_truncated: bool
    
    is_formatting_only: Optional[bool] = None
    is_dependency_bump: Optional[bool] = None

def extract_changeset(repo: str, pr_number: str, head_sha: str, raw_dir: Path = Path("data/raw")) -> Optional[Changeset]:
    # Construct path to payload
    repo_fs = repo.replace("/", "__")
    pr_str = str(pr_number)
    pr_bucket = pr_str[-3:].zfill(3)
    pr_padded = pr_str.zfill(12)
    path = raw_dir / repo_fs / "pr" / pr_bucket / pr_padded / "pull_files.jsonl.gz"
    if not path.exists():
        return None
        
    with gzip.open(path, "rt") as f:
        data = [json.loads(line) for line in f]
        
    if not data:
        return None
        
    files_data = []
    for row in data:
        if 'body' in row:
            try:
                page_data = json.loads(row['body'])
                if isinstance(page_data, list):
                    files_data.extend(page_data)
            except: pass
        elif isinstance(row, list):
            files_data.extend(row)
        else:
            if not row.get('_footer'):
                files_data.append(row)
            
    if not files_data:
        return None
        
    files = []
    touches_test = False
    touches_build = False
    touches_ci = False
    all_docs = True if files_data else False
    
    for item in files_data:
        filename = item.get("filename", "")
        status = item.get("status", "")
        additions = item.get("additions", 0)
        deletions = item.get("deletions", 0)
        prev = item.get("previous_filename")
        patch = item.get("patch")
        
        files.append(ChangedFile(
            filename=filename,
            status=status,
            additions=additions,
            deletions=deletions,
            previous_filename=prev,
            patch=patch
        ))
        
        lower_name = filename.lower()
        if "test" in lower_name:
            touches_test = True
            
        if "build.gradle" in lower_name or "pom.xml" in lower_name or "setup.py" in lower_name:
            touches_build = True
            
        if ".github/workflows" in filename or ".travis.yml" in filename:
            touches_ci = True
            
        if not (lower_name.endswith(".md") or lower_name.endswith(".txt") or lower_name.endswith(".rst") or "docs/" in filename):
            all_docs = False

    return Changeset(
        repo=repo,
        pr_number=pr_number,
        files=files,
        touches_test_file=touches_test,
        touches_build_config=touches_build,
        touches_ci_config=touches_ci,
        is_docs_only=all_docs,
        is_truncated=(len(files) >= 300),
        is_formatting_only=None,
        is_dependency_bump=None
    )
