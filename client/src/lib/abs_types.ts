export type ListState<DT> = {
    loading: boolean
    items: DT[]
}

export type ModelState<DT> = {
    loading: boolean
    model: DT | null
}


export interface Action<T, C, P> {
    type: T,
    component: C,
    payload: P
}

export type ActionList = {
    [K: string]: Action<string, string, any>
}