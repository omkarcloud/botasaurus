import { EuiButtonGroup } from  '@elastic/eui/optimize/es/components/button/button_group/button_group' ;
import React from 'react';

type ChooseOption = {
  value: string
  label: string
}

type ChooseProps = {
  color?: string
  options: ChooseOption[]
  title?: any
  disabled?: boolean
  value: string // Currently selected value
  onChange: (value: string) => void // Function to call when the selection changes
  name?: string
  isRequired?: boolean
}

const ChooseField: React.FC<ChooseProps> = ({
  options,
  value,
  onChange,
  title,
  disabled,
  name,
  color,
  isRequired
}) => {
  // Prepare options for EuiButtonGroupn
  const buttonOptions = options.map(option => ({
    id: option.value, // Use the option's value as the unique id
    label: option.label.toString(),
  }))

  const handleChange = (optionId: string) => {
    if (isRequired) {
      const newValue = value === optionId ? optionId : optionId // Toggle selection
      onChange(newValue) // Call the provided onChange function with the new value or null
    } else {
      const newValue = value === optionId ? null : optionId // Toggle selection
      // @ts-ignore
      onChange(newValue) // Call the provided onChange function with the new value or null
    }
  }



  return (
    <EuiButtonGroup
      title={title}
      isDisabled={disabled}
      legend="Select an option" // Provide a descriptive legend
      color={color === undefined ? 'primary' : undefined}
      type="multi" // Multi-selection button group
      id={name}
      options={buttonOptions}
      onChange={handleChange}
      idToSelectedMap={value !== null ? { [value]: true } : {}}
    />
  )
}

export default ChooseField
