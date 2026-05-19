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

dev:
	python3 mef_guardian.py

start:
	@echo "Iniciando MEF Structural Guardian em segundo plano..."
	@nohup python3 mef_guardian.py > guardian_run.log 2>&1 &
	@sleep 1.5
	@make status

stop:
	@echo "Parando todos os servicos..."
	-@pkill -f mef_guardian.py 2>/dev/null || true
	-@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo "Servicos encerrados."

status:
	@echo "================ STATUS DOS SERVICOS ================"
	@PID_BACKEND=$$(lsof -t -i:8000); \
	if [ -n "$$PID_BACKEND" ]; then \
		echo "Backend (Porta 8000): ONLINE (PID: $$PID_BACKEND)"; \
	else \
		echo "Backend (Porta 8000): OFFLINE"; \
	fi
	@PID_FRONTEND=$$(lsof -t -i:3000); \
	if [ -n "$$PID_FRONTEND" ]; then \
		echo "Frontend (Porta 3000): ONLINE (PID: $$PID_FRONTEND)"; \
	else \
		echo "Frontend (Porta 3000): OFFLINE"; \
	fi
	@PID_GUARDIAN=$$(pgrep -f mef_guardian.py); \
	if [ -n "$$PID_GUARDIAN" ]; then \
		echo "Guardian (mef_guardian.py): ATIVO (PID: $$PID_GUARDIAN)"; \
	else \
		echo "Guardian (mef_guardian.py): INATIVO"; \
	fi
	@echo "====================================================="

