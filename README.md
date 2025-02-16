# Arxiv Crawler

A full-stack application (server + client) for managing collections of arXiv papers. This project provides a **Flask-based REST API** for storing and retrieving papers in named “projects,” along with a **React client** that allows users to view, create, and manage these projects and their associated papers in a user-friendly interface.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Server Setup](#server-setup)
  - [Prerequisites](#prerequisites)
  - [Installation & Usage](#installation--usage)
- [Client Setup](#client-setup)
  - [Prerequisites](#prerequisites-1)
  - [Installation & Usage](#installation--usage-1)
- [API Endpoints](#api-endpoints)
  - [Projects](#projects)
  - [Papers](#papers)
- [Client Routing](#client-routing)
- [Development and Contributing](#development-and-contributing)
- [License](#license)

---

## Features

- **Server**: 
  - Create and list projects.
  - Add or remove arXiv papers from a project.
  - Retrieve a project’s details (its name and associated paper IDs).
  - Retrieve paper metadata from arXiv by ID and refresh it on demand.

- **Client**:
  - A React-based frontend to display a list of projects, show project details, and show individual paper information.
  - Easy navigation with React Router to navigate between the homepage (all projects), project details, and individual paper pages.

---

## Project Structure

A common directory layout might look like this:

```
arxiv-crawler/
│
├── server/
│   ├── app.py
│   ├── paper.py
│   ├── project.py
│   └── ... (other Python files)
│
├── client/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── Papers/
│   │   │   └── show.tsx
│   │   ├── Projects/
│   │   │   ├── list.tsx
│   │   │   └── show.tsx
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

You can adjust the structure to your preference as long as the server and client are set up to run independently.

---

## Server Setup

### Prerequisites

- Python 3.7+  
- [Flask](https://flask.palletsprojects.com/) and [Flask-CORS](https://flask-cors.readthedocs.io/) packages  
- A folder named `projects/` in the server directory to store project JSON files.

### Installation & Usage

1. **Navigate** to the `server/` directory (or wherever your server code is located).

2. **Create & activate** a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *(On Windows, use `venv\Scripts\activate`)*

3. **Install** dependencies:
   ```bash
   pip install flask flask-cors
   ```
   *(Add any additional Python packages you need.)*

4. **Create** a `projects/` directory if it doesn’t already exist:
   ```bash
   mkdir projects
   ```

5. **Run** the server:
   ```bash
   python app.py
   ```
   The Flask app will start by default on `http://0.0.0.0:4000`.

---

## Client Setup

### Prerequisites

- [Node.js (version 14+)](https://nodejs.org/)
- [npm](https://www.npmjs.com/) or [Yarn](https://yarnpkg.com/)

### Installation & Usage

1. **Navigate** to the `client/` directory (or wherever your React app is located).

2. **Install** the client dependencies:
   ```bash
   npm install
   ```
   or
   ```bash
   yarn
   ```
3. **Run** the client in development mode:
   ```bash
   npm start
   ```
   or
   ```bash
   yarn start
   ```
   By default, this will start a development server at `http://localhost:3000`.

4. **Open** your browser to [http://localhost:3000](http://localhost:3000). You’ll see the React application’s home page.

---

## API Endpoints

These endpoints (hosted by the Flask server) form the backend for the client application.

### Projects

- `GET /api/project/list`: Retrieves all projects.
- `POST /api/project/create`: Creates a new project.
  - **Request body**: `{ "name": "ProjectName" }`
- `GET /api/project/get?id=ProjectName`: Retrieves a project by name.

### Papers

- `POST /api/paper/create`: Adds a paper to a project.
  - **Request body**: `{ "arxiv_id": "...", "project_name": "..." }`
- `POST /api/paper/delete`: Removes a paper from a project.
- `GET /api/paper/get?id=ArxivID`: Retrieves a paper’s details (insert a dot in the ID if missing).
- `POST /api/paper/get-url`: Placeholder for retrieving a paper’s URL (not fully implemented).
- `POST /api/paper/reload`: Refreshes paper metadata from arXiv.

---

## Client Routing

The React frontend (in `client/src/App.tsx`) defines routes using **React Router**:

- **`"/"` (Home)**  
  Renders `ProjectList`, which displays all projects retrieved from the `/api/project/list` endpoint.

- **`"/projects/show/:name"`**  
  Renders `ProjectShow`, which fetches a project by its `name` parameter and displays its details (paper IDs, etc.).

- **`"/papers/show/:id"`**  
  Renders `PaperShow`, which fetches paper details by its arXiv `id`.

**Example** flow:
1. Navigate to [http://localhost:3000](http://localhost:3000) to see the list of projects.
2. Click on a project to see its details (`ProjectShow`).
3. Click on an individual paper ID to see that paper’s metadata (`PaperShow`).
