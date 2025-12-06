import { SkeletonLoader } from './ui'

export function ScheduleCardSkeleton() {
  return (
    <div className="card border-l-4 border-l-gray-300 animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <SkeletonLoader className="h-6 w-32 mb-2" />
          <SkeletonLoader className="h-4 w-64 mb-2" />
          <SkeletonLoader className="h-3 w-48" />
        </div>
        <SkeletonLoader className="h-10 w-16 rounded-lg" />
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <SkeletonLoader className="h-4 w-full" />
        <SkeletonLoader className="h-4 w-full" />
        <SkeletonLoader className="h-4 w-full" />
        <SkeletonLoader className="h-4 w-full" />
      </div>
      
      <SkeletonLoader className="h-20 w-full rounded-lg" />
    </div>
  )
}

export function CourseCardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="flex items-center space-x-2 mb-4">
        <SkeletonLoader className="h-6 w-24" />
        <SkeletonLoader className="h-5 w-20 rounded-full" />
      </div>
      <SkeletonLoader className="h-4 w-full mb-2" />
      <SkeletonLoader className="h-3 w-48 mb-4" />
      
      <div className="grid grid-cols-2 gap-3 mb-4">
        <SkeletonLoader className="h-4 w-full" />
        <SkeletonLoader className="h-4 w-full" />
      </div>
      
      <SkeletonLoader className="h-16 w-full rounded-lg" />
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {[1, 2, 3, 4].map((i) => (
        <SkeletonLoader key={i} className="h-64 rounded-2xl" />
      ))}
    </div>
  )
}

export function PreferencesSkeleton() {
  return (
    <div className="space-y-6">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="card">
          <SkeletonLoader className="h-6 w-48 mb-4" />
          <SkeletonLoader className="h-12 w-full mb-2" />
          <SkeletonLoader className="h-12 w-full" />
        </div>
      ))}
    </div>
  )
}
