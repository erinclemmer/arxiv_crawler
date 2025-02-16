import { ListState, ModelState } from "./abs_types"

export type Reference = {
  id: string
  title: string
  arxiv_id: string
  date: string
  dateFmt?: Date
  month?: string
  year?: number
  clean_id: string
  url: string
  author: string
  data: any
}

export type Paper = {
  arxiv_id: string
  clean_id: string
  title: string
  abstract: string
  log: string

  project_name?: string
  references_error: string | undefined
  references: Reference[]
}

export type Project = {
  name: string
  papers: Paper[]
}

export type AppState = {
  projectList: ListState<Project>
  projectModel: ModelState<Project>
  paperModel: ModelState<Paper>
}