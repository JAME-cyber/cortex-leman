import { LabelHTMLAttributes, forwardRef } from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {}

const Label = forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, ...props }, ref) => {
    const baseStyles = 'block text-sm font-medium text-gray-700 mb-2'

    const classes = twMerge(clsx(baseStyles, className))

    return (
      <label ref={ref} className={classes} {...props}>
        {children}
      </label>
    )
  }
)

Label.displayName = 'Label'

export default Label
