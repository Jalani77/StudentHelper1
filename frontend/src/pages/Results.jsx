import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Star, Clock, MapPin, Users, Copy, CheckCircle, AlertCircle, TrendingUp, Calendar } from 'lucide-react'
import { Button, Badge, Card } from '../components/ui'
import toast from 'react-hot-toast'

export default function Results() {
  const navigate = useNavigate()
  const [copiedCRNs, setCopiedCRNs] = useState(false)
  
  // Mock schedule data
  const schedule = {
    fitScore: 92,
    totalCredits: 15,
    courses: [
      {
        crn: '12345',
        code: 'CSC 1301',
        title: 'Principles of Computer Science I',
        credits: 3,
        section: '001',
        days: 'MWF',
        time: '10:00 AM - 10:50 AM',
        location: 'Classroom South 301',
        campus: 'Atlanta',
        instructor: 'Dr. Sarah Johnson',
        seatsAvailable: 5,
        seatsTotal: 30,
        modality: 'In-Person',
        professorRating: {
          rating: 4.5,
          numRatings: 42,
          difficulty: 3.2,
        },
        matchReasons: [
          'Matches your preferred days (MWF)',
          'Within your time range (9 AM - 5 PM)',
          'Highly rated professor',
        ],
      },
      {
        crn: '23456',
        code: 'MATH 2211',
        title: 'Calculus I',
        credits: 4,
        section: '002',
        days: 'TR',
        time: '2:00 PM - 3:15 PM',
        location: 'Langdale Hall 415',
        campus: 'Atlanta',
        instructor: 'Prof. Michael Chen',
        seatsAvailable: 12,
        seatsTotal: 35,
        modality: 'In-Person',
        professorRating: {
          rating: 4.2,
          numRatings: 38,
          difficulty: 3.8,
        },
        matchReasons: [
          'Within your time range',
          'No schedule conflicts',
        ],
      },
      {
        crn: '34567',
        code: 'ENGL 1102',
        title: 'English Composition II',
        credits: 3,
        section: '003',
        days: 'MW',
        time: '1:00 PM - 2:15 PM',
        location: 'General Classroom Building 205',
        campus: 'Atlanta',
        instructor: 'Dr. Emily Rodriguez',
        seatsAvailable: 8,
        seatsTotal: 25,
        modality: 'Hybrid',
        professorRating: {
          rating: 4.8,
          numRatings: 55,
          difficulty: 2.5,
        },
        matchReasons: [
          'Excellent professor rating (4.8/5)',
          'Hybrid format available',
          'Matches preferred days',
        ],
      },
      {
        crn: '45678',
        code: 'HIST 2110',
        title: 'Survey of United States History I',
        credits: 3,
        section: '001',
        days: 'Online',
        time: 'Asynchronous',
        location: 'Online',
        campus: 'Online',
        instructor: 'Prof. James Thompson',
        seatsAvailable: 25,
        seatsTotal: 50,
        modality: 'Online',
        professorRating: {
          rating: 4.1,
          numRatings: 29,
          difficulty: 2.8,
        },
        matchReasons: [
          'Flexible online format',
          'No schedule conflicts',
        ],
      },
    ],
  }
  
  const allCRNs = schedule.courses.map(c => c.crn).join(', ')
  
  const handleCopyCRNs = () => {
    navigator.clipboard.writeText(allCRNs)
    setCopiedCRNs(true)
    toast.success('CRNs copied to clipboard!')
    setTimeout(() => setCopiedCRNs(false), 3000)
  }
  
  const handleSaveSchedule = () => {
    toast.success('Schedule saved to your dashboard!')
    navigate('/dashboard')
  }
  
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Fit Score */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                Your Recommended Schedule
              </h1>
              <p className="text-lg text-gray-600">
                {schedule.totalCredits} credits • {schedule.courses.length} courses
              </p>
            </div>
            
            <div className="mt-4 lg:mt-0">
              <div className="inline-flex items-center space-x-2 bg-gradient-to-br from-primary-600 to-accent-600 text-white px-6 py-3 rounded-xl">
                <TrendingUp className="h-6 w-6" />
                <div>
                  <p className="text-sm opacity-90">Fit Score</p>
                  <p className="text-3xl font-bold">{schedule.fitScore}%</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-green-900 mb-1">
                  Great match! This schedule meets all your preferences
                </p>
                <p className="text-sm text-green-700">
                  All courses have available seats and match your time/day preferences
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Course Cards */}
          <div className="lg:col-span-2 space-y-4">
            {schedule.courses.map((course) => (
              <CourseCard key={course.crn} course={course} />
            ))}
          </div>
          
          {/* PAWS Registration Panel */}
          <div className="lg:col-span-1">
            <div className="sticky top-6">
              <Card className="border-2 border-primary-200 bg-primary-50/50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                    <Calendar className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">
                    Register in PAWS
                  </h3>
                </div>
                
                {/* CRN List */}
                <div className="bg-white rounded-lg p-4 mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-3">
                    Your CRNs:
                  </p>
                  <div className="space-y-2 mb-4">
                    {schedule.courses.map((course) => (
                      <div key={course.crn} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">{course.code}</span>
                        <span className="font-mono font-semibold text-primary-600">
                          {course.crn}
                        </span>
                      </div>
                    ))}
                  </div>
                  
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handleCopyCRNs}
                  >
                    {copiedCRNs ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-2" />
                        Copy All CRNs
                      </>
                    )}
                  </Button>
                </div>
                
                {/* Instructions */}
                <div className="bg-white rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-900 mb-3">
                    Registration Steps:
                  </p>
                  <ol className="space-y-3 text-sm text-gray-700">
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-5 h-5 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs mr-2 mt-0.5">
                        1
                      </span>
                      <span>Log in to <strong>PAWS</strong></span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-5 h-5 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs mr-2 mt-0.5">
                        2
                      </span>
                      <span>Go to <strong>Student Services → Registration</strong></span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-5 h-5 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs mr-2 mt-0.5">
                        3
                      </span>
                      <span>Click <strong>Add/Drop Classes</strong></span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-5 h-5 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs mr-2 mt-0.5">
                        4
                      </span>
                      <span>Paste all CRNs and click <strong>Submit</strong></span>
                    </li>
                  </ol>
                </div>
                
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-4 w-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-yellow-800">
                      Register quickly! Seats fill up fast during registration periods.
                    </p>
                  </div>
                </div>
              </Card>
              
              <Button
                variant="outline"
                size="lg"
                className="w-full mt-4"
                onClick={handleSaveSchedule}
              >
                Save Schedule
              </Button>
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="mt-8 flex items-center justify-center space-x-4">
          <Button
            variant="outline"
            size="lg"
            onClick={() => navigate('/preferences')}
          >
            ← Adjust Preferences
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => navigate('/dashboard')}
          >
            View All Schedules
          </Button>
        </div>
      </div>
    </div>
  )
}

function CourseCard({ course }) {
  const seatPercentage = (course.seatsAvailable / course.seatsTotal) * 100
  
  return (
    <Card hover className="border-l-4 border-l-primary-500">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4">
        <div className="flex-1 mb-3 sm:mb-0">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-xl font-bold text-gray-900">
              {course.code}
            </h3>
            <Badge variant="primary">CRN: {course.crn}</Badge>
            <Badge variant="gray">{course.section}</Badge>
          </div>
          <p className="text-gray-700 mb-2">{course.title}</p>
          <p className="text-sm text-gray-600">
            {course.credits} credits • {course.instructor}
          </p>
        </div>
        
        {/* Professor Rating */}
        {course.professorRating && (
          <div className="flex items-center space-x-2 bg-yellow-50 px-3 py-2 rounded-lg">
            <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
            <div>
              <p className="text-lg font-bold text-gray-900">
                {course.professorRating.rating}
              </p>
              <p className="text-xs text-gray-600">
                {course.professorRating.numRatings} reviews
              </p>
            </div>
          </div>
        )}
      </div>
      
      {/* Course Details */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div className="flex items-center space-x-2 text-sm text-gray-700">
          <Clock className="h-4 w-4 text-gray-400" />
          <span>
            {course.days === 'Online' ? 'Online' : course.days} • {course.time}
          </span>
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-gray-700">
          <MapPin className="h-4 w-4 text-gray-400" />
          <span>{course.location}</span>
        </div>
        
        <div className="flex items-center space-x-2 text-sm">
          <Users className="h-4 w-4 text-gray-400" />
          <span className={seatPercentage > 30 ? 'text-green-600' : seatPercentage > 10 ? 'text-yellow-600' : 'text-red-600'}>
            {course.seatsAvailable} / {course.seatsTotal} seats
          </span>
        </div>
        
        <div>
          <Badge variant={course.modality === 'Online' ? 'primary' : course.modality === 'Hybrid' ? 'warning' : 'success'}>
            {course.modality}
          </Badge>
        </div>
      </div>
      
      {/* Match Reasons */}
      {course.matchReasons.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-xs font-medium text-green-900 mb-2">
            Why this course:
          </p>
          <ul className="space-y-1">
            {course.matchReasons.map((reason, index) => (
              <li key={index} className="flex items-start space-x-2 text-xs text-green-700">
                <CheckCircle className="h-3 w-3 flex-shrink-0 mt-0.5" />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}
