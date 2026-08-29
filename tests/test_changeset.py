from pathlib import Path
from src.parse.changeset import extract_changeset

def test_extract_changeset():
    # Decentralized identity PR 577
    repo = "decentralized-identity/universal-resolver"
    pr = "577"
    head_sha = "000000000577"
    # Actually, the head_sha is 000000000577 in that dir structure? Let's check.
    cs = extract_changeset(repo, pr, head_sha)
    assert cs is not None
    assert len(cs.files) == 3
    assert cs.is_docs_only is False
    assert cs.touches_test_file is False
    assert cs.touches_build_config is False
