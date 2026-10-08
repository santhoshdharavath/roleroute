export type SkillDefinition = {
  id: string;
  name: string;
  weight: number;
};

export type SkillCoverage = {
  id: string;
  name: string;
  weight: number;
  mastery: number;
  status: string;
};

export type TopicOut = {
  id: number;
  module_id: number;
  title: string;
  description: string;
  skill_tags: string[];
  estimated_minutes: number;
  order_index: number;
  completed: boolean;
  completed_at: string | null;
};

export type ModuleOut = {
  id: number;
  role_id: number;
  title: string;
  description: string;
  order_index: number;
  topics: TopicOut[];
  completed_count: number;
  total_count: number;
};

export type Role = {
  id: number;
  name: string;
  description: string;
  required_skills: SkillDefinition[];
  role_goal_threshold: number;
};

export type RolePathOut = {
  role: Role;
  modules: ModuleOut[];
  next_topic: TopicOut | null;
};

export type OnboardingRequest = {
  role_id: number;
  target_date: string;
  name?: string;
};

export type OnboardingResponse = {
  user_id: number;
  name: string;
  selected_role_id: number;
  target_date: string;
};

export type SnapshotOut = {
  readiness_score: number;
  recorded_at: string;
};

export type ProgressSummaryOut = {
  user_id: number;
  selected_role: Role | null;
  target_date: string | null;
  completed_count: number;
  total_count: number;
  readiness_score: number;
  stage: string;
  skill_coverage: SkillCoverage[];
  skill_gaps: SkillCoverage[];
  next_topic: TopicOut | null;
  module_progress: ModuleOut[];
  graph_history: SnapshotOut[];
  demo_mode: boolean;
};

export type PredictionsOut = {
  readiness_score: number;
  stage: string;
  role_goal_threshold: number;
  skill_coverage: SkillCoverage[];
  skill_gaps: SkillCoverage[];
  next_topic: TopicOut | null;
  next_topic_improves: string[];
  goal_status: string;
  goal_explanation: string;
  suggested_actions: string[];
  disclaimer: string;
  demo_mode: boolean;
};

export type HealthStatus = {
  status: string;
  app: string;
  demo_mode: boolean;
  llm_configured: boolean;
};
