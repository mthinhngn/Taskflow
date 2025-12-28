import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'

interface Task {
  id: number
  title: string
  status: string
  due_at: string | null
  priority: number
  ai_score: number | null
}

interface Project {
  id: number
  name: string
}

function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userRes, projectsRes, tasksRes] = await Promise.all([
          apiClient.get('/auth/me'),
          apiClient.get('/projects'),
          apiClient.get('/tasks?limit=10'),
        ])

        setUser(userRes.data)
        setProjects(projectsRes.data)
        setTasks(tasksRes.data.items)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">TaskFlow</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {user?.email}</span>
            <button
              onClick={handleLogout}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Sidebar */}
          <div className="md:col-span-1">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Projects</h3>
                {projects.length === 0 ? (
                  <p className="text-sm text-gray-500">No projects yet</p>
                ) : (
                  <ul className="space-y-2">
                    {projects.map((project) => (
                      <li
                        key={project.id}
                        className="text-sm text-blue-600 hover:text-blue-700 cursor-pointer"
                      >
                        {project.name}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>

          {/* Tasks */}
          <div className="md:col-span-2">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Tasks</h3>
                {tasks.length === 0 ? (
                  <p className="text-sm text-gray-500">No tasks yet. Create one to get started!</p>
                ) : (
                  <div className="space-y-4">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium text-gray-900">{task.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              Status: <span className="font-medium">{task.status}</span>
                            </p>
                            {task.ai_score !== null && (
                              <p className="text-sm text-gray-600">
                                AI Score: <span className="font-medium">{(task.ai_score * 100).toFixed(0)}%</span>
                              </p>
                            )}
                          </div>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Priority {task.priority}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
