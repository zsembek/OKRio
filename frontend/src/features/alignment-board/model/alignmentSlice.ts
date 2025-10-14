import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { Objective } from './types';

export interface AlignmentState {
  objectives: Objective[];
}

const initialState: AlignmentState = {
  objectives: [
    {
      id: 'company-1',
      title: 'Expand enterprise OKR adoption',
      owner: 'CEO',
      progress: 72,
      children: [
        {
          id: 'sales-1',
          title: 'Increase ARR by 25%',
          owner: 'VP Sales',
          progress: 60
        },
        {
          id: 'product-1',
          title: 'Deliver OKR forecasting engine',
          owner: 'CPO',
          progress: 40
        }
      ]
    },
    {
      id: 'company-2',
      title: 'Elevate employee engagement',
      owner: 'CHRO',
      progress: 55,
      children: [
        {
          id: 'people-1',
          title: 'Launch leadership academy',
          owner: 'L&D',
          progress: 30
        }
      ]
    }
  ]
};

interface MoveObjectivePayload {
  objectiveId: string;
  targetParentId: string | null;
}

const findAndRemoveObjective = (objectives: Objective[], objectiveId: string): Objective | null => {
  for (let i = 0; i < objectives.length; i += 1) {
    const objective = objectives[i];
    if (objective.id === objectiveId) {
      objectives.splice(i, 1);
      return objective;
    }
    if (objective.children) {
      const removed = findAndRemoveObjective(objective.children, objectiveId);
      if (removed) {
        return removed;
      }
    }
  }
  return null;
};

const findObjective = (objectives: Objective[], objectiveId: string): Objective | null => {
  for (const objective of objectives) {
    if (objective.id === objectiveId) {
      return objective;
    }
    if (objective.children) {
      const match = findObjective(objective.children, objectiveId);
      if (match) {
        return match;
      }
    }
  }
  return null;
};

const alignmentSlice = createSlice({
  name: 'alignment',
  initialState,
  reducers: {
    moveObjective: (state, action: PayloadAction<MoveObjectivePayload>) => {
      const { objectiveId, targetParentId } = action.payload;
      if (objectiveId === targetParentId) return;

      const moved = findAndRemoveObjective(state.objectives, objectiveId);
      if (!moved) return;

      if (!targetParentId) {
        state.objectives.push(moved);
        return;
      }

      const targetParent = findObjective(state.objectives, targetParentId);
      if (!targetParent) {
        state.objectives.push(moved);
        return;
      }

      targetParent.children = targetParent.children ? [...targetParent.children, moved] : [moved];
    }
  }
});

export const { moveObjective } = alignmentSlice.actions;
export const alignmentReducer = alignmentSlice.reducer;
