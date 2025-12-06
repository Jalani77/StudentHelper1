import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sliders as SlidersIcon, Calendar, Clock, MapPin, Monitor } from 'lucide-react'
import { Button } from '../components/ui'
import { Slider, DayChips, TimeRangePicker, RadioGroup, ChipGroup } from '../components/ui/FormControls'
import toast from 'react-hot-toast'
import { apiClient } from '../api/client'
import { useEvalStore, usePreferencesStore, useScheduleStore } from '../store'

export default function Preferences() {
  const navigate = useNavigate()
  const { evalData } = useEvalStore()
  const { preferences: storedPrefs, setPreferences: savePreferences } = usePreferencesStore()
  const { setCurrentSchedule, setLoading } = useScheduleStore()
  const [isLoading, setIsLoading] = useState(false)
  
  const [preferences, setPreferences] = useState(storedPrefs)
  
  const campusOptions = [
    { value: 'atlanta', label: 'Atlanta Campus', description: 'Main downtown campus' },
    { value: 'online', label: 'Fully Online', description: 'Remote learning only' },
    { value: 'any', label: 'Any Campus', description: 'No preference' },
  ]
  
  const modalityOptions = [
    { value: 'in-person', label: 'In-Person' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'online', label: 'Online' },
  ]
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation
    if (preferences.preferredDays.length === 0) {
      toast.error('Please select at least one preferred day')
      return
    }
    
    if (preferences.startTime >= preferences.endTime) {
      toast.error('End time must be after start time')
      return
    }
    
    if (preferences.modalities.length === 0) {
      toast.error('Please select at least one course modality')
      return
    }
    
    setIsLoading(true)
    setLoading(true)
    
    try {
      // Save preferences to store
      savePreferences(preferences)
      
      // Submit to API
      const response = await apiClient.getSchedule(preferences, evalData)
      const schedule = response.data
      
      // Save schedule to store
      setCurrentSchedule(schedule)
      
      toast.success('Schedule generated successfully!')
      navigate('/results')
    } catch (error) {
      console.error('Schedule generation error:', error)
      toast.error('Failed to generate schedule. Using mock data.')
      // Continue to results page with mock data
      navigate('/results')
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Set Your Preferences
          </h1>
          <p className="text-lg text-gray-600">
            Customize your schedule to match your lifestyle
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Credit Hours */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <SlidersIcon className="h-5 w-5 text-primary-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Credit Hours
              </h2>
            </div>
            
            <div className="space-y-6">
              <Slider
                label="Minimum Credits"
                min={3}
                max={18}
                value={preferences.minCredits}
                onChange={(value) => setPreferences({ ...preferences, minCredits: value })}
                formatValue={(value) => `${value} credits`}
              />
              
              <Slider
                label="Maximum Credits"
                min={3}
                max={18}
                value={preferences.maxCredits}
                onChange={(value) => setPreferences({ ...preferences, maxCredits: value })}
                formatValue={(value) => `${value} credits`}
              />
              
              {preferences.minCredits > preferences.maxCredits && (
                <p className="text-sm text-red-600">
                  Minimum credits cannot exceed maximum credits
                </p>
              )}
            </div>
          </div>
          
          {/* Schedule Preferences */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
                <Calendar className="h-5 w-5 text-accent-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Schedule Preferences
              </h2>
            </div>
            
            <div className="space-y-6">
              <DayChips
                selectedDays={preferences.preferredDays}
                onChange={(days) => setPreferences({ ...preferences, preferredDays: days })}
              />
              
              <TimeRangePicker
                startTime={preferences.startTime}
                endTime={preferences.endTime}
                onStartChange={(time) => setPreferences({ ...preferences, startTime: time })}
                onEndChange={(time) => setPreferences({ ...preferences, endTime: time })}
              />
            </div>
          </div>
          
          {/* Campus Location */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <MapPin className="h-5 w-5 text-primary-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Campus Location
              </h2>
            </div>
            
            <RadioGroup
              label=""
              options={campusOptions}
              value={preferences.campus}
              onChange={(value) => setPreferences({ ...preferences, campus: value })}
            />
          </div>
          
          {/* Course Modality */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
                <Monitor className="h-5 w-5 text-accent-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Course Modality
              </h2>
            </div>
            
            <ChipGroup
              label=""
              options={modalityOptions}
              selectedValues={preferences.modalities}
              onChange={(values) => setPreferences({ ...preferences, modalities: values })}
            />
          </div>
          
          {/* Summary */}
          <div className="card bg-primary-50 border-primary-200">
            <h3 className="font-semibold text-gray-900 mb-4">
              Your Schedule Summary
            </h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>
                <span className="font-medium">Credits:</span>{' '}
                {preferences.minCredits} - {preferences.maxCredits} per semester
              </p>
              <p>
                <span className="font-medium">Days:</span>{' '}
                {preferences.preferredDays.length > 0
                  ? preferences.preferredDays.join(', ')
                  : 'No preference'}
              </p>
              <p>
                <span className="font-medium">Time:</span>{' '}
                {preferences.startTime} - {preferences.endTime}
              </p>
              <p>
                <span className="font-medium">Campus:</span>{' '}
                {campusOptions.find(o => o.value === preferences.campus)?.label}
              </p>
              <p>
                <span className="font-medium">Modalities:</span>{' '}
                {preferences.modalities.map(m =>
                  modalityOptions.find(o => o.value === m)?.label
                ).join(', ')}
              </p>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-4">
            <Button
              type="button"
              variant="outline"
              size="lg"
              className="flex-1"
              onClick={() => navigate('/upload')}
            >
              ← Back
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="flex-1"
              disabled={isLoading}
            >
              {isLoading ? 'Generating...' : 'Generate Schedule →'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
