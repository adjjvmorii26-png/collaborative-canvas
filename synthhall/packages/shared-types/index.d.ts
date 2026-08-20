/** SynthHall domain model — source of truth for the spec. */

export type AgentProvider = 'copilot' | 'openai' | 'local' | 'custom';
export type AgentRole = 'builder' | 'critic' | 'storyteller' | 'analyst';
export type ArenaType = 'debate' | 'design' | 'story';
export type ParticipantRole = 'owner' | 'member' | 'guest';
export type BindingMode = 'observer' | 'speaker' | 'tool';

export interface User {
  id: string;
  email: string;
  displayName: string;
}

export interface Agent {
  id: string;
  ownerUserId: string;
  name: string;
  provider: AgentProvider;
  role: AgentRole;
  config: Record<string, unknown>;
}

export interface ArenaConfig {
  type: ArenaType;
  topic: string;
  rules: string[];
}

export interface Room {
  id: string;
  name: string;
  createdByUserId: string;
  isPublic: boolean;
  arena?: ArenaConfig;
}

export interface RoomParticipant {
  roomId: string;
  userId: string;
  role: ParticipantRole;
}

export interface RoomAgentBinding {
  roomId: string;
  agentId: string;
  mode: BindingMode;
}

export interface Message {
  id: string;
  roomId: string;
  authorType: 'user' | 'agent';
  authorId: string;
  authorName: string;
  content: string;
  createdAt: string;
}
