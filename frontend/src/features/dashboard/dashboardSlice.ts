import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type ObjectiveSummary = {
  id: string;
  name: string;
  progress: number;
  status: "on_track" | "at_risk" | "off_track";
};

export interface DashboardState {
  activePeriod: string;
  objectives: ObjectiveSummary[];
}

const initialState: DashboardState = {
  activePeriod: "Q2 2024",
  objectives: [
    { id: "1", name: "Improve customer retention", progress: 0.35, status: "at_risk" },
    { id: "2", name: "Launch AI-assisted OKR coach", progress: 0.62, status: "on_track" },
    { id: "3", name: "Automate Excel connector rollout", progress: 0.18, status: "off_track" }
  ]
};

const dashboardSlice = createSlice({
  name: "dashboard",
  initialState,
  reducers: {
    setActivePeriod(state, action: PayloadAction<string>) {
      state.activePeriod = action.payload;
    }
  }
});

export const { setActivePeriod } = dashboardSlice.actions;
export const dashboardReducer = dashboardSlice.reducer;
