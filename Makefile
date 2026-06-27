.PHONY: setup ingest validate-candidates load-candidates coordinate-status dbt-run dbt-test test dashboard lint clean

setup:
	pip install -r requirements.txt
	@echo "Dependencies installed. Copy .env.example to .env and configure your database credentials."

ingest:
	python -m src.ingestion.run_pipeline

validate-candidates:
	python -m src.ingestion.validate_candidates

coordinate-status:
	python -m src.ingestion.coordinate_status

load-candidates: validate-candidates
	python -m src.ingestion.load_candidates

dbt-run:
	cd dbt && dbt run --profiles-dir .

dbt-test:
	cd dbt && dbt test --profiles-dir .

test:
	pytest tests/ -v

dashboard:
	streamlit run dashboard/app.py

lint:
	flake8 src/ tests/

clean:
	find data/raw -type f ! -name '.gitkeep' -delete
	@echo "Cleaned raw data files."
