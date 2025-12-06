import { Link } from 'react-router-dom'
import { Upload, Sliders, Calendar, CheckCircle, Star, Clock, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-accent-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight animate-fade-in">
              Smart Course Selection for{' '}
              <span className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                GSU Students
              </span>
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto animate-slide-up">
              Upload your degree eval, set your preferences, and let AI find the perfect schedule with 
              live professor ratings and real-time course availability.
            </p>
            
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '100ms' }}>
              <Link to="/signup" className="btn-primary btn-lg w-full sm:w-auto">
                Get Started Free
              </Link>
              <button className="btn-outline btn-lg w-full sm:w-auto">
                Watch Demo
              </button>
            </div>
            
            <p className="mt-6 text-sm text-gray-500">
              No credit card required • 2-minute setup
            </p>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-200/30 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent-200/30 rounded-full blur-3xl -z-10" />
      </section>
      
      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Three Simple Steps
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              From degree requirements to registered courses in minutes
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="relative">
              <div className="card text-center hover:shadow-xl transition-shadow duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl mb-6">
                  <Upload className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  1. Upload Your Eval
                </h3>
                <p className="text-gray-600">
                  Drag and drop your degree evaluation from PAWS. We'll extract all your requirements automatically.
                </p>
              </div>
              {/* Connector */}
              <div className="hidden md:block absolute top-1/3 -right-4 w-8 h-0.5 bg-gradient-to-r from-primary-300 to-accent-300" />
            </div>
            
            {/* Step 2 */}
            <div className="relative">
              <div className="card text-center hover:shadow-xl transition-shadow duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-accent-600 to-accent-700 rounded-2xl mb-6">
                  <Sliders className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  2. Set Preferences
                </h3>
                <p className="text-gray-600">
                  Choose your credit hours, preferred days, time ranges, and campus location with an intuitive interface.
                </p>
              </div>
              {/* Connector */}
              <div className="hidden md:block absolute top-1/3 -right-4 w-8 h-0.5 bg-gradient-to-r from-accent-300 to-primary-300" />
            </div>
            
            {/* Step 3 */}
            <div className="card text-center hover:shadow-xl transition-shadow duration-200">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-700 rounded-2xl mb-6">
                <Calendar className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                3. Get Your Schedule
              </h3>
              <p className="text-gray-600">
                Copy your CRNs and paste directly into PAWS. Register for all classes with a single click.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Everything You Need
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Powered by real-time data and AI matching
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Star className="h-6 w-6" />}
              title="Live Professor Ratings"
              description="RateMyProfessors integration shows quality ratings for every course option"
            />
            <FeatureCard
              icon={<TrendingUp className="h-6 w-6" />}
              title="Smart Matching"
              description="AI ranks schedules by fit score based on your exact preferences"
            />
            <FeatureCard
              icon={<Clock className="h-6 w-6" />}
              title="Real-Time Availability"
              description="Live seat counts from PAWS so you never waste time on full classes"
            />
            <FeatureCard
              icon={<CheckCircle className="h-6 w-6" />}
              title="Degree Requirements"
              description="Automatically matches courses to your eval requirements"
            />
            <FeatureCard
              icon={<Calendar className="h-6 w-6" />}
              title="Conflict Detection"
              description="Prevents scheduling conflicts and finds alternative sections"
            />
            <FeatureCard
              icon={<Upload className="h-6 w-6" />}
              title="One-Click Registration"
              description="Copy all CRNs at once and paste into PAWS for instant registration"
            />
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary-600 to-accent-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Build Your Perfect Schedule?
          </h2>
          <p className="text-xl text-primary-50 mb-10 max-w-2xl mx-auto">
            Join thousands of GSU students who have simplified their course selection
          </p>
          <Link 
            to="/signup" 
            className="inline-block bg-white text-primary-600 px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl transition-all duration-200 hover:scale-105"
          >
            Get Started Free
          </Link>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="card-hover">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-primary-600">
          {icon}
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">
            {title}
          </h3>
          <p className="text-sm text-gray-600">
            {description}
          </p>
        </div>
      </div>
    </div>
  )
}
