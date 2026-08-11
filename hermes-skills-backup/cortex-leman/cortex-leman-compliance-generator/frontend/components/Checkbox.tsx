'use client'

import { InputHTMLAttributes, forwardRef, useState } from 'react'
import { Check } from 'lucide-react'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, checked, onChange, disabled, ...props }, ref) => {
    const [internalChecked, setInternalChecked] = useState(checked || false)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setInternalChecked(e.target.checked)
      if (onChange) {
        onChange(e)
      }
    }

    return (
      <label className="flex items-center space-x-3 cursor-pointer">
        <div className="relative">
          <input
            type="checkbox"
            ref={ref}
            checked={internalChecked}
            onChange={handleChange}
            disabled={disabled}
            className="sr-only"
            {...props}
          />
          <div
            className={`w-5 h-5 border-2 rounded flex items-center justify-center transition-colors ${
              internalChecked
                ? 'bg-primary-600 border-primary-600'
                : 'border-gray-300 hover:border-gray-400'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {internalChecked && <Check className="w-3 h-3 text-white" />}
          </div>
        </div>
        {label && (
          <span className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
            {label}
          </span>
        )}
      </label>
    )
  }
)

Checkbox.displayName = 'Checkbox'

export default Checkbox
