import { useState } from 'react'
import { clsx } from 'clsx'

export function Slider({ label, min, max, value, onChange, formatValue, className }) {
  const percentage = ((value - min) / (max - min)) * 100
  
  return (
    <div className={clsx('space-y-3', className)}>
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
        <span className="text-sm font-semibold text-primary-600">
          {formatValue ? formatValue(value) : value}
        </span>
      </div>
      
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
          style={{
            background: `linear-gradient(to right, rgb(20 184 166) 0%, rgb(20 184 166) ${percentage}%, rgb(229 231 235) ${percentage}%, rgb(229 231 235) 100%)`
          }}
        />
        <div 
          className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-primary-600 rounded-full pointer-events-none shadow-lg"
          style={{ left: `calc(${percentage}% - 10px)` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-gray-500">
        <span>{formatValue ? formatValue(min) : min}</span>
        <span>{formatValue ? formatValue(max) : max}</span>
      </div>
    </div>
  )
}

export function DayChips({ selectedDays, onChange, className }) {
  const days = [
    { value: 'M', label: 'Mon' },
    { value: 'T', label: 'Tue' },
    { value: 'W', label: 'Wed' },
    { value: 'R', label: 'Thu' },
    { value: 'F', label: 'Fri' },
  ]
  
  const toggleDay = (dayValue) => {
    if (selectedDays.includes(dayValue)) {
      onChange(selectedDays.filter(d => d !== dayValue))
    } else {
      onChange([...selectedDays, dayValue])
    }
  }
  
  return (
    <div className={clsx('space-y-2', className)}>
      <label className="block text-sm font-medium text-gray-700">
        Preferred Days
      </label>
      <div className="flex flex-wrap gap-2">
        {days.map((day) => {
          const isSelected = selectedDays.includes(day.value)
          return (
            <button
              key={day.value}
              type="button"
              onClick={() => toggleDay(day.value)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-all duration-150 focus-ring',
                isSelected
                  ? 'bg-primary-600 text-white shadow-md scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {day.label}
            </button>
          )
        })}
      </div>
      {selectedDays.length === 0 && (
        <p className="text-xs text-gray-500">Select at least one day</p>
      )}
    </div>
  )
}

export function TimeRangePicker({ startTime, endTime, onStartChange, onEndChange, className }) {
  const timeOptions = []
  for (let hour = 8; hour <= 21; hour++) {
    const time24 = `${hour.toString().padStart(2, '0')}:00`
    const hour12 = hour > 12 ? hour - 12 : hour
    const period = hour >= 12 ? 'PM' : 'AM'
    const time12Format = `${hour12}:00 ${period}`
    timeOptions.push({ value: time24, label: time12Format })
  }
  
  return (
    <div className={clsx('space-y-3', className)}>
      <label className="block text-sm font-medium text-gray-700">
        Time Range
      </label>
      
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="block text-xs text-gray-600">From</label>
          <select
            value={startTime}
            onChange={(e) => onStartChange(e.target.value)}
            className="input text-sm"
          >
            {timeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="space-y-1.5">
          <label className="block text-xs text-gray-600">To</label>
          <select
            value={endTime}
            onChange={(e) => onEndChange(e.target.value)}
            className="input text-sm"
          >
            {timeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {startTime && endTime && startTime >= endTime && (
        <p className="text-sm text-red-600">End time must be after start time</p>
      )}
    </div>
  )
}

export function RadioGroup({ label, options, value, onChange, className }) {
  return (
    <div className={clsx('space-y-2', className)}>
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="space-y-2">
        {options.map((option) => {
          const isSelected = value === option.value
          return (
            <label
              key={option.value}
              className={clsx(
                'flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all duration-150',
                isSelected
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              )}
            >
              <input
                type="radio"
                value={option.value}
                checked={isSelected}
                onChange={(e) => onChange(e.target.value)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
              />
              <div className="ml-3 flex-1">
                <span className="block text-sm font-medium text-gray-900">
                  {option.label}
                </span>
                {option.description && (
                  <span className="block text-xs text-gray-500 mt-0.5">
                    {option.description}
                  </span>
                )}
              </div>
            </label>
          )
        })}
      </div>
    </div>
  )
}

export function ChipGroup({ label, options, selectedValues, onChange, className }) {
  const toggleValue = (value) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter(v => v !== value))
    } else {
      onChange([...selectedValues, value])
    }
  }
  
  return (
    <div className={clsx('space-y-2', className)}>
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const isSelected = selectedValues.includes(option.value)
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => toggleValue(option.value)}
              className={clsx(
                'px-4 py-2 rounded-full text-sm font-medium transition-all duration-150 focus-ring',
                isSelected
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-primary-300'
              )}
            >
              {option.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
