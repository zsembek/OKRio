import { RootState } from "../../app/store";

export const selectDashboardObjectives = (state: RootState) => state.dashboard.objectives;
export const selectActivePeriod = (state: RootState) => state.dashboard.activePeriod;
