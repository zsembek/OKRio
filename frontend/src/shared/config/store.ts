import { configureStore } from '@reduxjs/toolkit';
import { alignmentReducer } from '../../features/alignment-board/model/alignmentSlice';

export const store = configureStore({
  reducer: {
    alignment: alignmentReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
