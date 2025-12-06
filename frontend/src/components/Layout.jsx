import { Outlet, Link, useLocation } from 'react-router-dom'
import { GraduationCap, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Layout() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const isLanding = location.pathname === '/'
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link 
              to="/" 
              className="flex items-center space-x-2 group transition-transform duration-200 hover:scale-105"
            >
              <div className="bg-gradient-to-br from-primary-600 to-accent-600 p-2 rounded-xl">
                <GraduationCap className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                Yiri<span className="text-primary-600">Ai</span>
              </span>
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {!isLanding && (
                <>
                  <NavLink to="/dashboard">My Schedules</NavLink>
                  <NavLink to="/upload">New Schedule</NavLink>
                </>
              )}
              <NavLink to="/" className="text-gray-600 hover:text-gray-900">
                How it Works
              </NavLink>
              {isLanding ? (
                <>
                  <Link 
                    to="/signin" 
                    className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium rounded-lg transition-colors duration-150"
                  >
                    Sign In
                  </Link>
                  <Link 
                    to="/signup" 
                    className="btn-primary ml-2"
                  >
                    Get Started
                  </Link>
                </>
              ) : (
                <button className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium rounded-lg transition-colors duration-150">
                  Sign Out
                </button>
              )}
            </div>
            
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors duration-150"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white animate-slide-down">
            <div className="px-4 py-4 space-y-2">
              {!isLanding && (
                <>
                  <MobileNavLink to="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    My Schedules
                  </MobileNavLink>
                  <MobileNavLink to="/upload" onClick={() => setMobileMenuOpen(false)}>
                    New Schedule
                  </MobileNavLink>
                </>
              )}
              <MobileNavLink to="/" onClick={() => setMobileMenuOpen(false)}>
                How it Works
              </MobileNavLink>
              {isLanding ? (
                <div className="pt-4 space-y-2">
                  <Link 
                    to="/signin" 
                    onClick={() => setMobileMenuOpen(false)}
                    className="block w-full text-center px-4 py-2.5 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition-colors duration-150"
                  >
                    Sign In
                  </Link>
                  <Link 
                    to="/signup" 
                    onClick={() => setMobileMenuOpen(false)}
                    className="block w-full text-center btn-primary"
                  >
                    Get Started
                  </Link>
                </div>
              ) : (
                <button className="block w-full text-left px-4 py-2.5 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition-colors duration-150">
                  Sign Out
                </button>
              )}
            </div>
          </div>
        )}
      </nav>
      
      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* About */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-gradient-to-br from-primary-600 to-accent-600 p-2 rounded-xl">
                  <GraduationCap className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold text-gray-900">
                  Yiri<span className="text-primary-600">Ai</span>
                </span>
              </div>
              <p className="text-sm text-gray-600 max-w-md">
                Smart course selection for GSU students. Find the perfect schedule with live professor ratings, 
                real-time availability, and intelligent matching.
              </p>
              <p className="text-xs text-gray-500 mt-4">
                Built with ❤️ for GSU students | v2.0
              </p>
            </div>
            
            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                Product
              </h3>
              <ul className="space-y-2">
                <FooterLink to="/">How it Works</FooterLink>
                <FooterLink to="/upload">Get Started</FooterLink>
                <FooterLink to="/dashboard">My Schedules</FooterLink>
              </ul>
            </div>
            
            {/* Support */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
                Support
              </h3>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors duration-150">Help Center</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors duration-150">Privacy Policy</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors duration-150">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 text-center">
              © 2025 YiriAi. Educational tool for course selection only. 
              <span className="block sm:inline sm:ml-1">Students must manually register through PAWS.</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function NavLink({ to, children, className = '' }) {
  const location = useLocation()
  const isActive = location.pathname === to
  
  return (
    <Link
      to={to}
      className={`px-4 py-2 font-medium rounded-lg transition-colors duration-150 ${
        isActive 
          ? 'text-primary-600 bg-primary-50' 
          : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
      } ${className}`}
    >
      {children}
    </Link>
  )
}

function MobileNavLink({ to, children, onClick }) {
  const location = useLocation()
  const isActive = location.pathname === to
  
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`block px-4 py-2.5 font-medium rounded-lg transition-colors duration-150 ${
        isActive 
          ? 'text-primary-600 bg-primary-50' 
          : 'text-gray-700 hover:bg-gray-50'
      }`}
    >
      {children}
    </Link>
  )
}

function FooterLink({ to, children }) {
  return (
    <li>
      <Link 
        to={to} 
        className="text-sm text-gray-600 hover:text-primary-600 transition-colors duration-150"
      >
        {children}
      </Link>
    </li>
  )
}
