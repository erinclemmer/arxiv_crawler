import { Action, ActionList } from "./types"

export function createAction<T extends ActionList, K extends keyof T>(action: K, component: string, payload: T[K]['payload']): Action<K, T[K]['component'], T[K]['payload']> {
  return {
    type: action,
    component,
    payload
  }
}