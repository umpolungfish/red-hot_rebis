# Makefile — Red-Hot Rebis Integration
# rebis.<x> — serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber
# Callable from anywhere after: make install

.PHONY: all test verify status clean install uninstall reinstall editable

all: verify test

# === Installation (anywhere-callable) ===

install:
	@echo "=== Installing rebis (callable from anywhere) ==="
	pip install -e .
	@echo ""
	@echo "✅ rebis installed. Usage from any directory:"
	@echo "   rebis status         — Package status"
	@echo "   rebis verify         — Frobenius closure check"
	@echo "   rebis run <target>   — Load a subsystem"
	@echo "   rebis demo <name>    — Run a demo"
	@echo "   python3 -m rebis status"
	@echo "   python3 -c 'import rebis; rebis.p4ra.Belnap.T'"

uninstall:
	@echo "=== Uninstalling rebis ==="
	pip uninstall -y red-hot-rebis 2>/dev/null || true

reinstall: uninstall install

editable:
	@echo "=== Installing rebis in editable mode ==="
	pip install -e .
	@echo ""
	@echo "✅ Editable install complete."

# === Verification (Frobenius closure) ===

verify:
	@echo "=== Verifying all components ==="
	python -c "from shared.primitives import WEIGHTS, ORDINALS; print('primitives: %d weights, %d ordinal families' % (len(WEIGHTS), len(ORDINALS)))"
	python -c "import json; c = json.load(open('shared/IG_catalog.json')); print('catalog: %d entries' % len(c))"
	@python -m rebis verify
	@echo ""
	@echo "=== All components verified ==="

# === Status ===

status:
	@rebis status

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