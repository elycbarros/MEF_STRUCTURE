.PHONY: build-rust test clean bench

build-rust:
	cd mef_engine/structural_core_rs && \
	export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 && \
	maturin build --release && \
	pip install target/wheels/*.whl --force-reinstall

test: build-rust
	export PYTHONPATH="$(shell pwd):$(shell pwd)/mef_engine" && \
	python3 tests/test_rust_pdelta.py && \
	python3 tests/scale_test.py

bench: build-rust
	export PYTHONPATH="$(shell pwd):$(shell pwd)/mef_engine" && \
	python3 tests/benchmark_pdelta.py

clean:
	cd mef_engine/structural_core_rs && cargo clean
	rm -rf mef_engine/structural_core_rs/target/wheels/*.whl
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
