import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Calendar, Clock, Trash2, Edit, Star, TrendingUp } from 'lucide-react'
import { Button, Badge, Card } from '../components/ui'
import { Modal, ConfirmDialog } from '../components/ui/Modal'
import toast from 'react-hot-toast'
import { useScheduleStore } from '../store'

export default function Dashboard() {
  const navigate = useNavigate()
  const { schedules: storedSchedules, updateSchedule, deleteSchedule: removeSchedule } = useScheduleStore()
  
  // Use stored schedules or mock data for development
  const [schedules, setSchedules] = useState(storedSchedules.length > 0 ? storedSchedules : [
    {
      id: 1,
      name: 'Spring 2025 - Preferred',
      createdAt: '2025-01-15T10:30:00',
      fitScore: 92,
      totalCredits: 15,
      courseCount: 4,
      courses: [
        { code: 'CSC 1301', credits: 3, crn: '12345' },
        { code: 'MATH 2211', credits: 4, crn: '23456' },
        { code: 'ENGL 1102', credits: 3, crn: '34567' },
        { code: 'HIST 2110', credits: 3, crn: '45678' },
      ],
    },
    {
      id: 2,
      name: 'Spring 2025 - Backup',
      createdAt: '2025-01-15T11:00:00',
      fitScore: 85,
      totalCredits: 12,
      courseCount: 4,
      courses: [
        { code: 'CSC 1301', credits: 3, crn: '12399' },
        { code: 'MATH 1113', credits: 3, crn: '23488' },
        { code: 'ENGL 1101', credits: 3, crn: '34599' },
        { code: 'PHIL 2010', credits: 3, crn: '45699' },
      ],
    },
    {
      id: 3,
      name: 'Fall 2024 - Completed',
      createdAt: '2024-08-20T14:20:00',
      fitScore: 88,
      totalCredits: 15,
      courseCount: 5,
      courses: [
        { code: 'MATH 1111', credits: 3, crn: '11111' },
        { code: 'ENGL 1101', credits: 3, crn: '22222' },
        { code: 'BIOL 1107', credits: 4, crn: '33333' },
        { code: 'HIST 2110', credits: 3, crn: '44444' },
        { code: 'POLS 1101', credits: 2, crn: '55555' },
      ],
    },
  ])
  
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [scheduleToDelete, setScheduleToDelete] = useState(null)
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [editName, setEditName] = useState('')
  
  const handleDeleteSchedule = (schedule) => {
    setScheduleToDelete(schedule)
    setDeleteDialogOpen(true)
  }
  
  const confirmDelete = () => {
    setSchedules(schedules.filter(s => s.id !== scheduleToDelete.id))
    toast.success('Schedule deleted')
    setScheduleToDelete(null)
  }
  
  const handleRenameSchedule = (schedule) => {
    setEditingSchedule(schedule)
    setEditName(schedule.name)
  }
  
  const saveRename = () => {
    setSchedules(schedules.map(s =>
      s.id === editingSchedule.id ? { ...s, name: editName } : s
    ))
    toast.success('Schedule renamed')
    setEditingSchedule(null)
  }
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }
  
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
              My Schedules
            </h1>
            <p className="text-lg text-gray-600">
              {schedules.length} saved schedule{schedules.length !== 1 ? 's' : ''}
            </p>
          </div>
          
          <Button
            variant="primary"
            size="lg"
            className="mt-4 sm:mt-0"
            onClick={() => navigate('/upload')}
          >
            <Plus className="h-5 w-5 mr-2" />
            Create New Schedule
          </Button>
        </div>
        
        {/* Empty State */}
        {schedules.length === 0 && (
          <div className="card text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-6">
              <Calendar className="h-10 w-10 text-gray-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              No schedules yet
            </h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Create your first schedule by uploading your degree evaluation and setting your preferences
            </p>
            <Button
              variant="primary"
              size="lg"
              onClick={() => navigate('/upload')}
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Schedule
            </Button>
          </div>
        )}
        
        {/* Schedules Grid */}
        {schedules.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {schedules.map((schedule) => (
              <ScheduleCard
                key={schedule.id}
                schedule={schedule}
                onDelete={handleDeleteSchedule}
                onRename={handleRenameSchedule}
                formatDate={formatDate}
              />
            ))}
          </div>
        )}
        
        {/* Delete Confirmation Dialog */}
        <ConfirmDialog
          isOpen={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
          onConfirm={confirmDelete}
          title="Delete Schedule"
          message={`Are you sure you want to delete "${scheduleToDelete?.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="danger"
        />
        
        {/* Rename Modal */}
        <Modal
          isOpen={!!editingSchedule}
          onClose={() => setEditingSchedule(null)}
          title="Rename Schedule"
          size="sm"
        >
          <div className="space-y-6">
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="input w-full"
              placeholder="Schedule name"
              autoFocus
            />
            
            <div className="flex items-center justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setEditingSchedule(null)}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={saveRename}
                disabled={!editName.trim()}
              >
                Save
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  )
}

function ScheduleCard({ schedule, onDelete, onRename, formatDate }) {
  const navigate = useNavigate()
  
  return (
    <Card hover className="border-l-4 border-l-primary-500">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            {schedule.name}
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>{formatDate(schedule.createdAt)}</span>
          </div>
        </div>
        
        {/* Fit Score Badge */}
        <div className="flex items-center space-x-1 bg-gradient-to-br from-primary-600 to-accent-600 text-white px-3 py-1.5 rounded-lg">
          <TrendingUp className="h-4 w-4" />
          <span className="font-bold">{schedule.fitScore}%</span>
        </div>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-sm text-gray-600 mb-1">Total Credits</p>
          <p className="text-2xl font-bold text-gray-900">{schedule.totalCredits}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-sm text-gray-600 mb-1">Courses</p>
          <p className="text-2xl font-bold text-gray-900">{schedule.courseCount}</p>
        </div>
      </div>
      
      {/* Course List */}
      <div className="space-y-2 mb-4">
        <p className="text-sm font-medium text-gray-700">Courses:</p>
        <div className="space-y-1.5">
          {schedule.courses.map((course, index) => (
            <div
              key={index}
              className="flex items-center justify-between text-sm bg-gray-50 px-3 py-2 rounded-lg"
            >
              <span className="font-medium text-gray-900">{course.code}</span>
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">{course.credits} cr</span>
                <Badge variant="gray" className="text-xs">
                  {course.crn}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex items-center space-x-2 pt-4 border-t border-gray-200">
        <Button
          variant="primary"
          className="flex-1"
          onClick={() => navigate('/results')}
        >
          View Details
        </Button>
        <Button
          variant="ghost"
          onClick={() => onRename(schedule)}
          className="p-2.5"
        >
          <Edit className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          onClick={() => onDelete(schedule)}
          className="p-2.5 text-red-600 hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  )
}
