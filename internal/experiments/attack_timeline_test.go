package experiments

import "testing"

func TestAttackTimelineMatchesAnalyticalProfile(t *testing.T) {
	rep := BuildAttackTimelineReport()

	if rep.Profile.CALIBERCStarSat != rep.Profile.VSat+rep.Profile.VDepSat {
		t.Fatalf("c_star mismatch: got %d", rep.Profile.CALIBERCStarSat)
	}
	if got := rep.Baseline.WidthSat; got != rep.Profile.VSat+rep.Profile.VDepSat-rep.Profile.VColSat {
		t.Fatalf("baseline width mismatch: got %d", got)
	}
	if !rep.Baseline.Profitable {
		t.Fatalf("baseline CLBA should be profitable")
	}
	if rep.CALIBER.WidthSat != 0 {
		t.Fatalf("CALIBER width should be zero at c_star, got %d", rep.CALIBER.WidthSat)
	}
	if rep.CALIBER.Profitable {
		t.Fatalf("CALIBER CLBA should be infeasible at c_star")
	}
}
