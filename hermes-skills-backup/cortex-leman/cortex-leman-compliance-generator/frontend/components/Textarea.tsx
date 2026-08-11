import { TextareaHTMLAttributes, forwardRef } from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, rows = 4, ...props }, ref) => {
    const baseStyles = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 resize-none'

    const classes = twMerge(clsx(baseStyles, className))

    return (
      <textarea
        ref={ref}
        className={classes}
        rows={rows}
        {...props}
      />
    )
  }
)

Textarea.displayName = 'Textarea'

export default Textarea
