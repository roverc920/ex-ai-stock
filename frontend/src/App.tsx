import { BrowserRouter, Routes, Route, useLocation, Navigate } from 'react-router-dom'
import { Home } from './pages/Home'
import { History } from './pages/History'
import { HistoryDetail } from './pages/HistoryDetail'

function Layout() {
  const location = useLocation()
  const activeTab = location.pathname.startsWith('/history') ? 'history' : 'home'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="font-bold text-xl text-blue-600">
              AI股票分析
            </div>
            <div className="flex gap-4">
              <a
                href="/"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'home'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                分析
              </a>
              <a
                href="/history"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  activeTab === 'history'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                历史
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="history" element={<History />} />
        </Route>
        <Route path="/history/:id" element={<HistoryDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
