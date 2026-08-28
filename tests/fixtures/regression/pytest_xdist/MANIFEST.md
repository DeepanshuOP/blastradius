# Pytest-xdist Regression Fixtures Manifest

Per ROADMAP §9.1 (T1.1d) and amendment rulings.
Captures real GitHub Actions workflow execution logs running `pytest` under `pytest-xdist` multi-worker parallel execution, where live progress lines use the inverted token layout:
`[gw<N>] [<pct>%] (FAILED|ERROR) <node_id>`

These labels are provisional and feed no reported metric until ruled on.

---

## 1. apache__beam__081645128008.txt

- **Repository:** `apache/beam`
- **Job ID:** `081645128008`
- **ISIZE (Uncompressed Bytes):** `671,090 bytes` (655.36 KB)
- **Why Chosen:** Smallest real beam pytest-xdist execution log in `data/raw` exercising the multi-worker setup/collection failure shape (`ERROR`) across multiple workers (`gw0` through `gw5`).
- **Footer Count:** `17 errors` (Line 6109: `====== 1 passed, 12 skipped, 23 warnings, 17 errors in 654.62s (0:10:54) =======`)
- **Derived by Raw Grep Command:**
  ```bash
  grep -nE '\[gw[0-9]+\].*(FAILED|ERROR)' tests/fixtures/regression/pytest_xdist/apache__beam__081645128008.txt
  ```
- **Derived Failing Node IDs (17 error outcomes):**
  - Line 4172: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_invalid_query_on_non_existent_collection`
  - Line 4174: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_invalid_query_on_non_existent_field`
  - Line 4176: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_non_existent_partition`
  - Line 4178: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_on_auto_id_primary_key`
  - Line 4180: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_on_existent_collection_with_default_schema`
  - Line 4182: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_with_batching`
  - Line 4184: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_write_with_custom_column_specifications`
  - Line 4197: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_vector_search_with_inner_product_similarity`
  - Line 4198: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_empty_input_chunks`
  - Line 4200: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_filtered_search_with_cosine_similarity_and_batching`
  - Line 4202: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_missing_primary_key_in_entity`
  - Line 4204: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_keyword_search_with_inner_product_sparse_embedding`
  - Line 4206: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_invalid_write_on_non_existent_collection`
  - Line 4207: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_vector_search_with_euclidean_distance`
  - Line 4208: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_filtered_search_with_bm25_full_text_and_batching`
  - Line 4209: `[ERROR]` `apache_beam/ml/rag/enrichment/milvus_search_it_test.py::TestMilvusSearchEnrichment::test_hybrid_search`
  - Line 4211: `[ERROR]` `apache_beam/ml/rag/ingestion/milvus_search_it_test.py::TestMilvusVectorWriterConfig::test_idempotent_write`
- **Arithmetic Check:** Derived Identifier Count (17) **==** Footer Count (17 errors). Exact match.

---

## 2. apache__beam__077952110001.txt

- **Repository:** `apache/beam`
- **Job ID:** `077952110001`
- **ISIZE (Uncompressed Bytes):** `1,852,594 bytes` (1.77 MB)
- **Why Chosen:** Smallest real beam pytest-xdist execution log in `data/raw` exercising the single test assertion failure shape (`FAILED`).
- **Footer Count:** `1 failed` (Line 7226: `==== 1 failed, 1594 passed, 626 skipped, 728 warnings in 273.25s (0:04:33) =====`)
- **Derived by Raw Grep Command:**
  ```bash
  grep -nE '\[gw[0-9]+\].*(FAILED|ERROR)' tests/fixtures/regression/pytest_xdist/apache__beam__077952110001.txt
  ```
- **Derived Failing Node IDs (1 fail outcome):**
  - Line 3181: `[FAILED]` `apache_beam/runners/dataflow/internal/apiclient_test.py::UtilTest::test_environment_packages_with_hash`
- **Arithmetic Check:** Derived Identifier Count (1) **==** Footer Count (1 failed). Exact match.
