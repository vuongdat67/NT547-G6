package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"time"

	"github.com/caliber/internal/experiments"
)

type parameterSweepRow struct {
	VSat            int64 `json:"vSat"`
	VDepSat         int64 `json:"vDepSat"`
	VColSat         int64 `json:"vColSat"`
	WidthCRABSat    int64 `json:"widthCRABSat"`
	WidthCALIBERSat int64 `json:"widthCALIBERSat"`
}

type experimentReportM2 struct {
	GeneratedAtUTC string              `json:"generatedAtUtc"`
	Source         string              `json:"source"`
	Rows           []parameterSweepRow `json:"rows"`
}

func main() {
	startAll := time.Now()
	
	var rows []parameterSweepRow

	// We sweep vSat from 1,500,000 to 2,500,000 in steps of 10,000
	for v := int64(1_500_000); v <= 2_500_000; v += 10_000 {
		// As per paper, v_dep is 0.5 * v (e.g., 1M when v=2M)
		vDep := int64(math.Round(float64(v) * 0.50))
		vCol := int64(math.Round(float64(vDep) * 0.25)) // not deeply relevant for width but needed

		cStar := experiments.CStar(v, vDep, vCol)
		
		widthCRAB := crabWidthWithCollateral(v, vDep, vCol, cStar)
		widthCALIBER := experiments.LinkedWidth(v, vDep, vCol, cStar)

		rows = append(rows, parameterSweepRow{
			VSat:            v,
			VDepSat:         vDep,
			VColSat:         vCol,
			WidthCRABSat:    widthCRAB,
			WidthCALIBERSat: widthCALIBER,
		})
	}

	rep := experimentReportM2{
		GeneratedAtUTC: time.Now().UTC().Format(time.RFC3339),
		Source:         "caliber experiment runner (m2: parameter sensitivity range)",
		Rows:           rows,
	}

	must(os.MkdirAll(filepath.Join("artifacts", "experiments"), 0o755))
	jsonPath := filepath.Join("artifacts", "experiments", "experiment_summary_m2.json")

	b, err := json.MarshalIndent(rep, "", "  ")
	must(err)
	must(os.WriteFile(jsonPath, b, 0o644))

	fmt.Println("Generated experiment artifacts for M2:")
	fmt.Println(" -", jsonPath)
	fmt.Printf("Done in %.2f ms\n", float64(time.Since(startAll).Microseconds())/1000.0)
}

func crabWidthWithCollateral(vSat, vDepSat, vColSat, cPrimeSat int64) int64 {
	ub := vSat + cPrimeSat + vDepSat
	lb := cPrimeSat + vColSat
	return ub - lb
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
