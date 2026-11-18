export interface FollowUpTask {
  id: string;
  beneficiary_id: string;
  beneficiary_name?: string;
  visit_id?: string;
  task_type: string;
  title: string;
  description?: string;
  due_date: string;
  priority: 'EMERGENCY' | 'HIGH' | 'NORMAL';
  status: 'PENDING' | 'COMPLETED' | 'ESCALATED';
  completed_at?: string;
  created_at?: string;
}
