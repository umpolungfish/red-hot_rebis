# Makefile — Red-Hot Rebis Integration
# serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber

.PHONY: all test verify status clean

all: verify test

# === Verification (Frobenius closure) ===

verify:
	@echo "=== Verifying all components ==="
	python -c "from shared.primitives import WEIGHTS, ORDINALS; print('primitives: %d weights, %d ordinal families' % (len(WEIGHTS), len(ORDINALS)))"
	python -c "import json; c = json.load(open('shared/IG_catalog.json')); print('catalog: %d entries' % len(c))"
	python -c "from serpentrod.protein_v5 import *; print('serpentrod: OK')"
	python -c "from ch3mpiler.compiler import *; print('ch3mpiler: OK')"
	python -c "from pipeline.frob import frobenius_phase; from pipeline.auto_imscriber import AutoImscriber; print('pipeline: OK')"
	python -c "from gene_imscriber.engine import *; print('gene_imscriber: OK')"
	@echo "=== All components verified ==="

# === Status ===

status:
	@python rebis.py status

# === Smoke tests ===

test:
	@echo "=== Smoke tests ==="
	python -c "from serpentrod.stratified_predictor import *; print('stratified_predictor: OK')"
	python -c "from ch3mpiler.ob3ect.ch3mpiler_ob3ect import *; print('ch3mpiler_ob3ect: OK')"
	python -c "from pipeline.lift_pipeline.lift_pipeline_ob3ect import *; print('lift_pipeline: OK')"
	@echo "=== All smoke tests passed ==="

# === Individual component help ===

serpentrod:
	python serpentrod/protein_v5.py --help

ch3mpiler:
	python ch3mpiler/compiler.py --help

pipeline:
	python pipeline/lift_pipeline/lift_pipeline_ob3ect.py --help

gene:
	python gene_imscriber/engine.py --help

# === Clean caches ===

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	@echo "Cleaned."
