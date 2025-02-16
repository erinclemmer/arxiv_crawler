import { getApi, postApi } from "./api"
import { Action, ActionList, ModelState } from "./abs_types"
import { createAction } from "./util"

const LOADING = 'LOADING'
const UPDATE = 'UPDATE'

export interface ModelActions<DT, C extends string> extends ActionList {
  LOADING: Action<typeof LOADING, C,  boolean>,
  UPDATE: Action<typeof UPDATE, C, DT>
}

function runAction<DT, C extends string, K extends keyof ModelActions<DT, C>>(component: C, dispatch: any, type: K, payload: ModelActions<DT, C>[K]['payload']): Action<K, C, ModelActions<DT, C>[K]['payload']> {
  return dispatch(createAction<ModelActions<DT, C>, K>(type, component, payload))
}

export class Model<DT, C extends string> {
  private api_midpoint: string
  public runAction: <K extends keyof ModelActions<DT, C>>(type: K, payload: ModelActions<DT, C>[K]['payload']) => Action<K, C, ModelActions<DT, C>[K]['payload']>

  constructor(component: C, api_midpoint: string, dispatch: any) {
    this.api_midpoint = api_midpoint
    this.runAction = <K extends keyof ModelActions<DT, C>>(type: K, payload: ModelActions<DT, C>[K]['payload']) => runAction<DT, C, K>(component, dispatch, type, payload)
  }

  public async apiGet(endpoint: string, data: any = { }): Promise<any> {
    return (await getApi(`${this.api_midpoint}/${endpoint}`, data))
  }

  public async apiPost(endpoint: string, data: any) {
    return postApi(`${this.api_midpoint}/${endpoint}`, data)
  }

  public async get(id: any, cb: (() => void) | null = null): Promise<DT> {
    this.runAction(LOADING, true)
    let model = null
    try {
      model = (await this.apiGet('get', { id })).data as DT
      this.runAction(UPDATE, model)
    } finally {
      this.runAction(LOADING, false)
      if (cb != null) cb()
    }
    return model
  }

  public async create(data: DT): Promise<DT | null> {
    this.runAction(LOADING, true)
    let model = null
    try {
      const res = await this.apiPost('create', data)
      if (!res || res.status != 200) {
        console.error('ERROR: creating failed: ' + res.data)
        return null
      }
      model = res.data
    } finally {
      this.runAction(LOADING, false)
    }
    return model as DT
  }

  public async edit(data: DT): Promise<boolean> {
    this.runAction(LOADING, true)
    let ret = false
    try {
      const res = await this.apiPost('edit', data)
      if (!res) {
        console.error('ERROR: creating tune failed')
        return false
      }
      ret = res.data
    } finally {
      this.runAction(LOADING, false)
    }
    return ret
  }

  public async remove(model: DT) {
    this.runAction(LOADING, true)
    try {
      const res = await this.apiPost('delete', model)
      if (!!res.data.error) {
        console.error(res.data.errror)
        return
      }
    } finally {
      this.runAction(LOADING, false)
    }
  }
}

export const createModelReducer = <DT, C extends string, K extends keyof ModelActions<DT, C>>(component: C) => (
  state: ModelState<DT> = { loading: false, model: null }, 
  action: Action<keyof ModelActions<DT, C>, C, ModelActions<DT, C>[K]['payload']>
): ModelState<DT> => {
  if (action.component != component) return state
  switch (action.type) {
      case LOADING:
          return { ...state, loading: action.payload }
      case UPDATE:
          return { ...state, model: action.payload }
      default:
          return state
  }   
}