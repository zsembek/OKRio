export interface Objective {
  id: string;
  title: string;
  owner: string;
  progress: number;
  children?: Objective[];
}
