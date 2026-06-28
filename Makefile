.PHONY: verify figures docker-up reproduce clean

verify:
	go build ./...
	go test ./...
	go run ./cmd/verify_artifacts

figures:
	uv run scripts/generate_plots.py

docker-up:
	docker-compose up -d

reproduce: verify figures
	@echo "Reproduction complete."

clean:
	rm -rf artifacts/experiments/*.csv
	rm -rf artifacts/experiments/*.json
	rm -rf artifacts/publication/*.png
	rm -rf artifacts/publication/plotly/*.html
