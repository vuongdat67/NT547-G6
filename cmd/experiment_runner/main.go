package main

import (
	"crypto/sha256"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"os"
	"path/filepath"
	"time"

	"github.com/caliber/internal/attack"
	"github.com/caliber/internal/experiments"
)

const (
	defaultVSat int64 = 2_000_000
	epsilonSat  int64 = 1_000
)

type gridConfig = experiments.Config

type sweepRow struct {
	ConfigID               string `json:"configId"`
	VSat                   int64  `json:"vSat"`
	VDepSat                int64  `json:"vDepSat"`
	VColSat                int64  `json:"vColSat"`
	Kappa                  int    `json:"kappa"`
	HopsN                  int    `json:"hopsN"`
	WidthCRABSat           int64  `json:"widthCRABSat"`
	WidthCRABByzantineSat  int64  `json:"widthCRABByzantineSat"`
	WidthCRABPrime1_25Sat  int64  `json:"widthCRABPrime1_25Sat"`
	WidthCRABPrime1_50Sat  int64  `json:"widthCRABPrime1_50Sat"`
	WidthCRABPrime2_00Sat  int64  `json:"widthCRABPrime2_00Sat"`
	CStarSat               int64  `json:"cStarSat"`
	WidthCALIBERCStarMinus  int64  `json:"widthCALIBERCStarMinusEpsilonSat"`
	WidthCALIBERCStar       int64  `json:"widthCALIBERCStarSat"`
	WidthCALIBERCStarPlus   int64  `json:"widthCALIBERCStarPlusEpsilonSat"`
	CNStarSat              int64  `json:"cNStarSat"`
	HeConditionValid       bool   `json:"heConditionValid"`
	HeConditionReason      string `json:"heConditionReason"`
	MADStandaloneWidthSat  int64  `json:"madStandaloneWidthSat"`
	HeStandaloneMarginSat  int64  `json:"heStandaloneMarginSat"`
	ActiveMinerCoverageMAD bool   `json:"activeMinerCoverageMAD"`
	Notes                  string `json:"notes"`
	ElapsedMicros          int64  `json:"elapsedMicros"`
	GeneratedAtUTC         string `json:"generatedAtUtc"`
}

type parallelSwapRow struct {
	N           int   `json:"n"`
	CNStarSat   int64 `json:"cNStarSat"`
	OverheadSat int64 `json:"overheadAboveCRABByzSat"`
}

type kappaWindowRow struct {
	RhoH           float64 `json:"rhoH"`
	Kappa          int     `json:"kappa"`
	Runs           int     `json:"runs"`
	TrialsPerRun   int     `json:"trialsPerRun"`
	AnalyticalProb float64 `json:"analyticalProb"`
	SimulatedProbMean float64 `json:"simulatedProbMean"`
	SimulatedProbStd  float64 `json:"simulatedProbStd"`
	AbsDiffPct     float64 `json:"absDiffPct"`
}

type kappaWindowReport struct {
	Seed        int64            `json:"seed"`
	GeneratedAt string           `json:"generatedAtUtc"`
	Rows        []kappaWindowRow `json:"rows"`
}

type telemetryDistribution struct {
	Leaves      int       `json:"leaves"`
	TimesMicros []float64 `json:"timesMicros"`
}

type telemetry struct {
	RegtestBlocksObserved           int64                   `json:"regtestBlocksObserved"`
	SignetBlocksObserved            int64                   `json:"signetBlocksObserved"`
	WitnessGenerationDistributions  []telemetryDistribution `json:"witnessGenerationDistributions"`
	ScriptValidationDistributions   []telemetryDistribution `json:"scriptValidationDistributions"`
	LinkedACSRegtestArtifactPresent bool                    `json:"linkedACSRegtestArtifactPresent"`
	LinkedACSSignetArtifactPresent  bool                    `json:"linkedACSSignetArtifactPresent"`
	GeneratedAtUTC                  string                  `json:"generatedAtUtc"`
}

type experimentReport struct {
	GeneratedAtUTC    string                           `json:"generatedAtUtc"`
	Source            string                           `json:"source"`
	GridCount         int                              `json:"gridCount"`
	SweepRows         []sweepRow                       `json:"sweepRows"`
	ParallelSwapRows  []parallelSwapRow                `json:"parallelSwapRows"`
	MultiHopRows      []parallelSwapRow                `json:"multiHopRows"`
	AttackDecisions   attack.DecisionReport            `json:"attackDecisions"`
	AttackTimeline    experiments.AttackTimelineReport `json:"attackTimeline"`
	BaselinePipelines []experiments.Pipeline           `json:"baselinePipelines"`
	Telemetry         telemetry                        `json:"telemetry"`
}

func main() {
	startAll := time.Now()
	configs := buildGridConfigs(defaultVSat)

	sweepRows := make([]sweepRow, 0, len(configs))
	for _, cfg := range configs {
		sweepRows = append(sweepRows, evaluateGridRow(cfg))
	}
	baselinePipelines := buildBaselinePipelines(configs)

	parallelSwaps := buildParallelSwapTable(defaultVSat, 0.50, 0.25)
	attackDecisions := attack.BuildDecisionReport()
	attackTimeline := experiments.BuildAttackTimelineReport()
	
	// For statistical variance, we run 100 seeds with 1000 trials each instead of 1 seed with 100_000 trials.
	kappaReport := buildKappaWindowReport(42, 100, 1000)
	tel := collectTelemetry()

	rep := experimentReport{
		GeneratedAtUTC:    time.Now().UTC().Format(time.RFC3339),
		Source:            "caliber experiment runner (check-list + experiment_guide criteria)",
		GridCount:         len(configs),
		SweepRows:         sweepRows,
		ParallelSwapRows:  parallelSwaps,
		MultiHopRows:      parallelSwaps,
		AttackDecisions:   attackDecisions,
		AttackTimeline:    attackTimeline,
		BaselinePipelines: baselinePipelines,
		Telemetry:         tel,
	}

	must(os.MkdirAll(filepath.Join("artifacts", "experiments"), 0o755))
	jsonPath := filepath.Join("artifacts", "experiments", "experiment_summary.json")
	csvPath := filepath.Join("artifacts", "experiments", "parameter_sweep.csv")
	multiHopPath := filepath.Join("artifacts", "experiments", "multi_hop_table.csv")
	parallelSwapsPath := filepath.Join("artifacts", "experiments", "parallel_swaps_table.csv")
	attackDecisionsPath := filepath.Join("artifacts", "experiments", "attack_decisions.json")
	attackTimelineJSONPath := filepath.Join("artifacts", "experiments", "attack_timeline.json")
	attackTimelineCSVPath := filepath.Join("artifacts", "experiments", "attack_timeline.csv")
	baselinePipelinesPath := filepath.Join("artifacts", "experiments", "baseline_pipelines.json")
	kappaSimPath := filepath.Join("artifacts", "kappa_window_sim.json")
	kappaCSVPath := filepath.Join("artifacts", "experiments", "kappa_window_table.csv")

	b, err := json.MarshalIndent(rep, "", "  ")
	must(err)
	must(os.WriteFile(jsonPath, b, 0o644))
	must(writeSweepCSV(csvPath, sweepRows))
	must(writeParallelSwapCSV(multiHopPath, parallelSwaps))
	must(writeParallelSwapCSV(parallelSwapsPath, parallelSwaps))
	must(writeJSON(attackDecisionsPath, attackDecisions))
	must(writeJSON(attackTimelineJSONPath, attackTimeline))
	must(writeAttackTimelineCSV(attackTimelineCSVPath, attackTimeline.Rows))
	must(writeJSON(baselinePipelinesPath, baselinePipelines))
	must(writeJSON(kappaSimPath, kappaReport))
	must(writeKappaWindowCSV(kappaCSVPath, kappaReport.Rows))

	fmt.Println("Generated experiment artifacts:")
	fmt.Printf("Done in %.2f ms\n", float64(time.Since(startAll).Microseconds())/1000.0)
}

func buildGridConfigs(vSat int64) []gridConfig {
	return experiments.BuildGridConfigs(vSat)
}

func buildBaselinePipelines(configs []gridConfig) []experiments.Pipeline {
	out := make([]experiments.Pipeline, 0, len(configs)*2)
	for _, cfg := range configs {
		out = append(out, experiments.BuildMADStandalone(cfg, 0))
		out = append(out, experiments.BuildHeStandalone(cfg, 0))
	}
	return out
}

func evaluateGridRow(cfg gridConfig) sweepRow {
	rowStart := time.Now()
	cBase := experiments.CStar(cfg.VSat, cfg.VDepSat, cfg.VColSat)
	cPrime125 := int64(math.Round(float64(cBase) * 1.25))
	cPrime150 := int64(math.Round(float64(cBase) * 1.50))
	cPrime200 := int64(math.Round(float64(cBase) * 2.00))

	widthCRAB := crabWidthWithCollateral(cfg.VSat, cfg.VDepSat, cfg.VColSat, cBase)
	widthCRABPrime125 := crabWidthWithCollateral(cfg.VSat, cfg.VDepSat, cfg.VColSat, cPrime125)
	widthCRABPrime150 := crabWidthWithCollateral(cfg.VSat, cfg.VDepSat, cfg.VColSat, cPrime150)
	widthCRABPrime200 := crabWidthWithCollateral(cfg.VSat, cfg.VDepSat, cfg.VColSat, cPrime200)
	cStar := cBase
	widthCStarMinus := experiments.LinkedWidth(cfg.VSat, cfg.VDepSat, cfg.VColSat, cStar-epsilonSat)
	widthCStar := experiments.LinkedWidth(cfg.VSat, cfg.VDepSat, cfg.VColSat, cStar)
	widthCStarPlus := experiments.LinkedWidth(cfg.VSat, cfg.VDepSat, cfg.VColSat, cStar+epsilonSat)

	madStandalone := experiments.BuildMADStandalone(cfg, 0)
	heStandalone := experiments.BuildHeStandalone(cfg, 0)

	return sweepRow{
		ConfigID:               cfg.ID,
		VSat:                   cfg.VSat,
		VDepSat:                cfg.VDepSat,
		VColSat:                cfg.VColSat,
		Kappa:                  cfg.Kappa,
		HopsN:                  cfg.HopsN,
		WidthCRABSat:           widthCRAB,
		WidthCRABByzantineSat:  widthCRAB,
		WidthCRABPrime1_25Sat:  widthCRABPrime125,
		WidthCRABPrime1_50Sat:  widthCRABPrime150,
		WidthCRABPrime2_00Sat:  widthCRABPrime200,
		CStarSat:               cStar,
		WidthCALIBERCStarMinus:  widthCStarMinus,
		WidthCALIBERCStar:       widthCStar,
		WidthCALIBERCStarPlus:   widthCStarPlus,
		CNStarSat:              experiments.CNStar(cfg.VSat, cfg.VDepSat, cfg.VColSat, cfg.HopsN),
		HeConditionValid:       cfg.HeConditionValid,
		HeConditionReason:      cfg.HeConditionReason,
		MADStandaloneWidthSat:  madStandalone.AttackWidthSat,
		HeStandaloneMarginSat:  -heStandalone.AttackWidthSat,
		ActiveMinerCoverageMAD: madStandalone.Feasible,
		Notes:                  "CALIBER widths recomputed explicitly",
		ElapsedMicros:          time.Since(rowStart).Microseconds(),
		GeneratedAtUTC:         time.Now().UTC().Format(time.RFC3339),
	}
}

func crabWidthWithCollateral(vSat, vDepSat, vColSat, cPrimeSat int64) int64 {
	ub := vSat + cPrimeSat + vDepSat
	lb := cPrimeSat + vColSat
	return ub - lb
}

func buildParallelSwapTable(vSat int64, depRatio float64, colRatio float64) []parallelSwapRow {
	vDep := int64(math.Round(float64(vSat) * depRatio))
	vCol := int64(math.Round(float64(vDep) * colRatio))
	rows := make([]parallelSwapRow, 0, 4)
	for _, n := range []int{1, 3, 5, 7} {
		cN := experiments.CNStar(vSat, vDep, vCol, n)
		rows = append(rows, parallelSwapRow{
			N:           n,
			CNStarSat:   cN,
			OverheadSat: cN - vSat,
		})
	}
	return rows
}

func collectTelemetry() telemetry {
	regtestBlocks := int64(0)
	signetBlocks := int64(0)

	regtestPresent := false
	signetPresent := false

	if m, err := readHeightArtifact(filepath.Join("artifacts", "regtest_txids.json")); err == nil {
		regtestBlocks = m.EndHeight - m.StartHeight
	}
	if m, err := readHeightArtifact(filepath.Join("artifacts", "signet_txids.json")); err == nil {
		signetBlocks = m.EndHeight - m.StartHeight
	}
	if _, err := os.Stat(filepath.Join("artifacts", "linked_acs_regtest.json")); err == nil {
		regtestPresent = true
	}
	if _, err := os.Stat(filepath.Join("artifacts", "linked_acs_signet.json")); err == nil {
		signetPresent = true
	}

	leavesSweep := []int{1, 2, 4, 8}
	nRuns := 1000

	var witnessDists []telemetryDistribution
	var scriptDists []telemetryDistribution

	for _, leaves := range leavesSweep {
		wDist := benchmarkWitnessGeneration(nRuns, leaves)
		sDist := benchmarkScriptValidation(nRuns, leaves)
		witnessDists = append(witnessDists, wDist)
		scriptDists = append(scriptDists, sDist)
	}

	return telemetry{
		RegtestBlocksObserved:           regtestBlocks,
		SignetBlocksObserved:            signetBlocks,
		WitnessGenerationDistributions:  witnessDists,
		ScriptValidationDistributions:   scriptDists,
		LinkedACSRegtestArtifactPresent: regtestPresent,
		LinkedACSSignetArtifactPresent:  signetPresent,
		GeneratedAtUTC:                  time.Now().UTC().Format(time.RFC3339),
	}
}

func benchmarkWitnessGeneration(iter int, leaves int) telemetryDistribution {
	dist := telemetryDistribution{
		Leaves:      leaves,
		TimesMicros: make([]float64, iter),
	}
	for i := 0; i < iter; i++ {
		start := time.Now()
		// Simulate O(log N) overhead for building the MAST witness inclusion proof
		depth := math.Log2(float64(leaves))
		if depth < 0 {
			depth = 0
		}
		const batchSize = 10000
		start = time.Now()
		for k := 0; k < batchSize; k++ {
			// Base generation cost + depth cost
			for j := 0; j < int(depth)+1; j++ {
				pre := sha256.Sum256([]byte(fmt.Sprintf("pre-b-%d-%d", i, j)))
				_ = hex.EncodeToString(pre[:])
			}
		}
		d := time.Since(start)
		dist.TimesMicros[i] = (float64(d.Nanoseconds()) / 1000.0) / float64(batchSize)
	}
	return dist
}

func benchmarkScriptValidation(iter int, leaves int) telemetryDistribution {
	dist := telemetryDistribution{
		Leaves:      leaves,
		TimesMicros: make([]float64, iter),
	}
	secretR := []byte("revocation-secret-fixed")
	hR := sha256.Sum256(secretR)

	for i := 0; i < iter; i++ {
		start := time.Now()
		// Simulate O(log N) cost for MAST script path validation
		depth := math.Log2(float64(leaves))
		if depth < 0 {
			depth = 0
		}
		const batchSize = 10000
		start = time.Now()
		for k := 0; k < batchSize; k++ {
			for j := 0; j < int(depth)+1; j++ {
				cR := sha256.Sum256(secretR)
				if cR != hR {
					panic("script validation mismatch")
				}
			}
		}
		d := time.Since(start)
		dist.TimesMicros[i] = (float64(d.Nanoseconds()) / 1000.0) / float64(batchSize)
	}
	return dist
}

type heightArtifact struct {
	StartHeight int64 `json:"startHeight"`
	EndHeight   int64 `json:"endHeight"`
}

func readHeightArtifact(path string) (heightArtifact, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return heightArtifact{}, err
	}
	var h heightArtifact
	if err := json.Unmarshal(b, &h); err != nil {
		return heightArtifact{}, err
	}
	return h, nil
}

func writeSweepCSV(path string, rows []sweepRow) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	head := []string{
		"config_id", "v_sat", "v_dep_sat", "v_col_sat", "kappa", "n",
		"width_crab_sat", "width_crab_byz_sat", "width_crab_p125_sat",
		"width_crab_p150_sat", "width_crab_p200_sat", "c_star_sat",
		"width_caliber_cstar_minus_eps", "width_caliber_cstar", "width_caliber_cstar_plus_eps",
		"c_n_star_sat", "he_condition_valid", "he_condition_reason",
		"mad_standalone_width_sat", "he_standalone_margin_sat", "elapsed_micros",
	}
	if err := w.Write(head); err != nil {
		return err
	}
	for _, r := range rows {
		rec := []string{
			r.ConfigID,
			fmt.Sprintf("%d", r.VSat),
			fmt.Sprintf("%d", r.VDepSat),
			fmt.Sprintf("%d", r.VColSat),
			fmt.Sprintf("%d", r.Kappa),
			fmt.Sprintf("%d", r.HopsN),
			fmt.Sprintf("%d", r.WidthCRABSat),
			fmt.Sprintf("%d", r.WidthCRABByzantineSat),
			fmt.Sprintf("%d", r.WidthCRABPrime1_25Sat),
			fmt.Sprintf("%d", r.WidthCRABPrime1_50Sat),
			fmt.Sprintf("%d", r.WidthCRABPrime2_00Sat),
			fmt.Sprintf("%d", r.CStarSat),
			fmt.Sprintf("%d", r.WidthCALIBERCStarMinus),
			fmt.Sprintf("%d", r.WidthCALIBERCStar),
			fmt.Sprintf("%d", r.WidthCALIBERCStarPlus),
			fmt.Sprintf("%d", r.CNStarSat),
			fmt.Sprintf("%t", r.HeConditionValid),
			r.HeConditionReason,
			fmt.Sprintf("%d", r.MADStandaloneWidthSat),
			fmt.Sprintf("%d", r.HeStandaloneMarginSat),
			fmt.Sprintf("%d", r.ElapsedMicros),
		}
		if err := w.Write(rec); err != nil {
			return err
		}
	}
	return w.Error()
}

func writeParallelSwapCSV(path string, rows []parallelSwapRow) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	if err := w.Write([]string{"n", "c_n_star_sat", "overhead_sat"}); err != nil {
		return err
	}
	for _, r := range rows {
		if err := w.Write([]string{
			fmt.Sprintf("%d", r.N),
			fmt.Sprintf("%d", r.CNStarSat),
			fmt.Sprintf("%d", r.OverheadSat),
		}); err != nil {
			return err
		}
	}
	return w.Error()
}

func writeAttackTimelineCSV(path string, rows []experiments.AttackSummaryRow) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	if err := w.Write([]string{
		"scheme", "miner_lb_sat", "bob_ub_sat", "width_sat",
		"selected_br_sat", "profitable", "outcome",
	}); err != nil {
		return err
	}
	for _, r := range rows {
		if err := w.Write([]string{
			r.Scheme,
			fmt.Sprintf("%d", r.MinerLBSat),
			fmt.Sprintf("%d", r.BobUBSat),
			fmt.Sprintf("%d", r.WidthSat),
			fmt.Sprintf("%d", r.SelectedBRSat),
			fmt.Sprintf("%t", r.Profitable),
			r.Outcome,
		}); err != nil {
			return err
		}
	}
	return w.Error()
}

func writeKappaWindowCSV(path string, rows []kappaWindowRow) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	if err := w.Write([]string{
		"rho_h", "kappa", "runs", "trials_per_run", "analytical_prob", "simulated_prob_mean", "simulated_prob_std", "abs_diff_pct",
	}); err != nil {
		return err
	}
	for _, r := range rows {
		if err := w.Write([]string{
			fmt.Sprintf("%.2f", r.RhoH),
			fmt.Sprintf("%d", r.Kappa),
			fmt.Sprintf("%d", r.Runs),
			fmt.Sprintf("%d", r.TrialsPerRun),
			fmt.Sprintf("%.6f", r.AnalyticalProb),
			fmt.Sprintf("%.6f", r.SimulatedProbMean),
			fmt.Sprintf("%.6f", r.SimulatedProbStd),
			fmt.Sprintf("%.4f", r.AbsDiffPct),
		}); err != nil {
			return err
		}
	}
	return w.Error()
}

func buildKappaWindowReport(seed int64, runs int, trialsPerRun int) kappaWindowReport {
	rng := rand.New(rand.NewSource(seed))
	rhoHValues := []float64{0.30, 0.40, 0.50}
	kappaValues := []int{3, 5, 7}

	rows := make([]kappaWindowRow, 0, len(rhoHValues)*len(kappaValues))
	for _, rhoH := range rhoHValues {
		for _, kappa := range kappaValues {
			analytical := 1.0 - math.Pow(1.0-rhoH, float64(kappa))
			
			// Collect distribution
			probs := make([]float64, runs)
			sum := 0.0
			for r := 0; r < runs; r++ {
				p := simulateKappaWindow(rhoH, kappa, trialsPerRun, rng)
				probs[r] = p
				sum += p
			}
			mean := sum / float64(runs)
			
			var varianceSum float64
			for _, p := range probs {
				varianceSum += (p - mean) * (p - mean)
			}
			std := math.Sqrt(varianceSum / float64(runs))

			absDiff := math.Abs(mean-analytical) / analytical * 100.0
			
			rows = append(rows, kappaWindowRow{
				RhoH:              rhoH,
				Kappa:             kappa,
				Runs:              runs,
				TrialsPerRun:      trialsPerRun,
				AnalyticalProb:    analytical,
				SimulatedProbMean: mean,
				SimulatedProbStd:  std,
				AbsDiffPct:        absDiff,
			})
		}
	}
	return kappaWindowReport{
		Seed:        seed,
		GeneratedAt: time.Now().UTC().Format(time.RFC3339),
		Rows:        rows,
	}
}

func simulateKappaWindow(rhoH float64, kappa, trials int, rng *rand.Rand) float64 {
	successes := 0
	for i := 0; i < trials; i++ {
		for j := 0; j < kappa; j++ {
			if rng.Float64() < rhoH {
				successes++
				break
			}
		}
	}
	return float64(successes) / float64(trials)
}

func writeJSON(path string, v any) error {
	b, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o644)
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
