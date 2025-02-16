import { getApi, postApi } from "./api"
import { Action, ActionList, ListState } from "./abs_types"
import { createAction } from "./util"

const LOADING = 'LOADING'
const UPDATE = 'UPDATE'

export interface ListActions<DT, C extends string> extends ActionList {
  LOADING: Action<typeof LOADING, C,  boolean>,
  UPDATE: Action<typeof UPDATE, C, DT[]>
}

function runAction<DT, C extends string, K extends keyof ListActions<DT, C>>(component: C, dispatch: any, type: K, payload: ListActions<DT, C>[K]['payload']): Action<K, C, ListActions<DT, C>[K]['payload']> {
  return dispatch(createAction<ListActions<DT, C>, K>(type, component, payload))
}

export class Collection<DT, C extends string> {
  private api_midpoint: string
  public runAction: <K extends keyof ListActions<DT, C>>(type: K, payload: ListActions<DT, C>[K]['payload']) => Action<K, C, ListActions<DT, C>[K]['payload']>

  constructor(component: C, api_midpoint: string, dispatch: any) {
    this.api_midpoint = api_midpoint
    this.runAction = <K extends keyof ListActions<DT, C>>(type: K, payload: ListActions<DT, C>[K]['payload']) => runAction<DT, C, K>(component, dispatch, type, payload)
  }

  private async apiGet(endpoint: string, data: any = { }): Promise<any> {
    return (await getApi(`${this.api_midpoint}/${endpoint}`, data))
  }

  private async apiPost(endpoint: string, data: DT) {
    return postApi(`${this.api_midpoint}/${endpoint}`, data)
  }

  public async get(params: any = { }) {
    this.runAction(LOADING, true)
    try {
      const res = await this.apiGet('list', params)
      this.runAction(UPDATE, res.data)
    } finally {
      this.runAction(LOADING, false)
    }
  }
}

export const createCollectionReducer = <DT, C extends string, K extends keyof ListActions<DT, C>>(component: C) => (
  state: ListState<DT> = { loading: false, items: [] }, 
  action: Action<keyof ListActions<DT, C>, C, ListActions<DT, C>[K]['payload']>
): ListState<DT> => {
  if (action.component != component) return state
  switch (action.type) {
      case LOADING:
          return { ...state, loading: action.payload }
      case UPDATE:
          return { ...state, items: action.payload }
      default:
          return state
  }   
}